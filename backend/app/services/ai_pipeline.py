"""
Main AI processing pipeline for CybeMeeting
"""
import os
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.services.file_manager import FileManager
from app.services.audio_processor import AudioProcessor
from app.services.diarization_service import DiarizationService
from app.services.transcription_service import TranscriptionService
from app.services.analysis_service import AnalysisService
from app.services.report_generator import ReportGenerator
from app.models.schemas import ProcessingStage, MeetingStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIPipeline:
    """Main AI processing pipeline"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.audio_processor = AudioProcessor()
        self.diarization_service = DiarizationService()
        self.transcription_service = TranscriptionService()
        self.analysis_service = AnalysisService()
        self.report_generator = ReportGenerator()
    
    async def process_meeting(self, project_id: str, meeting_id: str, expected_speakers: int = 2, user_id: str = None):
        """
        Main processing pipeline for a meeting
        """
        try:
            logger.info(f"Starting processing for meeting {meeting_id}")
            
            # Store user_id for use in other methods
            self.current_user_id = user_id
            
            # Use user-specific path if user_id provided, otherwise fallback to old structure
            if user_id:
                meeting_dir = os.path.join(settings.DATA_PATH, "users", user_id, "projects", project_id, "meetings", meeting_id)
            else:
                meeting_dir = self.file_manager.get_meeting_path(project_id, meeting_id)
            
            # Load meeting metadata
            meeting_file = os.path.join(meeting_dir, "meeting.json")
            with open(meeting_file, "r", encoding="utf-8") as f:
                meeting_data = json.load(f)
            
            audio_file = meeting_data.get("audio_file")
            if not audio_file:
                raise Exception("No audio file found")
            
            audio_path = os.path.join(meeting_dir, audio_file)
            
            # Update status: Starting
            self._update_status(project_id, meeting_id, ProcessingStage.UPLOAD, 5, "Initialisation du traitement...")
            
            # Step 1: Audio normalization
            self._update_status(project_id, meeting_id, ProcessingStage.UPLOAD, 10, "Normalisation de l'audio...")
            normalized_audio = self.audio_processor.prepare_for_processing(audio_path, meeting_dir)
            
            if not normalized_audio:
                raise Exception("Audio normalization failed")
            
            # Step 2: Speaker diarization
            self._update_status(project_id, meeting_id, ProcessingStage.DIARIZATION, 20, "Détection des intervenants...")
            diarization_segments = self.diarization_service.diarize_audio(
                normalized_audio, 
                expected_speakers
            )
            
            if not diarization_segments:
                raise Exception("Diarization failed")
            
            # Save diarization results
            diarization_file = os.path.join(meeting_dir, "diarization.json")
            self.file_manager.save_json({
                "segments": diarization_segments,
                "statistics": self.diarization_service.get_speaker_statistics(diarization_segments)
            }, diarization_file)
            
            self._update_status(project_id, meeting_id, ProcessingStage.DIARIZATION, 40, f"Détection terminée: {len(set(s['speaker'] for s in diarization_segments))} intervenants")
            
            # Step 3: Transcription
            self._update_status(project_id, meeting_id, ProcessingStage.TRANSCRIPTION, 50, "Transcription en cours...")
            transcription_result = self.transcription_service.transcribe_audio(normalized_audio)
            
            # Align transcription with diarization
            aligned_segments = self.transcription_service.align_transcription_with_diarization(
                transcription_result, diarization_segments
            )
            
            # Save transcription results
            transcript_file = os.path.join(meeting_dir, "transcript.json")
            self.file_manager.save_json({
                "full_text": transcription_result.get("text", ""),
                "language": transcription_result.get("language", "fr"),
                "segments": aligned_segments,
                "service": transcription_result.get("service", "unknown")
            }, transcript_file)
            
            self._update_status(project_id, meeting_id, ProcessingStage.TRANSCRIPTION, 70, "Transcription terminée")
            
            # Step 4: AI Analysis
            self._update_status(project_id, meeting_id, ProcessingStage.REPORT, 80, "Analyse IA en cours...")
            
            # Prepare metadata for analysis
            detected_participants = list(set([seg["speaker"] for seg in aligned_segments]))
            analysis_metadata = {
                "project_name": meeting_data.get("project_name", "Projet BTP"),
                "title": meeting_data.get("title", "Réunion"),
                "ai_instructions": meeting_data.get("ai_instructions", ""),
                "date": meeting_data.get("date", ""),
                "duration": meeting_data.get("duration", 0),
                "expected_speakers": meeting_data.get("expected_speakers", expected_speakers),
                "participants": detected_participants
            }
            
            analysis_result = self.analysis_service.analyze_meeting(
                aligned_segments, analysis_metadata
            )
            
            # Save analysis results
            analysis_file = os.path.join(meeting_dir, "analysis.json")
            self.file_manager.save_json(analysis_result, analysis_file)
            
            # Step 5: Generate Word report
            self._update_status(project_id, meeting_id, ProcessingStage.REPORT, 90, "Génération du rapport Word...")
            
            report_path = os.path.join(meeting_dir, "report.docx")
            report_generated = self.report_generator.generate_report(
                analysis_result, aligned_segments, analysis_metadata, report_path
            )
            
            if not report_generated:
                logger.warning("Report generation failed, but continuing...")
            
            # Step 6: Update meeting metadata
            meeting_data["status"] = MeetingStatus.COMPLETED.value
            meeting_data["progress"] = 100
            meeting_data["participants_detected"] = analysis_metadata["participants"]
            meeting_data["report_file"] = "report.docx" if report_generated else None
            meeting_data["processed_at"] = datetime.now().isoformat()
            
            with open(meeting_file, "w", encoding="utf-8") as f:
                json.dump(meeting_data, f, ensure_ascii=False, indent=2)
            
            # Step 7: Update project.json with the updated meeting status
            if user_id:
                project_file = os.path.join(settings.DATA_PATH, "users", user_id, "projects", project_id, "project.json")
            else:
                project_file = os.path.join(settings.DATA_PATH, "projects", project_id, "project.json")
            if os.path.exists(project_file):
                with open(project_file, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                
                # Find and update the meeting in the project's meetings list
                for i, project_meeting in enumerate(project_data["meetings"]):
                    if project_meeting["id"] == meeting_id:
                        project_data["meetings"][i] = meeting_data
                        break
                
                with open(project_file, "w", encoding="utf-8") as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            # Final status update
            self._update_status(project_id, meeting_id, ProcessingStage.DONE, 100, "Traitement terminé avec succès")
            
            logger.info(f"Processing completed successfully for meeting {meeting_id}")
            
        except Exception as e:
            logger.error(f"Processing failed for meeting {meeting_id}: {e}")
            
            # Update error status
            self._update_status(project_id, meeting_id, ProcessingStage.ERROR, 0, f"Erreur: {str(e)}")
            
            # Update meeting status
            try:
                meeting_file = os.path.join(meeting_dir, "meeting.json")
                with open(meeting_file, "r", encoding="utf-8") as f:
                    meeting_data = json.load(f)
                
                meeting_data["status"] = MeetingStatus.ERROR.value
                meeting_data["error"] = str(e)
                
                with open(meeting_file, "w", encoding="utf-8") as f:
                    json.dump(meeting_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    
    def _update_status(self, project_id: str, meeting_id: str, stage: ProcessingStage, 
                      progress: int, message: str):
        """Update processing status"""
        try:
            # Estimate remaining time based on stage and progress
            time_estimates = {
                ProcessingStage.UPLOAD: 30,
                ProcessingStage.DIARIZATION: 60,
                ProcessingStage.TRANSCRIPTION: 90,
                ProcessingStage.REPORT: 30,
                ProcessingStage.DONE: 0,
                ProcessingStage.ERROR: 0
            }
            
            estimated_time = time_estimates.get(stage, 0)
            if progress > 0:
                estimated_time = int(estimated_time * (100 - progress) / 100)
            
            status_data = {
                "stage": stage.value,
                "progress": progress,
                "message": message,
                "estimated_time_remaining": estimated_time if stage != ProcessingStage.DONE else None
            }
            
            # Use new structure if user_id available
            if hasattr(self, 'current_user_id') and self.current_user_id:
                meeting_dir = os.path.join(settings.DATA_PATH, "users", self.current_user_id, "projects", project_id, "meetings", meeting_id)
                status_file = os.path.join(meeting_dir, "status.json")
                
                # Add timestamp
                status_data["updated_at"] = datetime.now().isoformat()
                
                os.makedirs(meeting_dir, exist_ok=True)
                with open(status_file, "w", encoding="utf-8") as f:
                    json.dump(status_data, f, ensure_ascii=False, indent=2)
            else:
                self.file_manager.update_meeting_status(project_id, meeting_id, status_data)
            logger.info(f"Status updated - {stage.value}: {progress}% - {message}")
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def generate_html_preview(self, analysis_data: Dict[str, Any], meeting_data: Dict[str, Any]) -> str:
        """Generate HTML preview of the report"""
        return self.report_generator.generate_html_preview(analysis_data, meeting_data)
