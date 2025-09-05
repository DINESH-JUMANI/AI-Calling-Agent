import requests
import json
from typing import Dict, List

class ClientSetup:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
    
    def create_client(self, client_data: Dict) -> Dict:
        """Create a new client"""
        response = requests.post(f"{self.api_base_url}/clients", json=client_data)
        return response.json()
    
    def upload_knowledge_file(self, client_id: str, file_path: str) -> Dict:
        """Upload knowledge file for client"""
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(
                f"{self.api_base_url}/clients/{client_id}/knowledge/upload",
                files=files
            )
        return response.json()
    
    def add_text_knowledge(self, client_id: str, content: str, source: str = None) -> Dict:
        """Add text knowledge for client"""
        data = {'content': content}
        if source:
            data['source'] = source
        
        response = requests.post(
            f"{self.api_base_url}/clients/{client_id}/knowledge/text",
            data=data
        )
        return response.json()

# Example usage:
if __name__ == "__main__":
    setup = ClientSetup()
    
    # Example client data
    client_data = {
        "name": "John Doe",
        "business_name": "Doe's Dental Clinic",
        "phone_number": "+1234567890",
        "email": "john@doesdental.com",
        "industry": "Healthcare",
        "business_hours": {
            "monday": {"open": "09:00", "close": "17:00"},
            "tuesday": {"open": "09:00", "close": "17:00"},
            "wednesday": {"open": "09:00", "close": "17:00"},
            "thursday": {"open": "09:00", "close": "17:00"},
            "friday": {"open": "09:00", "close": "15:00"}
        },
        "services": "General dentistry, teeth cleaning, dental implants, cosmetic dentistry",
        "faqs": "Q: Do you accept insurance? A: Yes, we accept most major insurance plans.\nQ: How often should I visit? A: We recommend visits every 6 months.",
        "appointment_webhook_url": "https://your-n8n-instance.com/webhook/appointments"
    }
    
    # Create client
    client = setup.create_client(client_data)
    print(f"Client created: {client}")