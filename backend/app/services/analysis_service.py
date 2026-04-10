from typing import List, Dict, Any
from .ai_service import ai_service
from ..core.config import settings
from ..db.mongodb import get_database

class AnalysisService:
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        # Limit text length for free API tier
        truncated_text = text[:1000]
        
        # 1. Get Sentiment
        sentiment_task = ai_service.query_hf_model(
            settings.MODEL_SENTIMENT,
            {"inputs": truncated_text}
        )
        
        # 2. Get Emotion
        emotion_task = ai_service.query_hf_model(
            settings.MODEL_EMOTION,
            {"inputs": truncated_text}
        )
        
        # Resolve results
        sentiment_res = await sentiment_task
        emotion_res = await emotion_task
        
        return {
            "sentiment": sentiment_res,
            "emotion": emotion_res
        }

    async def analyze_image(self, ocr_text: str, visual_emotion: Any) -> Dict[str, Any]:
        # 1. Analyze the OCR text (Sentinent/Emotion)
        text_analysis = await self.analyze_text(ocr_text) if ocr_text.strip() else {"sentiment": {}, "emotion": {}}
        
        return {
            "text_analysis": text_analysis,
            "visual_emotion": visual_emotion
        }

    async def analyze_audio(self, transcription: str) -> Dict[str, Any]:
        # Reuse text analysis logic for the transcription
        return await self.analyze_text(transcription)

    async def analyze_video(self, transcription: str, visual_emotions: List[Any]) -> Dict[str, Any]:
        # 1. Analyze transcribed speech
        speech_analysis = await self.analyze_text(transcription) if transcription.strip() else {}
        
        return {
            "speech_analysis": speech_analysis,
            "visual_timeline": visual_emotions
        }

    async def save_analysis(self, result_data: Dict[str, Any]) -> Any:
        db = get_database()
        result = await db.analyses.insert_one(result_data)
        return await db.analyses.find_one({"_id": result.inserted_id})

    def generate_suggestions(self, sentiment: List[Any], emotion: List[Any]) -> List[str]:
        # Basic logic to generate suggestions based on top emotion/sentiment
        suggestions = []
        
        # This is a placeholder for more complex logic or another AI call
        # For now, we'll suggest reflection if negative, and celebration if positive
        score = 0
        if isinstance(sentiment, list) and len(sentiment) > 0:
            # Roberta sentiment returns [[{'label': 'positive', 'score': 0.9}, ...]]
            top_s = sentiment[0][0] if isinstance(sentiment[0], list) else sentiment[0]
            if top_s.get('label') == 'positive':
                suggestions.append("Keep up the positive energy!")
            elif top_s.get('label') == 'negative':
                suggestions.append("Take a moment to breathe and reflect on these feelings.")
        
        return suggestions

analysis_service = AnalysisService()
