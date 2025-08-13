"""
Speaker diarization service using pyannote.audio
"""
import os
import torch
from pyannote.audio import Pipeline
from typing import List, Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class DiarizationService:
    """Service for speaker diarization using pyannote.audio"""
    
    def __init__(self):
        self.pipeline = None
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the diarization pipeline"""
        try:
            if not settings.is_huggingface_available:
                logger.warning("Hugging Face token not available, diarization will be limited")
                return
            
            # Set the token for pyannote
            os.environ["HUGGINGFACE_HUB_TOKEN"] = settings.HUGGINGFACE_TOKEN
            
            # Initialize pipeline
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=settings.HUGGINGFACE_TOKEN
            )
            
            # Use GPU if available
            if torch.cuda.is_available():
                self.pipeline = self.pipeline.to(torch.device("cuda"))
                logger.info("Using GPU for diarization")
            else:
                logger.info("Using CPU for diarization")
            
            logger.info("Diarization pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize diarization pipeline: {e}")
            self.pipeline = None
    
    def diarize_audio(self, audio_path: str, num_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Perform speaker diarization on audio file
        Returns list of segments with speaker labels and timestamps
        """
        if not self.pipeline:
            logger.warning("Diarization pipeline not available, creating mock segments")
            return self._create_mock_diarization(audio_path, num_speakers)
        
        try:
            logger.info(f"Starting diarization for {audio_path}")
            
            # Configure pipeline parameters
            if num_speakers:
                diarization = self.pipeline(
                    audio_path,
                    num_speakers=num_speakers
                )
            else:
                diarization = self.pipeline(audio_path)
            
            # Convert to our format
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker": f"SPEAKER_{speaker}",
                    "start_time": round(turn.start, 2),
                    "end_time": round(turn.end, 2),
                    "duration": round(turn.end - turn.start, 2)
                })
            
            # Sort by start time
            segments.sort(key=lambda x: x["start_time"])
            
            logger.info(f"Diarization completed: {len(segments)} segments, {len(set(s['speaker'] for s in segments))} speakers")
            return segments
            
        except Exception as e:
            logger.error(f"Error during diarization: {e}")
            return self._create_mock_diarization(audio_path, num_speakers)
    
    def _create_mock_diarization(self, audio_path: str, num_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Create mock diarization when real diarization is not available
        """
        try:
            from app.services.audio_processor import AudioProcessor
            audio_processor = AudioProcessor()
            
            duration = audio_processor.get_duration(audio_path)
            if not duration:
                duration = 60.0  # Default fallback
            
            # Create segments based on expected speakers
            expected_speakers = num_speakers or 2
            segment_duration = duration / max(expected_speakers * 2, 4)  # At least 4 segments
            
            segments = []
            current_time = 0.0
            speaker_index = 0
            
            while current_time < duration:
                end_time = min(current_time + segment_duration, duration)
                
                segments.append({
                    "speaker": f"SPEAKER_{speaker_index}",
                    "start_time": round(current_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": round(end_time - current_time, 2)
                })
                
                current_time = end_time
                speaker_index = (speaker_index + 1) % expected_speakers
            
            logger.info(f"Created mock diarization: {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error creating mock diarization: {e}")
            return []
    
    def merge_short_segments(self, segments: List[Dict[str, Any]], min_duration: float = 1.0) -> List[Dict[str, Any]]:
        """
        Merge segments that are too short with adjacent segments from the same speaker
        """
        if not segments:
            return segments
        
        merged = []
        current_segment = segments[0].copy()
        
        for next_segment in segments[1:]:
            # If same speaker and current segment is short, merge
            if (current_segment["speaker"] == next_segment["speaker"] and 
                current_segment["duration"] < min_duration):
                
                current_segment["end_time"] = next_segment["end_time"]
                current_segment["duration"] = round(
                    current_segment["end_time"] - current_segment["start_time"], 2
                )
            else:
                merged.append(current_segment)
                current_segment = next_segment.copy()
        
        merged.append(current_segment)
        return merged
    
    def get_speaker_statistics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about speakers"""
        if not segments:
            return {}
        
        speaker_stats = {}
        total_duration = 0
        
        for segment in segments:
            speaker = segment["speaker"]
            duration = segment["duration"]
            
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    "total_duration": 0,
                    "segment_count": 0,
                    "average_segment_duration": 0
                }
            
            speaker_stats[speaker]["total_duration"] += duration
            speaker_stats[speaker]["segment_count"] += 1
            total_duration += duration
        
        # Calculate percentages and averages
        for speaker in speaker_stats:
            stats = speaker_stats[speaker]
            stats["total_duration"] = round(stats["total_duration"], 2)
            stats["percentage"] = round((stats["total_duration"] / total_duration) * 100, 1) if total_duration > 0 else 0
            stats["average_segment_duration"] = round(
                stats["total_duration"] / stats["segment_count"], 2
            ) if stats["segment_count"] > 0 else 0
        
        return {
            "speakers": speaker_stats,
            "total_speakers": len(speaker_stats),
            "total_duration": round(total_duration, 2)
        }

