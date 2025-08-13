"""
Tests for the analysis service
"""
import pytest
import json
from app.services.analysis_service import AnalysisService


def test_validate_and_clean_analysis():
    """Test analysis data validation and cleaning"""
    service = AnalysisService()
    
    # Test with incomplete data
    incomplete_data = {
        "objectifs": ["Objectif 1"],
        "actions": [
            {"tache": "Test action", "responsable": "John"},
            {"invalid": "data"}  # Invalid action
        ]
    }
    
    cleaned = service._validate_and_clean_analysis(incomplete_data)
    
    # Should have all required fields
    assert "meta" in cleaned
    assert "objectifs" in cleaned
    assert "actions" in cleaned
    assert "risques" in cleaned
    
    # Should filter out invalid actions
    assert len(cleaned["actions"]) == 1
    assert cleaned["actions"][0]["tache"] == "Test action"
    assert cleaned["actions"][0]["responsable"] == "John"


def test_create_fallback_analysis():
    """Test fallback analysis creation"""
    service = AnalysisService()
    
    transcript_segments = [
        {"speaker": "SPEAKER_0", "text": "Hello world", "start_time": 0, "end_time": 5},
        {"speaker": "SPEAKER_1", "text": "How are you?", "start_time": 5, "end_time": 10}
    ]
    
    meeting_metadata = {
        "title": "Test Meeting",
        "project_name": "Test Project"
    }
    
    fallback = service._create_fallback_analysis(transcript_segments, meeting_metadata)
    
    # Should have basic structure
    assert fallback["meta"]["meetingTitle"] == "Test Meeting"
    assert fallback["meta"]["projectName"] == "Test Project"
    assert len(fallback["meta"]["participantsDetected"]) == 2
    
    # Should have fallback content
    assert len(fallback["objectifs"]) > 0
    assert len(fallback["actions"]) > 0
    assert len(fallback["divers"]) > 0


def test_format_transcript_for_analysis():
    """Test transcript formatting"""
    service = AnalysisService()
    
    segments = [
        {"speaker": "SPEAKER_0", "text": "Bonjour", "start_time": 0},
        {"speaker": "SPEAKER_1", "text": "Comment allez-vous?", "start_time": 65}
    ]
    
    formatted = service._format_transcript_for_analysis(segments)
    
    assert "[00:00] SPEAKER_0: Bonjour" in formatted
    assert "[01:05] SPEAKER_1: Comment allez-vous?" in formatted

