"""
Audio processing service for CybeMeeting
"""
import os
import subprocess
import librosa
import soundfile as sf
from typing import Optional, Tuple
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for audio file processing and conversion"""
    
    def __init__(self):
        self.target_sample_rate = 16000
        self.target_channels = 1
    
    def get_duration(self, audio_path: str) -> Optional[float]:
        """Get audio duration in seconds"""
        try:
            duration = librosa.get_duration(path=audio_path)
            return round(duration, 2)
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return None
    
    def get_audio_info(self, audio_path: str) -> dict:
        """Get detailed audio information"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            return {
                "duration": round(duration, 2),
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[1],
                "samples": len(y),
                "format": os.path.splitext(audio_path)[1].lower()
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}
    
    def normalize_audio(self, input_path: str, output_path: str) -> bool:
        """
        Normalize audio to WAV format with standard settings
        Returns True if successful, False otherwise
        """
        try:
            # Load audio with librosa (handles most formats)
            y, sr = librosa.load(input_path, sr=self.target_sample_rate, mono=True)
            
            # Normalize audio levels
            y = librosa.util.normalize(y)
            
            # Save as WAV
            sf.write(output_path, y, self.target_sample_rate)
            
            logger.info(f"Audio normalized: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            # Fallback to ffmpeg
            return self._normalize_with_ffmpeg(input_path, output_path)
    
    def _normalize_with_ffmpeg(self, input_path: str, output_path: str) -> bool:
        """Fallback normalization using ffmpeg"""
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-ar", str(self.target_sample_rate),
                "-ac", str(self.target_channels),
                "-acodec", "pcm_s16le",
                "-y", output_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            logger.info(f"Audio normalized with ffmpeg: {input_path} -> {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error with ffmpeg normalization: {e}")
            return False
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate audio file
        Returns (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, "Fichier audio non trouvé"
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > settings.MAX_AUDIO_SIZE_MB:
            return False, f"Fichier trop volumineux ({file_size_mb:.1f}MB > {settings.MAX_AUDIO_SIZE_MB}MB)"
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if file_ext not in settings.allowed_formats_list:
            return False, f"Format non supporté: {file_ext}"
        
        # Try to load audio
        try:
            duration = self.get_duration(file_path)
            if duration is None or duration <= 0:
                return False, "Fichier audio corrompu ou vide"
            
            if duration > 7200:  # 2 hours max
                return False, f"Fichier trop long ({duration/60:.1f} minutes > 120 minutes)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Erreur lors de la lecture du fichier: {str(e)}"
    
    def prepare_for_processing(self, audio_path: str, meeting_dir: str) -> Optional[str]:
        """
        Prepare audio file for AI processing
        Returns path to normalized audio file or None if failed
        """
        try:
            # Validate input file
            is_valid, error_msg = self.validate_audio_file(audio_path)
            if not is_valid:
                logger.error(f"Audio validation failed: {error_msg}")
                return None
            
            # Prepare output path
            normalized_path = os.path.join(meeting_dir, "audio_normalized.wav")
            
            # Normalize audio
            if self.normalize_audio(audio_path, normalized_path):
                return normalized_path
            else:
                logger.error("Audio normalization failed")
                return None
                
        except Exception as e:
            logger.error(f"Error preparing audio for processing: {e}")
            return None
