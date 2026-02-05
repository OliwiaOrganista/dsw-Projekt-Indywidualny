import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app, Base, get_db

# Test database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/filedb")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAPI:
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_list_files_empty(self):
        """Test listing files when empty"""
        response = client.get("/files")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_upload_file(self):
        """Test file upload"""
        # This is a basic test - actual test would need DB setup
        with open(__file__, 'rb') as f:
            response = client.post(
                "/files",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "filename" in data
            assert data["status"] == "queued"
    
    def test_list_files(self):
        """Test listing files"""
        response = client.get("/files?skip=0&limit=10")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
