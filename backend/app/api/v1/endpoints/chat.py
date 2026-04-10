from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any
from ....services.chat_service import chat_service
from ...deps import get_current_user
from ....models.user import UserOut

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Chat with the AI assistant about your emotional history.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    response_text = await chat_service.get_chat_response(
        str(current_user["_id"]), 
        request.message
    )
    return {"response": response_text}
