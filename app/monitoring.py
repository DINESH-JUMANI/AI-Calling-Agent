from fastapi import APIRouter
from app.database import SessionLocal
from app.database import Client, CallLog
import psutil
import os

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/system/health")
async def system_health():
    """Get system health metrics"""
    # Database health
    db = SessionLocal()
    try:
        client_count = db.query(Client).count()
        db_healthy = True
    except:
        db_healthy = False
        client_count = 0
    finally:
        db.close()
    
    # System metrics
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": {
            "connected": db_healthy,
            "total_clients": client_count
        },
        "system": {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "processes": len(psutil.pids())
        }
    }

@router.get("/metrics/calls")
async def call_metrics():
    """Get call metrics across all clients"""
    db = SessionLocal()
    try:
        total_calls = db.query(CallLog).count()
        appointments_booked = db.query(CallLog).filter(CallLog.appointment_booked == True).count()
        
        return {
            "total_calls": total_calls,
            "appointments_booked": appointments_booked,
            "conversion_rate": (appointments_booked / total_calls * 100) if total_calls > 0 else 0
        }
    finally:
        db.close()