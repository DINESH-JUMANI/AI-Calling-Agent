import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_client():
    """Test client creation"""
    client_data = {
        "name": "Test Client",
        "business_name": "Test Business",
        "phone_number": "+1234567890",
        "email": "test@example.com",
        "industry": "Technology"
    }
    
    response = client.post("/clients", json=client_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Client"
    assert data["business_name"] == "Test Business"

def test_get_clients():
    """Test getting all clients"""
    response = client.get("/clients")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"