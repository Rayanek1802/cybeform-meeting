"""
File management service for CybeMeeting
"""
import os
import json
import shutil
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings


class FileManager:
    """Service for managing files and directories"""
    
    def __init__(self):
        self.data_path = settings.DATA_PATH
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(os.path.join(self.data_path, "projects"), exist_ok=True)
    
    def get_project_path(self, project_id: str) -> str:
        """Get path to project directory"""
        return os.path.join(self.data_path, "projects", project_id)
    
    def get_meeting_path(self, project_id: str, meeting_id: str) -> str:
        """Get path to meeting directory"""
        return os.path.join(self.get_project_path(project_id), "meetings", meeting_id)
    
    def save_json(self, data: Dict[Any, Any], file_path: str) -> None:
        """Save data as JSON file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_json(self, file_path: str) -> Optional[Dict[Any, Any]]:
        """Load data from JSON file"""
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    
    def update_meeting_status(self, project_id: str, meeting_id: str, 
                            status_data: Dict[str, Any]) -> None:
        """Update meeting processing status"""
        meeting_dir = self.get_meeting_path(project_id, meeting_id)
        status_file = os.path.join(meeting_dir, "status.json")
        
        # Add timestamp
        status_data["updated_at"] = datetime.now().isoformat()
        
        self.save_json(status_data, status_file)
    
    def cleanup_temp_files(self, directory: str) -> None:
        """Clean up temporary files in directory"""
        if not os.path.exists(directory):
            return
        
        temp_extensions = [".tmp", ".temp", ".processing"]
        for filename in os.listdir(directory):
            if any(filename.endswith(ext) for ext in temp_extensions):
                try:
                    os.remove(os.path.join(directory, filename))
                except Exception:
                    pass
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        if not os.path.exists(file_path):
            return 0.0
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def ensure_meeting_directory(self, project_id: str, meeting_id: str) -> str:
        """Ensure meeting directory exists and return path"""
        meeting_dir = self.get_meeting_path(project_id, meeting_id)
        os.makedirs(meeting_dir, exist_ok=True)
        return meeting_dir

