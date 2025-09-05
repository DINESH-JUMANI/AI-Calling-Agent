from fastapi import APIRouter, Depends, HTTPException
from httpx import Client
from sqlalchemy.orm import Session
from typing import List, Dict

from app.database import CallLog, get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/clients/{client_id}/overview")
async def get_client_overview(client_id: str, db: Session = Depends(get_db)):
    """Get client dashboard overview"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get statistics
    total_calls = db.query(CallLog).filter(CallLog.client_id == client_id).count()
    appointments_booked = db.query(CallLog).filter(
        CallLog.client_id == client_id,
        CallLog.appointment_booked == True
    ).count()
    
    # Get recent activity
    recent_calls = db.query(CallLog).filter(
        CallLog.client_id == client_id
    ).order_by(CallLog.created_at.desc()).limit(5).all()
    
    return {
        "client_info": {
            "business_name": client.business_name,
            "phone_number": client.phone_number,
            "is_active": client.is_active
        },
        "statistics": {
            "total_calls": total_calls,
            "appointments_booked": appointments_booked,
            "conversion_rate": (appointments_booked / total_calls * 100) if total_calls > 0 else 0
        },
        "recent_activity": [
            {
                "caller_phone": call.caller_phone,
                "appointment_booked": call.appointment_booked,
                "created_at": call.created_at
            }
            for call in recent_calls
        ]
    }
