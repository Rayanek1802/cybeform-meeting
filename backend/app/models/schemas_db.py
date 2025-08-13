"""
Pydantic schemas for database models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== User Schemas ====================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str
    last_name: str
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    company: Optional[str]
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: str


# ==================== Project Schemas ====================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    client: Optional[str] = None
    location: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client: Optional[str] = None
    location: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    client: Optional[str]
    location: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Meeting Schemas ====================

class MeetingCreate(BaseModel):
    title: str
    date: datetime
    location: Optional[str] = None
    participants: List[str] = []
    description: Optional[str] = None
    expected_speakers: int = 2


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    participants: Optional[List[str]] = None
    description: Optional[str] = None


class MeetingResponse(BaseModel):
    id: str
    project_id: str
    title: str
    date: datetime
    location: Optional[str]
    participants: Optional[str]  # JSON string
    description: Optional[str]
    
    # Audio info
    audio_url: Optional[str]
    audio_duration: Optional[float]
    audio_format: Optional[str]
    
    # Processing status
    status: str
    processing_stage: Optional[str]
    processing_progress: Optional[int]
    processing_message: Optional[str]
    
    # Analysis results
    transcript: Optional[str]
    summary: Optional[str]
    action_items: Optional[str]
    risks: Optional[str]
    key_points: Optional[str]
    
    # Report
    report_url: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Processing Schemas ====================

class ProcessingStage(str, Enum):
    UPLOAD = "upload"
    DIARIZATION = "diarization"
    TRANSCRIPTION = "transcription"
    ANALYSIS = "analysis"
    REPORT = "report"
    COMPLETED = "completed"
    ERROR = "error"


class ProcessingStatus(BaseModel):
    status: str
    stage: str
    progress: int
    message: str


class MeetingStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


# ==================== Analysis Schemas ====================

class ActionItem(BaseModel):
    description: str
    responsible: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[str] = None


class RiskItem(BaseModel):
    description: str
    severity: Optional[str] = None
    mitigation: Optional[str] = None


class MeetingAnalysis(BaseModel):
    summary: str
    key_points: List[str]
    action_items: List[ActionItem]
    risks: List[RiskItem]
    decisions: List[str]
    next_steps: List[str]
