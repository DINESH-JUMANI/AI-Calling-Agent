import datetime
from typing import Dict, List, Optional
import json
import re

from app.appointment_service import AppointmentService
from app.llm_service import LLMService

class CallHandler:
    def __init__(self):
        self.llm_service = LLMService()
        self.appointment_service = AppointmentService()
        self.conversations = {}  # In production, use Redis
    
    def get_conversation_history(self, call_sid: str) -> List[Dict]:
        """Get conversation history for a call"""
        return self.conversations.get(call_sid, [])
    
    def add_to_conversation(self, call_sid: str, role: str, content: str):
        """Add message to conversation history"""
        if call_sid not in self.conversations:
            self.conversations[call_sid] = []
        
        self.conversations[call_sid].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def process_call(self, client_data: Dict, user_input: str, call_sid: str) -> Dict:
        """Process call and generate response"""
        # Add user input to conversation
        self.add_to_conversation(call_sid, "user", user_input)
        
        # Get conversation history
        history = self.get_conversation_history(call_sid)
        
        # Generate AI response
        ai_response = self.llm_service.generate_response(
            client_data, 
            user_input, 
            history
        )
        
        # Check if response contains appointment booking request
        appointment_data = None
        if "BOOK_APPOINTMENT:" in ai_response:
            try:
                appointment_json = ai_response.split("BOOK_APPOINTMENT:")[1].strip()
                appointment_data = json.loads(appointment_json)
                
                # Book appointment
                booking_result = await self.appointment_service.book_appointment(
                    client_data, 
                    appointment_data
                )
                
                if booking_result["success"]:
                    ai_response = "Perfect! I've booked your appointment. You'll receive a confirmation shortly. Is there anything else I can help you with?"
                else:
                    ai_response = "I apologize, but I'm having trouble booking your appointment right now. Let me have someone call you back to confirm the details."
            
            except Exception as e:
                ai_response = "I'd be happy to help you book an appointment. Let me have someone call you back to confirm the details."
        
        # Add AI response to conversation
        self.add_to_conversation(call_sid, "assistant", ai_response)
        
        return {
            "response": ai_response,
            "appointment_booked": appointment_data is not None,
            "appointment_data": appointment_data
        }