"""
Pydantic models for CybeMeeting API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessingStage(str, Enum):
    """Processing stages for meetings"""
    UPLOAD = "upload"
    DIARIZATION = "diarization"
    TRANSCRIPTION = "transcription"
    REPORT = "report"
    DONE = "done"
    ERROR = "error"


class MeetingStatus(str, Enum):
    """Meeting status"""
    PENDING = "En attente"
    PROCESSING = "En cours de traitement"
    COMPLETED = "Terminé"
    ERROR = "Erreur"


# Removed MeetingType enum - replaced by custom user instructions


# Project models
class ProjectCreate(BaseModel):
    """Schema for creating a project"""
    name: str = Field(..., min_length=1, max_length=200, description="Nom du projet BTP")


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str
    name: str
    created_at: datetime
    meetings_count: int = 0


# Meeting models
class MeetingCreate(BaseModel):
    """Schema for creating a meeting"""
    title: Optional[str] = Field(None, max_length=200, description="Titre du meeting")
    date: Optional[datetime] = Field(None, description="Date et heure du meeting")
    expected_speakers: int = Field(..., ge=1, le=20, description="Nombre d'intervenants attendus")
    ai_instructions: Optional[str] = Field(None, max_length=1000, description="Instructions personnalisées pour l'analyse IA")


class MeetingResponse(BaseModel):
    """Schema for meeting response"""
    id: str
    title: str
    date: datetime
    expected_speakers: int
    ai_instructions: Optional[str] = None
    status: MeetingStatus
    progress: int = Field(0, ge=0, le=100)
    duration: Optional[float] = None
    participants_detected: List[str] = []
    audio_file: Optional[str] = None
    report_file: Optional[str] = None
    created_at: datetime


class ProcessingRequest(BaseModel):
    """Schema for processing request"""
    expected_speakers: Optional[int] = Field(None, ge=1, le=20)


class ProcessingStatus(BaseModel):
    """Schema for processing status"""
    stage: ProcessingStage
    progress: int = Field(0, ge=0, le=100)
    message: str
    estimated_time_remaining: Optional[int] = None  # seconds


# AI Analysis models
class ActionItem(BaseModel):
    """Action item from meeting"""
    tache: str
    responsable: str
    echeance: Optional[str] = None


class RiskItem(BaseModel):
    """Risk item from meeting"""
    risque: str
    impact: str
    mitigation: str


class MeetingAnalysis(BaseModel):
    """AI analysis result"""
    meta: Dict[str, Any]
    objectifs: List[str]
    problemes: List[str]
    decisions: List[str]
    actions: List[ActionItem]
    risques: List[RiskItem]
    points_techniques_btp: List[str]
    planning: List[str]
    budget_chiffrage: List[str]
    divers: List[str]
    exclusions: List[str]
    full_transcript_ref: Optional[str] = None


class TranscriptSegment(BaseModel):
    """Transcript segment"""
    speaker: str
    start_time: float
    end_time: float
    text: str


class MeetingPreview(BaseModel):
    """Preview of meeting report"""
    report_html: str
    stats: Dict[str, Any]
    participants: List[str]
    duration: float
    transcript: List[TranscriptSegment]


# Audio models
class AudioUploadResponse(BaseModel):
    """Response for audio upload"""
    message: str
    filename: str
    size_mb: float
    duration: Optional[float] = None


# Authentication models
class UserCreate(BaseModel):
    """Schema for user creation"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    company: Optional[str] = Field(None, max_length=100, description="Company name")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    first_name: str
    last_name: str
    company: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[str] = None


# Error models
class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
