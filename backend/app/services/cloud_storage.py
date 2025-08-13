"""
Cloud storage service using Cloudinary
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import logging
from typing import Optional, Dict, Any
import tempfile

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Service for managing files in Cloudinary"""
    
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
        self.configured = all([
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET")
        ])
        
        if not self.configured:
            logger.warning("Cloudinary not configured, using local storage fallback")
    
    def upload_audio(self, file_path: str, meeting_id: str) -> Dict[str, Any]:
        """
        Upload audio file to Cloudinary
        Returns dict with url and public_id
        """
        if not self.configured:
            # Fallback to local storage
            return {
                "url": f"/local/audio/{meeting_id}",
                "public_id": None,
                "secure_url": f"/local/audio/{meeting_id}"
            }
        
        try:
            # Upload to Cloudinary with resource type 'video' for audio files
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="video",  # Audio files use 'video' type in Cloudinary
                public_id=f"cybeform/audio/{meeting_id}",
                folder="cybeform/audio",
                overwrite=True,
                notification_url=None
            )
            
            logger.info(f"Audio uploaded successfully: {result['secure_url']}")
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "secure_url": result["secure_url"],
                "duration": result.get("duration"),
                "format": result.get("format")
            }
            
        except Exception as e:
            logger.error(f"Error uploading audio to Cloudinary: {e}")
            raise
    
    def upload_document(self, file_path: str, meeting_id: str, doc_type: str = "report") -> Dict[str, Any]:
        """
        Upload document (Word, PDF) to Cloudinary
        """
        if not self.configured:
            return {
                "url": f"/local/docs/{meeting_id}/{doc_type}",
                "public_id": None
            }
        
        try:
            # Upload as raw file
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="raw",
                public_id=f"cybeform/documents/{meeting_id}_{doc_type}",
                folder="cybeform/documents",
                overwrite=True
            )
            
            logger.info(f"Document uploaded successfully: {result['secure_url']}")
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "secure_url": result["secure_url"]
            }
            
        except Exception as e:
            logger.error(f"Error uploading document to Cloudinary: {e}")
            raise
    
    def delete_file(self, public_id: str, resource_type: str = "video") -> bool:
        """
        Delete file from Cloudinary
        """
        if not self.configured or not public_id:
            return True
        
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"Error deleting file from Cloudinary: {e}")
            return False
    
    def download_file(self, url: str, local_path: str) -> bool:
        """
        Download file from Cloudinary to local path
        """
        try:
            import requests
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False
    
    def get_temp_file_from_cloud(self, url: str) -> Optional[str]:
        """
        Download cloud file to temporary location
        Returns path to temporary file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".audio")
            temp_path = temp_file.name
            temp_file.close()
            
            # Download file
            if self.download_file(url, temp_path):
                return temp_path
            else:
                os.unlink(temp_path)
                return None
                
        except Exception as e:
            logger.error(f"Error getting temp file from cloud: {e}")
            return None
