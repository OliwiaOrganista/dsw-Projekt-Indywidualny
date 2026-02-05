import os
import logging
from celery import Celery
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/filedb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Celery configuration
app = Celery(
    'file_processor',
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# Database models
class FileRecord(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    status = Column(String, default="queued")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    file_size = Column(Integer)

# Tasks
@app.task(name='process_file_task')
def process_file_task(file_id: str, filename: str, content: bytes):
    """Process uploaded file asynchronously"""
    db = SessionLocal()
    try:
        logger.info(f"Processing file {file_id}: {filename}")
        
        # Update status to processing
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if db_file:
            db_file.status = "processing"
            db.commit()
        
        # Simulate processing
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
        logger.error(f"Processing error for {file_id}: {e}", exc_info=True)
        db_file = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if db_file:
            db_file.status = "failed"
            db_file.error = str(e)
            db.commit()
    finally:
        db.close()

def process_file_content(filename: str, content: bytes) -> str:
    """Process file content based on type"""
    try:
        if filename.endswith('.txt'):
            text = content.decode('utf-8')
            return f"Text file processed: {len(content)} bytes, lines: {len(text.split(chr(10)))}"
        
        elif filename.endswith('.csv'):
            text = content.decode('utf-8')
            lines = text.split('\n')
            rows = len([l for l in lines if l.strip()])
            cols = len(lines[0].split(',')) if rows > 0 else 0
            return f"CSV file: {rows} rows, {cols} columns, {len(content)} bytes"
        
        elif filename.endswith('.json'):
            import json
            data = json.loads(content.decode('utf-8'))
            return f"JSON file processed: {len(str(data))} chars, valid JSON"
        
        else:
            return f"File processed: {filename}, size: {len(content)} bytes"
    
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        raise

if __name__ == "__main__":
    app.worker_main(['worker', '--loglevel=info'])
