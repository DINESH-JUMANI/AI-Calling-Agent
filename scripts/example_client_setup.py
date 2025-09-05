import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

def setup_example_client():
    """Set up an example dental clinic client"""
    
    # 1. Create client
    client_data = {
        "name": "Dr. Sarah Johnson",
        "business_name": "SmileCare Dental Clinic",
        "phone_number": "+1555123456",
        "email": "sarah@smilecare.com",
        "industry": "Healthcare - Dental",
        "business_hours": {
            "monday": {"open": "08:00", "close": "18:00"},
            "tuesday": {"open": "08:00", "close": "18:00"},
            "wednesday": {"open": "08:00", "close": "18:00"},
            "thursday": {"open": "08:00", "close": "18:00"},
            "friday": {"open": "08:00", "close": "16:00"},
            "saturday": {"open": "09:00", "close": "14:00"}
        },
        "services": "General dentistry, teeth cleaning, dental implants, cosmetic dentistry, orthodontics, emergency dental care",
        "faqs": """
        Q: Do you accept insurance?
        A: Yes, we accept most major dental insurance plans including Delta Dental, MetLife, and Cigna.
        
        Q: How often should I visit the dentist?
        A: We recommend regular checkups and cleanings every 6 months.
        
        Q: Do you offer emergency dental services?
        A: Yes, we provide emergency dental care. Please call us immediately for urgent issues.
        
        Q: What payment methods do you accept?
        A: We accept cash, credit cards, dental insurance, and offer payment plans.
        
        Q: How long does a typical cleaning take?
        A: A routine cleaning usually takes 45 minutes to 1 hour.
        
        Q: Do you see children?
        A: Yes, we provide dental care for patients of all ages, including children.
        """,
        "appointment_webhook_url": "https://your-n8n-instance.com/webhook/smilecare-appointments"
    }
    
    response = requests.post(f"{API_BASE}/clients", json=client_data)
    client = response.json()
    client_id = client['client_id']
    
    print(f"Created client: {client['business_name']} (ID: {client_id})")
    
    # 2. Add additional knowledge
    additional_knowledge = """
    About SmileCare Dental Clinic:
    
    Our Services:
    - Routine Checkups and Cleanings: Comprehensive oral health examinations
    - Fillings and Restorations: Using tooth-colored composite materials
    - Crowns and Bridges: Custom-made to restore damaged teeth
    - Dental Implants: Permanent tooth replacement solution
    - Cosmetic Dentistry: Teeth whitening, veneers, smile makeovers
    - Orthodontics: Braces and Invisalign treatment
    - Root Canal Therapy: Saving infected or damaged teeth
    - Oral Surgery: Tooth extractions and other surgical procedures
    
    Our Team:
    Dr. Sarah Johnson has over 15 years of experience in general and cosmetic dentistry.
    
    Location and Parking:
    We're located at 123 Main Street, Downtown. Free parking is available in our lot.
    
    Appointment Policies:
    - Please arrive 15 minutes early for your first visit
    - We require 24-hour notice for cancellations
    - Late arrivals may need to be rescheduled
    
    Emergency Contact:
    For dental emergencies outside business hours, call our emergency line at +1555123999.
    """
    
    knowledge_response = requests.post(
        f"{API_BASE}/clients/{client_id}/knowledge/text",
        data={"content": additional_knowledge, "source": "clinic_information"}
    )
    
    print("Added additional knowledge base")
    
    return client_id

if __name__ == "__main__":
    client_id = setup_example_client()
    print(f"Example client setup complete! Client ID: {client_id}")