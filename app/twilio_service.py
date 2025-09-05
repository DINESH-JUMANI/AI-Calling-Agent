from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import httpx
from typing import Dict, Optional

from app.config import settings

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    
    def create_twiml_response(self, text: str, voice_id: str = None) -> str:
        """Create TwiML response with text-to-speech"""
        response = VoiceResponse()
        
        if voice_id:
            # Use ElevenLabs for custom voice
            audio_url = self.generate_audio_url(text, voice_id)
            response.play(audio_url)
        else:
            # Use Twilio's default TTS
            response.say(text, voice='alice', language='en-US')
        
        # Add gather for user input
        gather = response.gather(
            input='speech',
            action='/call/process-speech',
            method='POST',
            speech_timeout=3,
            timeout=10
        )
        
        return str(response)
    
    def generate_audio_url(self, text: str, voice_id: str) -> str:
        """Generate audio using ElevenLabs and return URL"""
        # This would integrate with your audio generation service
        # For now, return a placeholder
        return f"/audio/{voice_id}/{hash(text)}"