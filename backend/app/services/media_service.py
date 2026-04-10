import os
import cv2
import tempfile
from typing import List, Dict, Any, Optional
from moviepy.editor import VideoFileClip
from fastapi import UploadFile
from PIL import Image
import io
from .ai_service import ai_service
from ..core.config import settings

class MediaService:
    async def save_temp_file(self, upload_file: UploadFile) -> str:
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await upload_file.read())
            return tmp.name

    async def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        try:
            audio_path = f"{video_path}.mp3"
            clip = VideoFileClip(video_path)
            # Truncate to 30 seconds to stay within free tier limits
            if clip.duration > 30:
                clip = clip.subclip(0, 30)
            
            if clip.audio is not None:
                clip.audio.write_audiofile(audio_path, logger=None)
                clip.close()
                return audio_path
            clip.close()
            return None
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    async def extract_frames(self, video_path: str, interval_seconds: int = 5) -> List[bytes]:
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0: fps = 24
            
            frame_count = 0
            while cap.isOpened() and len(frames) < 5: # Limit to 5 frames for free tier
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % (int(fps) * interval_seconds) == 0:
                    # Convert to bytes
                    _, buffer = cv2.imencode('.jpg', frame)
                    frames.append(buffer.tobytes())
                
                frame_count += 1
            cap.release()
        except Exception as e:
            print(f"Error extracting frames: {e}")
        return frames

    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        if not os.path.exists(audio_path):
            return {"error": "Audio file not found"}
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
            
        result = await ai_service.query_hf_model(
            settings.MODEL_AUDIO,
            {"inputs": audio_data}
        )
        return result

media_service = MediaService()
