from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL Database setup - reads from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model (same as before)
class SnippetDB(Base):
    __tablename__ = "snippets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    tags = Column(JSON)  # PostgreSQL has native JSON support
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(JSON)  # Store embeddings as JSON array

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()