from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .user import PyObjectId
from bson import ObjectId

class AnalysisResult(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    input_type: str  # text, image, audio, video
    content: str  # The extracted text or description
    sentiment: Any
    emotion: Any
    suggestions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TextAnalysisRequest(BaseModel):
    text: Optional[str] = None
