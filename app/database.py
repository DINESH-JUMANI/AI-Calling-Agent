from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from app.config import settings

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    business_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    industry = Column(String)
    business_hours = Column(JSON)  # {"monday": {"open": "09:00", "close": "17:00"}}
    services = Column(Text)
    faqs = Column(Text)
    appointment_webhook_url = Column(String)
    voice_id = Column(String)  # ElevenLabs voice ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, nullable=False)
    caller_phone = Column(String, nullable=False)
    call_sid = Column(String, unique=True, nullable=False)
    conversation = Column(JSON)  # Store conversation history
    appointment_booked = Column(Boolean, default=False)
    call_duration = Column(Integer)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)

class Knowledge(Base):
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String)  # file name or source description
    embedding_id = Column(String)  # ChromaDB document ID
    created_at = Column(DateTime, default=datetime.utcnow)

# Create database engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
