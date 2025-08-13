"""
CybeMeeting Backend - Version légère pour Render (Plan Gratuit)
Utilise uniquement les API cloud, pas de modèles locaux
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os
import logging
from dotenv import load_dotenv
from typing import List, Optional
import tempfile
import json
from datetime import datetime

# Import seulement ce qui est nécessaire (pas les modèles lourds)
from app.models.database import init_db, get_db, User, Project, Meeting
from app.models.schemas import (
    UserCreate, UserLogin, UserResponse,
    ProjectCreate, ProjectResponse,
    MeetingCreate, MeetingResponse,
    ProcessingStatus
)
from app.services.auth_service_db import AuthServiceDB
from app.services.cloud_storage import CloudStorageService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 CybeMeeting API (Render Lite) starting...")
    logger.info("💡 Version allégée pour plan gratuit Render")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"Database init error: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 CybeMeeting API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="CybeMeeting API - Render Lite",
    description="Version allégée pour Render plan gratuit",
    version="1.0.0-lite",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://cybeform-frontend.onrender.com"
]

# Ajouter tous les domaines Render possibles
allowed_origins.extend([
    "https://*.onrender.com",
    "https://cybeform-frontend.onrender.com",
    "https://cybeform-frontend-*.onrender.com"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporairement pour le debug
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health & Root ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "CybeMeeting API - Render Lite",
            "version": "1.0.0-lite",
            "mode": "cloud-only",
            "memory": "optimized for 512MB"
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "CybeMeeting API - Version Render Lite",
            "docs": "/docs",
            "health": "/health",
            "note": "Version optimisée pour plan gratuit"
        }
    )


# ==================== Authentication ====================

@app.post("/api/auth/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        auth_service = AuthServiceDB(db)
        user = auth_service.create_user(user_data)
        token = auth_service.create_access_token(user.id)
        
        return {
            "user": user.dict(),
            "token": token
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/auth/login", response_model=dict)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    auth_service = AuthServiceDB(db)
    user = auth_service.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_service.create_access_token(user.id)
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company": user.company
        },
        "token": token
    }


# ==================== Projects ====================

@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    user_id: Optional[str] = None
):
    """Get all projects for a user"""
    if not user_id:
        projects = db.query(Project).all()
    else:
        projects = db.query(Project).filter(Project.user_id == user_id).all()
    
    return [ProjectResponse.from_orm(p) for p in projects]


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None
):
    """Create a new project"""
    if not user_id:
        user = db.query(User).first()
        if not user:
            # Créer un utilisateur de démo si aucun n'existe
            demo_user = User(
                email="demo@cybeform.com",
                password_hash="demo",
                first_name="Demo",
                last_name="User",
                company="Demo Company"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            user = demo_user
        user_id = user.id
    
    project = Project(
        user_id=user_id,
        name=project_data.name,
        description=project_data.description,
        client=project_data.client,
        location=project_data.location
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse.from_orm(project)


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse.from_orm(project)


# ==================== Meetings ====================

@app.get("/api/projects/{project_id}/meetings", response_model=List[MeetingResponse])
async def get_meetings(project_id: str, db: Session = Depends(get_db)):
    """Get all meetings for a project"""
    meetings = db.query(Meeting).filter(Meeting.project_id == project_id).all()
    return [MeetingResponse.from_orm(m) for m in meetings]


@app.post("/api/projects/{project_id}/meetings")
async def create_meeting(
    project_id: str,
    title: str = Form(...),
    date: str = Form(...),
    location: str = Form(None),
    participants: str = Form("[]"),
    description: str = Form(None),
    audio_file: UploadFile = File(...),
    expected_speakers: int = Form(2),
    db: Session = Depends(get_db)
):
    """Create a new meeting with audio file - VERSION LITE"""
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create meeting record
        meeting = Meeting(
            project_id=project_id,
            title=title,
            date=datetime.fromisoformat(date),
            location=location,
            participants=participants,
            description=description,
            status="processing"
        )
        
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        
        # Save audio file to Cloudinary
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}")
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.close()
            
            storage = CloudStorageService()
            if storage.configured:
                upload_result = storage.upload_audio(temp_file.name, meeting.id)
                meeting.audio_url = upload_result["url"]
                meeting.audio_public_id = upload_result["public_id"]
                meeting.audio_duration = upload_result.get("duration")
            else:
                # Pas de Cloudinary configuré
                meeting.audio_url = f"/local/audio/{meeting.id}"
            
            os.unlink(temp_file.name)
        except Exception as e:
            logger.error(f"Error uploading audio: {e}")
            meeting.audio_url = f"/local/audio/{meeting.id}"
        
        # Simulation d'analyse (pas de traitement réel dans la version lite)
        meeting.status = "completed"
        meeting.processing_progress = 100
        meeting.summary = "📝 Analyse automatique désactivée en mode démo (plan gratuit Render)"
        meeting.key_points = json.dumps([
            "✅ Fichier audio uploadé avec succès",
            "💡 Pour activer l'analyse IA, passez au plan payant",
            "🔧 Ou utilisez une instance locale avec plus de mémoire"
        ])
        meeting.action_items = json.dumps([])
        meeting.risks = json.dumps([])
        
        db.commit()
        
        return {
            "meeting_id": meeting.id,
            "status": "completed",
            "message": "Meeting créé (analyse IA désactivée en mode démo)",
            "note": "Plan gratuit Render - Pas assez de mémoire pour l'analyse IA"
        }
        
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(project_id: str, meeting_id: str, db: Session = Depends(get_db)):
    """Get a specific meeting"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.project_id == project_id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return MeetingResponse.from_orm(meeting)


@app.get("/api/projects/{project_id}/meetings/{meeting_id}/status")
async def get_meeting_status(project_id: str, meeting_id: str, db: Session = Depends(get_db)):
    """Get processing status of a meeting"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.project_id == project_id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return ProcessingStatus(
        status=meeting.status or "completed",
        stage="completed",
        progress=100,
        message="Mode démo - Analyse IA désactivée (plan gratuit)"
    )


@app.delete("/api/projects/{project_id}/meetings/{meeting_id}")
async def delete_meeting(project_id: str, meeting_id: str, db: Session = Depends(get_db)):
    """Delete a meeting"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.project_id == project_id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Delete from Cloudinary if configured
    if meeting.audio_public_id:
        try:
            storage = CloudStorageService()
            storage.delete_file(meeting.audio_public_id)
        except:
            pass
    
    db.delete(meeting)
    db.commit()
    
    return {"message": "Meeting deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
