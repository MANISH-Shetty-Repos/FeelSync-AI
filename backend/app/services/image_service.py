import io
import pytesseract
from PIL import Image
from fastapi import UploadFile
from typing import Optional, Dict, Any
from .ai_service import ai_service
from ..core.config import settings

class ImageService:
    async def extract_text_ocr(self, file: UploadFile) -> str:
        # 1. Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # 2. Attempt AI OCR first (Hugging Face)
        # Reseting file pointer for subsequent reads if needed
        await file.seek(0)
        
        # Note: HF OCR models often take the binary directly or a URL
        # For simplicity in this free tier, we'll try the handwritten model if requested
        # But we'll mostly rely on Tesseract as a fast local fallback
        
        # 3. Local Tesseract Fallback
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            text = f"[OCR Error: {str(e)}]"
            
        return text

    async def analyze_image_emotion(self, file: UploadFile) -> Any:
        # Reset file for reading
        await file.seek(0)
        image_data = await file.read()
        
        # Query HF Visual Emotion model
        # Base64 or binary depending on model; most HF models take binary
        result = await ai_service.query_hf_model(
            settings.MODEL_VISUAL_EMOTION,
            {"inputs": image_data}
        )
        return result

image_service = ImageService()
