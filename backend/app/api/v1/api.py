from fastapi import APIRouter
from .endpoints import auth, analyze, history, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
