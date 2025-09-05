from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    business_name: str
    phone_number: str
    email: str
    industry: Optional[str] = None
    business_hours: Optional[Dict] = None
    services: Optional[str] = None
    faqs: Optional[str] = None
    appointment_webhook_url: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    client_id: str
    name: str
    business_name: str
    phone_number: str
    email: str
    industry: Optional[str]
    business_hours: Optional[Dict]
    services: Optional[str]
    faqs: Optional[str]
    appointment_webhook_url: Optional[str]
    voice_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class KnowledgeUpload(BaseModel):
    client_id: str
    content: str
    source: Optional[str] = None

class CallRequest(BaseModel):
    From: str
    To: str
    CallSid: str

class AppointmentRequest(BaseModel):
    client_name: str
    phone_number: str
    preferred_date: str
    preferred_time: str
    service_type: Optional[str] = None
    notes: Optional[str] = None