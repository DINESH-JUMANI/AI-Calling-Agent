import datetime
import httpx
import json
from typing import Dict, Optional

from app.config import settings

class AppointmentService:
    def __init__(self):
        self.n8n_base_url = settings.n8n_base_url
    
    async def book_appointment(self, client_data: Dict, appointment_data: Dict) -> Dict:
        """Book appointment via N8N webhook"""
        if not client_data.get('appointment_webhook_url'):
            return {"success": False, "message": "No appointment webhook configured"}
        
        webhook_url = client_data['appointment_webhook_url']
        
        payload = {
            "business_name": client_data['business_name'],
            "client_phone": client_data['phone_number'],
            "appointment": appointment_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "message": f"Webhook failed: {response.status_code}"}
        
        except Exception as e:
            return {"success": False, "message": f"Error booking appointment: {str(e)}"}
