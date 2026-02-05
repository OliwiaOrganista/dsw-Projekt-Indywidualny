import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.main import Base, FileRecord

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    yield db
    db.close()

def test_file_record_creation(test_db):
    """Test creating file record"""
    file = FileRecord(
        id="test-id",
        filename="test.txt",
        file_size=1024,
        status="queued"
    )
    test_db.add(file)
    test_db.commit()
    
    stored_file = test_db.query(FileRecord).filter(FileRecord.id == "test-id").first()
    assert stored_file is not None
    assert stored_file.filename == "test.txt"
    assert stored_file.status == "queued"

def test_file_status_update(test_db):
    """Test updating file status"""
    file = FileRecord(
        id="test-id-2",
        filename="test2.csv",
        file_size=2048,
        status="queued"
    )
    test_db.add(file)
    test_db.commit()
    
    # Update status
    file.status = "processing"
    test_db.commit()
    
    stored_file = test_db.query(FileRecord).filter(FileRecord.id == "test-id-2").first()
    assert stored_file.status == "processing"

def test_file_result(test_db):
    """Test storing file result"""
    file = FileRecord(
        id="test-id-3",
        filename="test3.json",
        file_size=512,
        status="done",
        result="Processed: 512 bytes"
    )
    test_db.add(file)
    test_db.commit()
    
    stored_file = test_db.query(FileRecord).filter(FileRecord.id == "test-id-3").first()
    assert stored_file.status == "done"
    assert stored_file.result == "Processed: 512 bytes"
