"""
Meetings API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, BackgroundTasks, status, Depends
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, Annotated
import os
import json
import uuid
from datetime import datetime

from app.models.schemas import (
    MeetingCreate, MeetingResponse, ProcessingRequest, ProcessingStatus,
    AudioUploadResponse, MeetingPreview, MeetingStatus, ProcessingStage, UserResponse
)
from app.core.config import settings
from app.services.file_manager import FileManager
from app.services.audio_processor import AudioProcessor
from app.services.ai_pipeline import AIPipeline
from app.api.endpoints.auth import get_current_user

router = APIRouter()
file_manager = FileManager()
audio_processor = AudioProcessor()
ai_pipeline = AIPipeline()


@router.post("/{project_id}/meetings", response_model=MeetingResponse)
async def create_meeting(
    project_id: str, 
    meeting_data: MeetingCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Créer un nouveau meeting dans un projet"""
    try:
        # Verify project exists and belongs to user
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        # Verify project belongs to user
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        meeting_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Use provided title or generate default
        title = meeting_data.title or f"Réunion du {now.strftime('%d/%m/%Y')}"
        meeting_date = meeting_data.date or now
        
        meeting = {
            "id": meeting_id,
            "title": title,
            "date": meeting_date.isoformat(),
            "expected_speakers": meeting_data.expected_speakers,
            "ai_instructions": meeting_data.ai_instructions,
            "status": MeetingStatus.PENDING.value,
            "progress": 0,
            "duration": None,
            "participants_detected": [],
            "audio_file": None,
            "report_file": None,
            "created_at": now.isoformat()
        }
        
        # Create meeting directory
        meeting_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id)
        os.makedirs(meeting_dir, exist_ok=True)
        
        # Save meeting metadata
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        with open(meeting_file, "w", encoding="utf-8") as f:
            json.dump(meeting, f, ensure_ascii=False, indent=2)
        
        # Update project with new meeting
        project_data["meetings"].append(meeting)
        
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        return MeetingResponse(**meeting)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du meeting: {str(e)}"
        )


@router.post("/{meeting_id}/audio", response_model=AudioUploadResponse)
async def upload_audio(
    meeting_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    file: UploadFile = File(...),
    project_id: str = Form(...)
):
    """Upload d'un fichier audio pour un meeting"""
    try:
        # Verify meeting exists
        meeting_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id)
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        
        if not os.path.exists(meeting_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        # Verify meeting belongs to user (check project ownership)
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom de fichier manquant"
            )
        
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_formats_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format non supporté. Formats autorisés: {', '.join(settings.allowed_formats_list)}"
            )
        
        # Check file size
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > settings.MAX_AUDIO_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Fichier trop volumineux. Taille max: {settings.MAX_AUDIO_SIZE_MB}MB"
            )
        
        # Save audio file
        audio_filename = f"audio.{file_ext}"
        audio_path = os.path.join(meeting_dir, audio_filename)
        
        with open(audio_path, "wb") as f:
            f.write(content)
        
        # Get audio duration
        try:
            duration = audio_processor.get_duration(audio_path)
        except Exception:
            duration = None
        
        # Update meeting metadata
        with open(meeting_file, "r", encoding="utf-8") as f:
            meeting_data = json.load(f)
        
        meeting_data["audio_file"] = audio_filename
        meeting_data["duration"] = duration
        
        with open(meeting_file, "w", encoding="utf-8") as f:
            json.dump(meeting_data, f, ensure_ascii=False, indent=2)
        
        return AudioUploadResponse(
            message="Fichier audio uploadé avec succès",
            filename=audio_filename,
            size_mb=round(file_size_mb, 2),
            duration=duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )


@router.post("/{meeting_id}/process")
async def process_meeting(
    meeting_id: str,
    request: ProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    project_id: str = Query(...)
):
    """Lancer le traitement IA d'un meeting"""
    try:
        meeting_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id)
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        
        if not os.path.exists(meeting_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        # Verify project belongs to user
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        with open(meeting_file, "r", encoding="utf-8") as f:
            meeting_data = json.load(f)
        
        if not meeting_data.get("audio_file"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun fichier audio trouvé pour ce meeting"
            )
        
        # Update status to processing
        meeting_data["status"] = MeetingStatus.PROCESSING.value
        meeting_data["progress"] = 0
        
        if request.expected_speakers:
            meeting_data["expected_speakers"] = request.expected_speakers
        
        with open(meeting_file, "w", encoding="utf-8") as f:
            json.dump(meeting_data, f, ensure_ascii=False, indent=2)
        
        # Start background processing
        background_tasks.add_task(
            ai_pipeline.process_meeting,
            project_id,
            meeting_id,
            meeting_data["expected_speakers"],
            current_user.id  # Add user_id for path resolution
        )
        
        return JSONResponse(
            content={"message": "Traitement lancé avec succès"},
            status_code=status.HTTP_202_ACCEPTED
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du lancement du traitement: {str(e)}"
        )


@router.get("/{meeting_id}/status", response_model=ProcessingStatus)
async def get_processing_status(
    meeting_id: str, 
    project_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Récupérer le statut de traitement d'un meeting"""
    try:
        status_file = os.path.join(
            settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id, "status.json"
        )
        
        if not os.path.exists(status_file):
            return ProcessingStatus(
                stage=ProcessingStage.UPLOAD,
                progress=0,
                message="En attente de traitement"
            )
        
        with open(status_file, "r", encoding="utf-8") as f:
            status_data = json.load(f)
        
        return ProcessingStatus(**status_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )


@router.get("/{meeting_id}/report.docx")
async def download_report(
    meeting_id: str, 
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    project_id: str = Query(...)
):
    """Télécharger le rapport Word d'un meeting"""
    try:
        report_path = os.path.join(
            settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id, "report.docx"
        )
        
        if not os.path.exists(report_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapport non trouvé"
            )
        
        # Verify project belongs to user
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapport non trouvé"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapport non trouvé"
            )
        
        # Ensure file has write permissions before download
        try:
            os.chmod(report_path, 0o666)
        except Exception:
            pass  # Continue even if chmod fails
        
        # Get meeting title for filename
        meeting_file = os.path.join(
            settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id, "meeting.json"
        )
        
        filename = "rapport.docx"
        if os.path.exists(meeting_file):
            try:
                with open(meeting_file, "r", encoding="utf-8") as f:
                    meeting_data = json.load(f)
                safe_title = "".join(c for c in meeting_data.get("title", "rapport") if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}.docx"
            except Exception:
                pass
        
        # Create response with additional headers to prevent read-only mode
        response = FileResponse(
            path=report_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Add headers to indicate the file should be editable
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du téléchargement: {str(e)}"
        )


@router.get("/{meeting_id}/preview", response_model=MeetingPreview)
async def get_meeting_preview(
    meeting_id: str, 
    project_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Récupérer l'aperçu d'un meeting (rapport HTML + transcription)"""
    try:
        meeting_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id)
        
        # Verify project belongs to user
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        # Load meeting data
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        if not os.path.exists(meeting_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        with open(meeting_file, "r", encoding="utf-8") as f:
            meeting_data = json.load(f)
        
        # Load analysis results
        analysis_file = os.path.join(meeting_dir, "analysis.json")
        if not os.path.exists(analysis_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analyse non trouvée - le traitement n'est peut-être pas terminé"
            )
        
        with open(analysis_file, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        
        # Load transcript
        transcript_file = os.path.join(meeting_dir, "transcript.json")
        transcript = []
        if os.path.exists(transcript_file):
            with open(transcript_file, "r", encoding="utf-8") as f:
                transcript_data = json.load(f)
                transcript = transcript_data.get("segments", [])
        
        # Generate HTML preview
        report_html = ai_pipeline.generate_html_preview(analysis_data, meeting_data)
        
        # Prepare stats
        stats = {
            "total_segments": len(transcript),
            "total_words": sum(len(seg.get("text", "").split()) for seg in transcript),
            "processing_date": meeting_data.get("processed_at", ""),
            "analysis_version": "1.0"
        }
        
        return MeetingPreview(
            report_html=report_html,
            stats=stats,
            participants=meeting_data.get("participants_detected", []),
            duration=meeting_data.get("duration", 0.0),
            transcript=transcript
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'aperçu: {str(e)}"
        )


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: str, 
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    project_id: str = Query(...)
):
    """Supprimer un meeting et tous ses fichiers"""
    try:
        meeting_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id)
        
        # Vérifier que le meeting existe
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        if not os.path.exists(meeting_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        # Supprimer tout le dossier du meeting
        import shutil
        if os.path.exists(meeting_dir):
            shutil.rmtree(meeting_dir)
        
        return JSONResponse(
            content={"message": "Meeting supprimé avec succès"},
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: str, 
    meeting_data: MeetingCreate, 
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    project_id: str = Query(...)
):
    """Modifier les informations d'un meeting"""
    try:
        meeting_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "meetings", meeting_id)
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        
        # Vérifier que le meeting existe
        if not os.path.exists(meeting_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting non trouvé"
            )
        
        # Charger les données existantes
        with open(meeting_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        
        # Mettre à jour seulement les champs modifiables
        existing_data["title"] = meeting_data.title
        existing_data["expected_speakers"] = meeting_data.expected_speakers
        existing_data["ai_instructions"] = meeting_data.ai_instructions
        existing_data["updated_at"] = datetime.now().isoformat()
        
        # Sauvegarder
        with open(meeting_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        # Retourner les données mises à jour
        return MeetingResponse(
            id=existing_data["id"],
            title=existing_data["title"],
            date=existing_data["date"],
            expected_speakers=existing_data["expected_speakers"],
            ai_instructions=existing_data.get("ai_instructions"),
            status=existing_data.get("status", "En attente"),
            progress=existing_data.get("progress", 0),
            duration=existing_data.get("duration"),
            participants_detected=existing_data.get("participants_detected", []),
            audio_file=existing_data.get("audio_file"),
            report_file=existing_data.get("report_file"),
            created_at=existing_data["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la modification: {str(e)}"
        )
