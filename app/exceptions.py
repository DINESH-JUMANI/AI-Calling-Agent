from fastapi import HTTPException
from typing import Dict, Any

class AICallAssistantException(Exception):
    """Base exception for AI Call Assistant"""
    pass

class ClientNotFoundError(AICallAssistantException):
    """Raised when client is not found"""
    pass

class VoiceGenerationError(AICallAssistantException):
    """Raised when voice generation fails"""
    pass

class AppointmentBookingError(AICallAssistantException):
    """Raised when appointment booking fails"""
    pass

def create_error_response(status_code: int, detail: str, error_code: str = None) -> HTTPException:
    """Create standardized error response"""
    error_dict = {"detail": detail}
    if error_code:
        error_dict["error_code"] = error_code
    
    return HTTPException(status_code=status_code, detail=error_dict)