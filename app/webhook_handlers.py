from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import httpx
import json
from typing import Dict

from app.database import Client, get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/n8n/appointment-status/{client_id}")
async def handle_appointment_status(
    client_id: str,
    status_data: Dict,
    db: Session = Depends(get_db)
):
    """Handle appointment status updates from N8N"""
    
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Log the appointment status update
    appointment_log = {
        "client_id": client_id,
        "status": status_data.get("status"),
        "appointment_id": status_data.get("appointment_id"),
        "details": status_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # In production, store this in a dedicated table
    print(f"Appointment status update: {appointment_log}")
    
    return {"message": "Status updated successfully"}