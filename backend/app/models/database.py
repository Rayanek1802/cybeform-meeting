"""
Database models for CybeMeeting with PostgreSQL
"""
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/cybeform.db")
# Fix for Render PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relations
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    client = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="projects")
    meetings = relationship("Meeting", back_populates="project", cascade="all, delete-orphan")


class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    location = Column(String)
    participants = Column(Text)  # JSON string
    description = Column(Text)
    
    # Audio file info (stored in Cloudinary)
    audio_url = Column(String)
    audio_public_id = Column(String)  # Cloudinary public ID for deletion
    audio_duration = Column(Float)
    audio_format = Column(String)
    
    # Processing status
    status = Column(String, default="pending")
    processing_stage = Column(String)
    processing_progress = Column(Integer, default=0)
    processing_message = Column(String)
    
    # Analysis results (JSON strings)
    transcript = Column(Text)
    summary = Column(Text)
    action_items = Column(Text)
    risks = Column(Text)
    key_points = Column(Text)
    
    # Report
    report_url = Column(String)
    report_public_id = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    project = relationship("Project", back_populates="meetings")


# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
