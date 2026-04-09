import fitz  # PyMuPDF
from typing import Optional
from fastapi import UploadFile

class TextService:
    async def extract_text_from_file(self, file: UploadFile) -> str:
        content_type = file.content_type
        
        if content_type == "text/plain":
            content = await file.read()
            return content.decode("utf-8")
        
        elif content_type == "application/pdf":
            content = await file.read()
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        
        else:
            raise ValueError(f"Unsupported file type: {content_type}")

text_service = TextService()
