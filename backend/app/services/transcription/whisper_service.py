import openai
from typing import List, Dict, Optional
import tempfile
import os
from datetime import datetime, timezone
import httpx
from app.core.config import settings

class WhisperService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def transcribe_audio(
        self,
        audio_file_url: str,
        session_id: str,
        enable_timestamps: bool = True,
        language: str = "ja"
    ) -> Dict:
        """
        Transcribe audio using OpenAI Whisper API
        """
        try:
            # Download audio file from S3
            audio_data = self._download_audio_file(audio_file_url)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Call Whisper API
                with open(temp_file_path, 'rb') as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        language=language
                    )
                
                # Process response
                transcription_result = {
                    "session_id": session_id,
                    "full_text": response.text,
                    "language": response.language,
                    "duration": response.duration if hasattr(response, 'duration') else None,
                    "segments": []
                }
                
                # Process segments with timestamps
                if hasattr(response, 'segments') and response.segments:
                    for i, segment in enumerate(response.segments):
                        transcription_result["segments"].append({
                            "id": i,
                            "start": getattr(segment, 'start', 0),
                            "end": getattr(segment, 'end', 0),
                            "text": getattr(segment, 'text', '').strip(),
                            "speaker": None  # Will be filled by speaker diarization
                        })
                else:
                    # If no segments available, create a single segment with full text
                    transcription_result["segments"].append({
                        "id": 0,
                        "start": 0,
                        "end": transcription_result.get("duration", 0) or 0,
                        "text": response.text.strip(),
                        "speaker": None
                    })
                
                return transcription_result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def _download_audio_file(self, audio_url: str) -> bytes:
        """
        Download audio file from S3 URL
        """
        try:
            with httpx.Client(timeout=300.0) as client:  # 5 minutes timeout
                response = client.get(audio_url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            raise Exception(f"Failed to download audio file: {str(e)}")

    def estimate_processing_time(self, file_size_mb: float) -> int:
        """
        Estimate processing time in seconds based on file size
        """
        # Rough estimate: 1MB = 30 seconds processing time
        return int(file_size_mb * 30)

whisper_service = WhisperService()