from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from celery import Celery
import os
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/filedb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Celery configuration
celery_app = Celery(
    'file_processor',
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# FastAPI app
app = FastAPI(title="Cloud File Ingestor", version="1.0.0")

# Database models
class FileRecord(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    status = Column(String, default="queued")  # queued, processing, done, failed
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    file_size = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.post("/files")
async def upload_file(file: UploadFile = File(...), db: Session = None):
    """Upload a file and queue it for processing"""
    if db is None:
        db = SessionLocal()
    
    try:
        file_id = str(uuid.uuid4())
        content = await file.read()
        
        # Create database record
        db_file = FileRecord(
            id=file_id,
            filename=file.filename,
            file_size=len(content),
            status="queued"
        )
        db.add(db_file)
        db.commit()
        
        # Queue async task
        process_file_task.delay(file_id, file.filename, content)
        
        return {
            "id": file_id,
            "filename": file.filename,
            "status": "queued",
            "message": "File uploaded and queued for processing"
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/files")
async def list_files(skip: int = 0, limit: int = 10, db: Session = None):
    """List all uploaded files"""
    if db is None:
        db = SessionLocal()
    
    try:
        files = db.query(FileRecord).offset(skip).limit(limit).all()
        return [
            {
                "id": f.id,
                "filename": f.filename,
                "status": f.status,
                "uploaded_at": f.uploaded_at.isoformat(),
                "file_size": f.file_size
            }
            for f in files
        ]
    finally:
        db.close()

@app.get("/files/{file_id}")
async def get_file_status(file_id: str, db: Session = None):
    """Get file processing status"""
    if db is None:
        db = SessionLocal()
    
    try:
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "status": db_file.status,
            "uploaded_at": db_file.uploaded_at.isoformat(),
            "processed_at": db_file.processed_at.isoformat() if db_file.processed_at else None,
            "file_size": db_file.file_size
        }
    finally:
        db.close()

@app.get("/files/{file_id}/result")
async def get_file_result(file_id: str, db: Session = None):
    """Get file processing result"""
    if db is None:
        db = SessionLocal()
    
    try:
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if db_file.status != "done":
            raise HTTPException(status_code=400, detail=f"File not processed yet (status: {db_file.status})")
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "status": db_file.status,
            "result": db_file.result,
            "processed_at": db_file.processed_at.isoformat()
        }
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Celery task
@celery_app.task(name='app.process_file_task')
def process_file_task(file_id: str, filename: str, content: bytes):
    """Process uploaded file asynchronously"""
    db = SessionLocal()
    try:
        # Update status to processing
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if db_file:
            db_file.status = "processing"
            db.commit()
        
        # Process file
        result = process_file_content(filename, content)
        
        # Update status to done
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if db_file:
            db_file.status = "done"
            db_file.result = result
            db_file.processed_at = datetime.utcnow()
            db.commit()
            logger.info(f"File {file_id} processed successfully")
    except Exception as e:
        logger.error(f"Processing error for {file_id}: {e}")
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if db_file:
            db_file.status = "failed"
            db_file.error = str(e)
            db.commit()
    finally:
        db.close()

def process_file_content(filename: str, content: bytes) -> str:
    """Process file content based on type"""
    if filename.endswith('.txt'):
        return f"Text file processed: {len(content)} bytes, lines: {content.count(b'\\n')}"
    elif filename.endswith('.csv'):
        lines = content.decode('utf-8').split('\\n')
        return f"CSV file processed: {len(lines)} rows, size: {len(content)} bytes"
    elif filename.endswith('.json'):
        return f"JSON file processed: {len(content)} bytes"
    else:
        return f"File processed: {filename}, size: {len(content)} bytes"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
