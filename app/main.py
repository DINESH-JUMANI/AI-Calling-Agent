from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import Response
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from typing import List, Optional
import aiofiles
import PyPDF2
import docx
from io import BytesIO
    
from app.call_handler import CallHandler
from app.config import settings
from app.database import Base, CallLog, Client, Knowledge, get_db, engine
from app.elevenlabs_service import ElevenLabsService
from app.llm_service import LLMService
from app.models import ClientCreate, ClientResponse
from app.twilio_service import TwilioService
from app.vector_store import VectorStore

from twilio.twiml.voice_response import VoiceResponse


app = FastAPI(title="AI Call Assistant API", version="1.0.0")

# Initialize services
vector_store = VectorStore()
llm_service = LLMService()
twilio_service = TwilioService()
elevenlabs_service = ElevenLabsService()
call_handler = CallHandler()

# Create database tables
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    print("AI Call Assistant API starting up...")

@app.get("/")
async def root():
    return {"message": "AI Call Assistant API", "status": "running"}

# Client Management Endpoints
@app.post("/clients", response_model=ClientResponse)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    # Check if phone number already exists
    existing_client = db.query(Client).filter(Client.phone_number == client.phone_number).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create new client
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Create vector store collection for client
    vector_store.create_collection_for_client(db_client.client_id)
    
    return db_client

@app.get("/clients", response_model=List[ClientResponse])
async def get_clients(db: Session = Depends(get_db)):
    """Get all clients"""
    return db.query(Client).all()

@app.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, db: Session = Depends(get_db)):
    """Get specific client"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, client_update: ClientCreate, db: Session = Depends(get_db)):
    """Update client information"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    for field, value in client_update.dict(exclude_unset=True).items():
        setattr(client, field, value)
    
    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)
    return client

# Knowledge Management Endpoints
@app.post("/clients/{client_id}/knowledge/text")
async def add_text_knowledge(
    client_id: str, 
    content: str = Form(...), 
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add text knowledge to client's knowledge base"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Add to vector store
    document_ids = vector_store.add_knowledge(client_id, content, source)
    
    # Save to database
    knowledge = Knowledge(
        client_id=client_id,
        content=content,
        source=source or "manual_input",
        embedding_id=",".join(document_ids)
    )
    db.add(knowledge)
    db.commit()
    
    return {"message": "Knowledge added successfully", "document_ids": document_ids}

@app.post("/clients/{client_id}/knowledge/upload")
async def upload_knowledge_file(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process knowledge file (PDF, DOCX, TXT)"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Read file content
    content = await file.read()
    
    # Extract text based on file type
    text_content = ""
    if file.filename.endswith('.pdf'):
        text_content = extract_pdf_text(content)
    elif file.filename.endswith('.docx'):
        text_content = extract_docx_text(content)
    elif file.filename.endswith('.txt'):
        text_content = content.decode('utf-8')
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Add to vector store
    document_ids = vector_store.add_knowledge(client_id, text_content, file.filename)
    
    # Save to database
    knowledge = Knowledge(
        client_id=client_id,
        content=text_content,
        source=file.filename,
        embedding_id=",".join(document_ids)
    )
    db.add(knowledge)
    db.commit()
    
    return {"message": "File processed successfully", "document_ids": document_ids}

def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF"""
    try:
        pdf_file = BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX"""
    try:
        doc = docx.Document(BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX: {str(e)}")

# Call Handling Endpoints
@app.post("/call/incoming")
async def handle_incoming_call(request: Request, db: Session = Depends(get_db)):
    """Handle incoming Twilio call"""
    form_data = await request.form()
    
    to_number = form_data.get("To")
    from_number = form_data.get("From")
    call_sid = form_data.get("CallSid")
    
    # Find client by phone number
    client = db.query(Client).filter(Client.phone_number == to_number).first()
    
    if not client or not client.is_active:
        response = VoiceResponse()
        response.say("I'm sorry, this number is not currently available. Please try again later.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Create call log
    call_log = CallLog(
        client_id=client.client_id,
        caller_phone=from_number,
        call_sid=call_sid,
        conversation=[]
    )
    db.add(call_log)
    db.commit()
    
    # Generate greeting
    greeting = f"Hello! Thank you for calling {client.business_name}. How can I help you today?"
    
    # Create TwiML response
    twiml = twilio_service.create_twiml_response(greeting, client.voice_id)
    
    return Response(content=twiml, media_type="application/xml")

@app.post("/call/process-speech")
async def process_speech(request: Request, db: Session = Depends(get_db)):
    """Process speech input from caller"""
    form_data = await request.form()
    
    speech_result = form_data.get("SpeechResult", "")
    call_sid = form_data.get("CallSid")
    to_number = form_data.get("To")
    
    # Find client
    client = db.query(Client).filter(Client.phone_number == to_number).first()
    if not client:
        response = VoiceResponse()
        response.say("I'm sorry, there was an error. Please try again.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Convert client to dict for processing
    client_data = {
        "client_id": client.client_id,
        "business_name": client.business_name,
        "industry": client.industry,
        "business_hours": client.business_hours,
        "services": client.services,
        "faqs": client.faqs,
        "phone_number": client.phone_number
    }
    
    # Process the call
    result = await call_handler.process_call(client_data, speech_result, call_sid)
    
    # Update call log
    call_log = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
    if call_log:
        conversation = call_log.conversation or []
        conversation.extend([
            {"role": "user", "content": speech_result, "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": result["response"], "timestamp": datetime.utcnow().isoformat()}
        ])
        call_log.conversation = conversation
        if result["appointment_booked"]:
            call_log.appointment_booked = True
        db.commit()
    
    # Generate TwiML response
    twiml = twilio_service.create_twiml_response(result["response"], client.voice_id)
    
    return Response(content=twiml, media_type="application/xml")

# Voice Management Endpoints
@app.get("/voices")
async def get_available_voices():
    """Get available ElevenLabs voices"""
    return elevenlabs_service.get_available_voices()

@app.put("/clients/{client_id}/voice")
async def set_client_voice(client_id: str, voice_id: str = Form(...), db: Session = Depends(get_db)):
    """Set client's preferred voice"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.voice_id = voice_id
    db.commit()
    
    return {"message": "Voice updated successfully"}

# Audio Generation Endpoint
@app.get("/audio/{voice_id}/{text_hash}")
async def get_audio(voice_id: str, text_hash: str):
    """Get generated audio file"""
    # In production, implement caching mechanism
    # For now, return a placeholder response
    return {"message": "Audio generation endpoint - implement caching"}

# Analytics Endpoints
@app.get("/clients/{client_id}/analytics")
async def get_client_analytics(client_id: str, db: Session = Depends(get_db)):
    """Get analytics for a client"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get call statistics
    total_calls = db.query(CallLog).filter(CallLog.client_id == client_id).count()
    appointments_booked = db.query(CallLog).filter(
        CallLog.client_id == client_id,
        CallLog.appointment_booked == True
    ).count()
    
    # Get recent calls
    recent_calls = db.query(CallLog).filter(
        CallLog.client_id == client_id
    ).order_by(CallLog.created_at.desc()).limit(10).all()
    
    return {
        "total_calls": total_calls,
        "appointments_booked": appointments_booked,
        "conversion_rate": (appointments_booked / total_calls * 100) if total_calls > 0 else 0,
        "recent_calls": [
            {
                "caller_phone": call.caller_phone,
                "duration": call.call_duration,
                "appointment_booked": call.appointment_booked,
                "created_at": call.created_at
            }
            for call in recent_calls
        ]
    }

@app.get("/clients/{client_id}/calls")
async def get_client_calls(client_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get call history for a client"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    calls = db.query(CallLog).filter(
        CallLog.client_id == client_id
    ).order_by(CallLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": call.id,
            "caller_phone": call.caller_phone,
            "call_sid": call.call_sid,
            "conversation": call.conversation,
            "appointment_booked": call.appointment_booked,
            "call_duration": call.call_duration,
            "created_at": call.created_at
        }
        for call in calls
    ]

# Testing Endpoints
@app.post("/test/conversation")
async def test_conversation(
    client_id: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """Test conversation with AI assistant"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_data = {
        "client_id": client.client_id,
        "business_name": client.business_name,
        "industry": client.industry,
        "business_hours": client.business_hours,
        "services": client.services,
        "faqs": client.faqs,
        "phone_number": client.phone_number
    }
    
    # Generate test response
    test_call_sid = f"test_{client_id}_{datetime.utcnow().timestamp()}"
    result = await call_handler.process_call(client_data, message, test_call_sid)
    
    return result

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
