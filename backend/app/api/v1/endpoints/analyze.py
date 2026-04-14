import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Any, List
from ....models.analysis import AnalysisResult, TextAnalysisRequest
from ....services.analysis_service import analysis_service
from ....services.text_service import text_service
from ....services.image_service import image_service
from ....services.media_service import media_service
from ....services.history_service import history_service
from ...deps import get_current_user
from ....models.user import UserOut

router = APIRouter()

@router.post("/text", response_model=AnalysisResult)
async def analyze_text_input(
    request: TextAnalysisRequest,
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    if not request.text:
        raise HTTPException(status_code=400, detail="Text input is required")
    
    # 1. Perform AI analysis
    analysis_data = await analysis_service.analyze_text(request.text)
    
    # Check for AI errors
    if isinstance(analysis_data.get("sentiment"), dict) and "error" in analysis_data["sentiment"]:
        raise HTTPException(status_code=503, detail=analysis_data["sentiment"]["error"])

    # 2. Generate suggestions
    suggestions = analysis_service.generate_suggestions(
        analysis_data["sentiment"], 
        analysis_data["emotion"]
    )
    
    # 3. Prepare result for DB
    result_to_save = {
        "user_id": str(current_user["_id"]),
        "input_type": "text",
        "content": request.text,
        "sentiment": analysis_data["sentiment"],
        "emotion": analysis_data["emotion"],
        "suggestions": suggestions
    }
    
    # 4. Save to MongoDB
    saved_result = await analysis_service.save_analysis(result_to_save)
    return saved_result

@router.post("/file", response_model=AnalysisResult)
async def analyze_file_input(
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    # 1. Extract text
    try:
        text = await text_service.extract_text_from_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file")
    
    # 2. Perform AI analysis
    analysis_data = await analysis_service.analyze_text(text)
    
    # Check for AI errors
    if isinstance(analysis_data.get("sentiment"), dict) and "error" in analysis_data["sentiment"]:
        raise HTTPException(status_code=503, detail=analysis_data["sentiment"]["error"])

    # 3. Generate suggestions
    suggestions = analysis_service.generate_suggestions(
        analysis_data["sentiment"], 
        analysis_data["emotion"]
    )
    
    # 4. Prepare result for DB
    result_to_save = {
        "user_id": str(current_user["_id"]),
        "input_type": "file",
        "content": text[:2000],  # Store snippet if long
        "sentiment": analysis_data["sentiment"],
        "emotion": analysis_data["emotion"],
        "suggestions": suggestions
    }
    
    # 5. Save to MongoDB
    saved_result = await analysis_service.save_analysis(result_to_save)
    return saved_result

@router.post("/image", response_model=AnalysisResult)
async def analyze_image_input(
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    # 1. Extract text via OCR (Tesseract fallback)
    ocr_text = await image_service.extract_text_ocr(file)
    
    # 2. Analyze visual emotion
    visual_emotion = await image_service.analyze_image_emotion(file)
    
    # 3. Coordinate multimodal analysis
    analysis_data = await analysis_service.analyze_image(ocr_text, visual_emotion)
    
    # 4. Generate suggestions based on both text and visual cues
    # Combining text analysis scores if available
    text_sent = analysis_data["text_analysis"].get("sentiment", [])
    text_emot = analysis_data["text_analysis"].get("emotion", [])
    suggestions = analysis_service.generate_suggestions(text_sent, text_emot)
    
    # 5. Prepare result for DB
    result_to_save = {
        "user_id": str(current_user["_id"]),
        "input_type": "image",
        "content": ocr_text[:1000] if ocr_text else "Visual image analysis",
        "sentiment": analysis_data["text_analysis"].get("sentiment", {}),
        "emotion": {
            "text_emotion": analysis_data["text_analysis"].get("emotion", {}),
            "visual_emotion": visual_emotion
        },
        "suggestions": suggestions
    }
    
    # 6. Save to MongoDB
    saved_result = await analysis_service.save_analysis(result_to_save)
    return saved_result

@router.post("/audio", response_model=AnalysisResult)
async def analyze_audio_input(
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    # 1. Save temp file for processing
    temp_path = await media_service.save_temp_file(file)
    
    try:
        # 2. Transcribe
        transcription_res = await media_service.transcribe_audio(temp_path)
        
        if isinstance(transcription_res, dict) and "error" in transcription_res:
            raise HTTPException(status_code=503, detail=transcription_res["error"])
            
        text = transcription_res.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio: No speech detected")
        
        # 3. Analyze text
        analysis_data = await analysis_service.analyze_audio(text)
        
        # Check for AI errors
        if isinstance(analysis_data, dict) and "error" in analysis_data:
            raise HTTPException(status_code=503, detail=analysis_data["error"])

        # 4. Generate suggestions
        suggestions = analysis_service.generate_suggestions(
            analysis_data.get("sentiment", []),
            analysis_data.get("emotion", [])
        )
        
        # 5. Prepare results
        result_to_save = {
            "user_id": str(current_user["_id"]),
            "input_type": "audio",
            "content": text,
            "sentiment": analysis_data.get("sentiment", {}),
            "emotion": analysis_data.get("emotion", {}),
            "suggestions": suggestions
        }
        
        # 6. Save
        return await analysis_service.save_analysis(result_to_save)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/video", response_model=AnalysisResult)
async def analyze_video_input(
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    # 1. Save temp file
    temp_path = await media_service.save_temp_file(file)
    audio_path = None
    
    try:
        # 2. Extract Audio & Transcribe
        audio_path = await media_service.extract_audio_from_video(temp_path)
        transcription = ""
        if audio_path:
            trans_res = await media_service.transcribe_audio(audio_path)
            transcription = trans_res.get("text", "")
        
        # 3. Extract Frames & Visual Emotion
        frames = await media_service.extract_frames(temp_path)
        visual_emotions = []
        for frame_bytes in frames:
            # Create a mock upload file form bytes for the logic
            # Actually we can just query the model with bytes directly
            from ....services.ai_service import ai_service
            from ....core.config import settings
            v_emot = await ai_service.query_hf_model(settings.MODEL_VISUAL_EMOTION, frame_bytes)
            visual_emotions.append(v_emot)
        
        # 4. Multimodal Coordination
        analysis_data = await analysis_service.analyze_video(transcription, visual_emotions)
        
        # 5. Suggestions
        suggestions = analysis_service.generate_suggestions(
            analysis_data["speech_analysis"].get("sentiment", []),
            analysis_data["speech_analysis"].get("emotion", [])
        )
        
        # 6. Save
        result_to_save = {
            "user_id": str(current_user["_id"]),
            "input_type": "video",
            "content": transcription or "Visual video analysis",
            "sentiment": analysis_data["speech_analysis"].get("sentiment", {}),
            "emotion": {
                "speech_emotion": analysis_data["speech_analysis"].get("emotion", {}),
                "visual_timeline": visual_emotions
            },
            "suggestions": suggestions
        }
        
        return await analysis_service.save_analysis(result_to_save)
        
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)
        if audio_path and os.path.exists(audio_path): os.remove(audio_path)
