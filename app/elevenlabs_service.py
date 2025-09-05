from typing import Dict, List
from app.config import settings
from elevenlabs.client import ElevenLabs
import io

class ElevenLabsService:
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    def generate_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
        """Generate speech audio from text"""
        try:
            audio = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_monolingual_v1",
                text=text
            )
            # Convert generator response into bytes
            audio_bytes = b"".join(audio)
            return audio_bytes
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

    def get_available_voices(self) -> List[Dict]:
        """Get available ElevenLabs voices"""
        try:
            voices = self.client.voices.get_all()
            return [{"id": v.voice_id, "name": v.name} for v in voices.voices]
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
