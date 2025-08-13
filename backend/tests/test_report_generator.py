"""
Tests for the report generator
"""
import pytest
import tempfile
import os
from app.services.report_generator import ReportGenerator


def test_generate_html_preview():
    """Test HTML preview generation"""
    generator = ReportGenerator()
    
    analysis_data = {
        "meta": {
            "projectName": "Test Project",
            "meetingTitle": "Test Meeting",
            "meetingDate": "2024-01-01",
            "duration": 60,
            "participantsDetected": ["SPEAKER_0", "SPEAKER_1"]
        },
        "objectifs": ["Objectif 1", "Objectif 2"],
        "decisions": ["Décision 1"],
        "actions": [
            {"tache": "Action 1", "responsable": "John", "echeance": "2024-01-15"}
        ],
        "risques": [
            {"risque": "Risque 1", "impact": "Impact 1", "mitigation": "Mitigation 1"}
        ],
        "pointsTechniquesBTP": ["Point technique 1"],
        "planning": ["Jalon 1"],
        "budget_chiffrage": ["Budget 1"],
        "divers": ["Info 1"],
        "exclusions": ["Exclusion 1"]
    }
    
    meeting_data = {
        "project_name": "Test Project",
        "title": "Test Meeting"
    }
    
    html = generator.generate_html_preview(analysis_data, meeting_data)
    
    # Should contain expected content
    assert "CybeMeeting" in html
    assert "Test Project" in html
    assert "Test Meeting" in html
    assert "Objectif 1" in html
    assert "Action 1" in html
    assert "John" in html


def test_generate_report():
    """Test Word report generation"""
    generator = ReportGenerator()
    
    analysis_data = {
        "meta": {
            "projectName": "Test Project",
            "meetingTitle": "Test Meeting",
            "meetingDate": "2024-01-01",
            "duration": 60,
            "participantsDetected": ["SPEAKER_0", "SPEAKER_1"]
        },
        "objectifs": ["Objectif test"],
        "problemes": ["Problème test"],
        "decisions": ["Décision test"],
        "actions": [
            {"tache": "Action test", "responsable": "John Doe", "echeance": "2024-01-15"}
        ],
        "risques": [
            {"risque": "Risque test", "impact": "Impact test", "mitigation": "Mitigation test"}
        ],
        "pointsTechniquesBTP": ["Point technique test"],
        "planning": ["Jalon test"],
        "budget_chiffrage": ["Budget test"],
        "divers": ["Info test"],
        "exclusions": ["Exclusion test"]
    }
    
    transcript_segments = [
        {"speaker": "SPEAKER_0", "text": "Bonjour tout le monde", "start_time": 0, "end_time": 5},
        {"speaker": "SPEAKER_1", "text": "Comment allez-vous?", "start_time": 5, "end_time": 10}
    ]
    
    meeting_metadata = {
        "project_name": "Test Project",
        "title": "Test Meeting"
    }
    
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
        success = generator.generate_report(
            analysis_data, 
            transcript_segments, 
            meeting_metadata, 
            tmp.name
        )
        
        assert success
        assert os.path.exists(tmp.name)
        assert os.path.getsize(tmp.name) > 0
        
        # Cleanup
        os.unlink(tmp.name)

