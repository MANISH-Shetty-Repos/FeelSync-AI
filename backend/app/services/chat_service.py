from typing import List, Dict, Any
from .ai_service import ai_service
from .history_service import history_service
from ..core.config import settings

class ChatService:
    async def get_chat_response(self, user_id: str, user_message: str) -> str:
        # 1. Fetch context (Last 5 analyses as per Option A)
        history = await history_service.get_user_history(user_id, limit=5)
        
        # 2. Build the context string
        context_data = []
        for h in history:
            sentiment = h.get("sentiment", {}).get("label", "unknown")
            # Extract predominant emotion
            emotions = h.get("emotion", {})
            # Handle different structures for text vs image/video
            top_emotion = "unknown"
            if isinstance(emotions, list) and len(emotions) > 0:
                top_emotion = emotions[0].get("label", "unknown")
            elif isinstance(emotions, dict):
                # Search for nested visual/speech emotion if available
                top_emotion = str(emotions) # fallback
            
            context_data.append(f"- {h['input_type']} input: {sentiment} mood, primary emotion: {top_emotion}")

        context_str = "\n".join(context_data) if context_data else "No history yet."
        
        # 3. Create prompt
        prompt = f"""<|system|>
You are FeelSync AI, an empathetic emotional intelligence assistant. 
Use the following emotional history of the user to provide insights and answer their questions.
Recent History:
{context_str}
</s>
<|user|>
{user_message}</s>
<|assistant|>"""

        # 4. Query LLM
        response = await ai_service.query_hf_model(
            settings.MODEL_CHAT,
            {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 250, "temperature": 0.7}
            }
        )
        
        # Extract generated text from Zephyr response format
        if isinstance(response, list) and len(response) > 0:
            full_text = response[0].get("generated_text", "")
            # Zephyr usually returns prompt + response, so we split
            if "<|assistant|>" in full_text:
                return full_text.split("<|assistant|>")[-1].strip()
            return full_text
        
        return "I'm having trouble connecting to my reasoning engine right now. Please try again in a moment."

chat_service = ChatService()
