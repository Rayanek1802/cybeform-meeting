"""
Transcription service using OpenAI Whisper API or local Whisper
"""
import os
import openai
from typing import List, Dict, Any, Optional
import logging
import whisper
import torch

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for audio transcription using Whisper"""
    
    def __init__(self):
        self.openai_client = None
        self.local_model = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize transcription services"""
        # Initialize OpenAI client if API key is available
        if settings.is_openai_available and settings.WHISPER_API.lower() == "on":
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI Whisper API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize local Whisper as fallback
        if not self.openai_client:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.local_model = whisper.load_model("base", device=device)
                logger.info(f"Local Whisper model loaded on {device}")
            except Exception as e:
                logger.error(f"Failed to load local Whisper model: {e}")
    
    def transcribe_audio(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """
        Transcribe audio file
        Returns transcription with segments and text
        """
        try:
            # Try OpenAI API first
            if self.openai_client:
                return self._transcribe_with_openai(audio_path, language)
            
            # Fallback to local model
            elif self.local_model:
                return self._transcribe_with_local(audio_path, language)
            
            else:
                raise Exception("No transcription service available")
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return self._create_fallback_transcription(audio_path)
    
    def _transcribe_with_openai(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            logger.info(f"Transcribing with OpenAI API: {audio_path}")
            
            # Check file size (OpenAI limit is 25MB)
            file_size = os.path.getsize(audio_path)
            max_size = 25 * 1024 * 1024  # 25MB in bytes
            
            if file_size > max_size:
                logger.warning(f"File size ({file_size} bytes) exceeds OpenAI limit ({max_size} bytes). Splitting audio...")
                return self._transcribe_large_file_with_openai(audio_path, language)
            
            with open(audio_path, "rb") as audio_file:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            
            # Convert to our format
            segments = []
            for segment in response.segments:
                # Handle both dict and object formats
                if isinstance(segment, dict):
                    segments.append({
                        "start_time": round(segment.get("start", 0.0), 2),
                        "end_time": round(segment.get("end", 0.0), 2),
                        "text": segment.get("text", "").strip(),
                        "confidence": segment.get("avg_logprob", 0.0)
                    })
                else:
                    segments.append({
                        "start_time": round(segment.start, 2),
                        "end_time": round(segment.end, 2),
                        "text": segment.text.strip(),
                        "confidence": getattr(segment, 'avg_logprob', 0.0)
                    })
            
            result = {
                "text": response.text,
                "language": response.language,
                "segments": segments,
                "service": "openai"
            }
            
            logger.info(f"OpenAI transcription completed: {len(segments)} segments")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI transcription error: {e}")
            raise
    
    def _transcribe_large_file_with_openai(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """Transcribe large files by splitting them into smaller chunks"""
        try:
            from app.services.audio_processor import AudioProcessor
            import tempfile
            import shutil
            
            audio_processor = AudioProcessor()
            
            # Get duration and split into 10-minute chunks (safer than file size)
            duration = audio_processor.get_duration(audio_path)
            if not duration:
                raise Exception("Could not determine audio duration")
            
            chunk_duration = 600  # 10 minutes per chunk
            chunks_count = max(1, int(duration / chunk_duration) + (1 if duration % chunk_duration else 0))
            
            logger.info(f"Splitting {duration:.1f}s audio into {chunks_count} chunks of {chunk_duration}s each")
            
            all_segments = []
            combined_text = ""
            
            with tempfile.TemporaryDirectory() as temp_dir:
                for i in range(chunks_count):
                    start_time = i * chunk_duration
                    end_time = min((i + 1) * chunk_duration, duration)
                    
                    # Create chunk file path
                    chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
                    
                    # Extract audio chunk using ffmpeg
                    import subprocess
                    cmd = [
                        "ffmpeg", "-i", audio_path,
                        "-ss", str(start_time),
                        "-t", str(end_time - start_time),
                        "-acodec", "copy",
                        "-y", chunk_path
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        logger.error(f"Failed to create chunk {i}: {result.stderr}")
                        continue
                    
                    # Transcribe chunk
                    logger.info(f"Transcribing chunk {i+1}/{chunks_count} ({start_time:.1f}s - {end_time:.1f}s)")
                    
                    with open(chunk_path, "rb") as chunk_file:
                        chunk_response = self.openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=chunk_file,
                            language=language,
                            response_format="verbose_json"
                        )
                    
                    # Add chunk text to combined text
                    if chunk_response.text.strip():
                        combined_text += chunk_response.text.strip() + " "
                    
                    # Adjust segment timestamps and add to all_segments
                    for segment in chunk_response.segments:
                        if isinstance(segment, dict):
                            all_segments.append({
                                "start_time": round(segment.get("start", 0.0) + start_time, 2),
                                "end_time": round(segment.get("end", 0.0) + start_time, 2),
                                "text": segment.get("text", "").strip(),
                                "confidence": segment.get("avg_logprob", 0.0)
                            })
                        else:
                            all_segments.append({
                                "start_time": round(segment.start + start_time, 2),
                                "end_time": round(segment.end + start_time, 2),
                                "text": segment.text.strip(),
                                "confidence": getattr(segment, 'avg_logprob', 0.0)
                            })
            
            result = {
                "text": combined_text.strip(),
                "language": language,
                "segments": all_segments,
                "service": "openai-chunked"
            }
            
            logger.info(f"Large file transcription completed: {len(all_segments)} segments from {chunks_count} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Large file transcription error: {e}")
            raise
    
    def _transcribe_with_local(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """Transcribe using local Whisper model"""
        try:
            logger.info(f"Transcribing with local Whisper: {audio_path}")
            
            result = self.local_model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                verbose=False
            )
            
            # Convert to our format
            segments = []
            for segment in result["segments"]:
                segments.append({
                    "start_time": round(segment["start"], 2),
                    "end_time": round(segment["end"], 2),
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0.0)
                })
            
            response = {
                "text": result["text"],
                "language": result["language"],
                "segments": segments,
                "service": "local"
            }
            
            logger.info(f"Local transcription completed: {len(segments)} segments")
            return response
            
        except Exception as e:
            logger.error(f"Local transcription error: {e}")
            raise
    
    def _create_fallback_transcription(self, audio_path: str) -> Dict[str, Any]:
        """Create fallback transcription when services fail"""
        logger.warning("Creating fallback transcription")
        
        from app.services.audio_processor import AudioProcessor
        audio_processor = AudioProcessor()
        duration = audio_processor.get_duration(audio_path) or 60.0
        
        # Create mock segments
        num_segments = max(1, int(duration / 10))  # One segment per 10 seconds
        segment_duration = duration / num_segments
        
        segments = []
        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = min((i + 1) * segment_duration, duration)
            
            segments.append({
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "text": f"[Segment {i+1} - Transcription non disponible]",
                "confidence": 0.0
            })
        
        return {
            "text": "[Transcription automatique non disponible - Veuillez configurer OpenAI API ou vérifier le service de transcription]",
            "language": "fr",
            "segments": segments,
            "service": "fallback"
        }
    
    def align_transcription_with_diarization(
        self, 
        transcription: Dict[str, Any], 
        diarization_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Align transcription segments with speaker diarization
        Returns aligned segments with speaker labels and text
        """
        try:
            aligned_segments = []
            
            for diar_segment in diarization_segments:
                # Find overlapping transcription segments
                overlapping_texts = []
                
                for trans_segment in transcription["segments"]:
                    # Check for overlap
                    if (trans_segment["start_time"] < diar_segment["end_time"] and 
                        trans_segment["end_time"] > diar_segment["start_time"]):
                        
                        overlapping_texts.append(trans_segment["text"])
                
                # Combine texts
                combined_text = " ".join(overlapping_texts).strip()
                if not combined_text:
                    combined_text = "[Aucun texte détecté]"
                
                aligned_segments.append({
                    "speaker": diar_segment["speaker"],
                    "start_time": diar_segment["start_time"],
                    "end_time": diar_segment["end_time"],
                    "duration": diar_segment["duration"],
                    "text": combined_text
                })
            
            logger.info(f"Aligned {len(aligned_segments)} segments")
            return aligned_segments
            
        except Exception as e:
            logger.error(f"Error aligning transcription with diarization: {e}")
            return []
    
    def clean_transcription_text(self, text: str) -> str:
        """Clean and normalize transcription text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Basic French text cleaning
        replacements = {
            " , ": ", ",
            " . ": ". ",
            " ? ": "? ",
            " ! ": "! ",
            " : ": ": ",
            " ; ": "; ",
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
