from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Any, List
from ....models.analysis import AnalysisResult, TextAnalysisRequest
from ....services.analysis_service import analysis_service
from ....services.text_service import text_service
from ..deps import get_current_user
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
