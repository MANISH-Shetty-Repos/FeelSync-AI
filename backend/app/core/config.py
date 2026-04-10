import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "FeelSync AI"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "feelsync_db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Hugging Face
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    MODEL_SENTIMENT: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    MODEL_EMOTION: str = "bhadresh-savani/bert-base-uncased-emotion"
    MODEL_OCR_HANDWRITTEN: str = "microsoft/trocr-base-handwritten"
    MODEL_VISUAL_EMOTION: str = "dima806/facial_emotions_image_detection"
    MODEL_AUDIO: str = "openai/whisper-large-v3"
    MODEL_CHAT: str = "HuggingFaceH4/zephyr-7b-beta"
    
    class Config:
        case_sensitive = True

settings = Settings()
