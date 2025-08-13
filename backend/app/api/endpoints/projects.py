"""
Projects API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List, Annotated
import os
import json
import uuid
from datetime import datetime

from app.models.schemas import ProjectCreate, ProjectResponse, MeetingResponse, UserResponse
from app.core.config import settings
from app.services.file_manager import FileManager
from app.api.endpoints.auth import get_current_user

router = APIRouter()
file_manager = FileManager()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Créer un nouveau projet BTP"""
    try:
        project_id = str(uuid.uuid4())
        now = datetime.now()
        
        project = {
            "id": project_id,
            "name": project_data.name,
            "user_id": current_user.id,
            "created_at": now.isoformat(),
            "meetings": []
        }
        
        # Create project directory in user's folder
        project_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Save project metadata
        project_file = os.path.join(project_dir, "project.json")
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        return ProjectResponse(
            id=project_id,
            name=project_data.name,
            created_at=now,
            meetings_count=0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du projet: {str(e)}"
        )


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    """Lister tous les projets de l'utilisateur"""
    try:
        projects = []
        projects_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects")
        
        if not os.path.exists(projects_dir):
            return projects
        
        for project_id in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_id)
            if not os.path.isdir(project_path):
                continue
                
            project_file = os.path.join(project_path, "project.json")
            if not os.path.exists(project_file):
                continue
                
            try:
                with open(project_file, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                
                # Count meetings
                meetings_count = len(project_data.get("meetings", []))
                
                projects.append(ProjectResponse(
                    id=project_data["id"],
                    name=project_data["name"],
                    created_at=datetime.fromisoformat(project_data["created_at"]),
                    meetings_count=meetings_count
                ))
            except Exception as e:
                print(f"Erreur lors du chargement du projet {project_id}: {e}")
                continue
        
        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x.created_at, reverse=True)
        return projects
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des projets: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Récupérer un projet par ID"""
    try:
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        # Verify project belongs to user
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        meetings_count = len(project_data.get("meetings", []))
        
        return ProjectResponse(
            id=project_data["id"],
            name=project_data["name"],
            created_at=datetime.fromisoformat(project_data["created_at"]),
            meetings_count=meetings_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du projet: {str(e)}"
        )


@router.put("/{project_id}")
async def update_project(
    project_id: str, 
    project_data: ProjectCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Mettre à jour un projet"""
    try:
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        # Load existing project
        with open(project_file, "r", encoding="utf-8") as f:
            existing_project = json.load(f)
        
        # Verify project belongs to user
        if existing_project.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        # Update project name
        existing_project["name"] = project_data.name
        existing_project["updated_at"] = datetime.now().isoformat()
        
        # Save updated project
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(existing_project, f, ensure_ascii=False, indent=2)
        
        return existing_project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du projet: {str(e)}"
        )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Supprimer un projet et tous ses meetings"""
    try:
        project_dir = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id)
        project_file = os.path.join(project_dir, "project.json")
        
        if not os.path.exists(project_dir) or not os.path.exists(project_file):
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
        
        # Remove entire project directory
        import shutil
        shutil.rmtree(project_dir)
        
        return JSONResponse(
            content={"message": "Projet supprimé avec succès"},
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du projet: {str(e)}"
        )


@router.get("/{project_id}/meetings", response_model=List[MeetingResponse])
async def list_project_meetings(
    project_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """Lister tous les meetings d'un projet"""
    try:
        project_file = os.path.join(settings.DATA_PATH, "users", current_user.id, "projects", project_id, "project.json")
        
        if not os.path.exists(project_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        
        # Verify project belongs to user
        if project_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projet non trouvé"
            )
        
        meetings = []
        for meeting_data in project_data.get("meetings", []):
            meetings.append(MeetingResponse(**meeting_data))
        
        # Sort by creation date (newest first)
        meetings.sort(key=lambda x: x.created_at, reverse=True)
        return meetings
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des meetings: {str(e)}"
        )
