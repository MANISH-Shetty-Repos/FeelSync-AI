import httpx
from typing import Any, Dict, List, Union
from ..core.config import settings

class AIService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}

    async def query_hf_model(self, model_id: str, payload: Dict[str, Any]) -> Any:
        # Check if token is present
        if not settings.HF_API_TOKEN:
            return {"error": "Hugging Face API Token not configured in .env"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}{model_id}",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            
            # If model is loading, wait and retry? Or just return status
            if response.status_code == 503:
                return {"error": "Model is currently loading on Hugging Face. Please try again in 30 seconds."}
            
            if response.status_code != 200:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                return {"error": f"HF API Error ({response.status_code})", "details": error_detail}
            
            return response.json()

ai_service = AIService()
