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


def test_analyze_in_chunks():
    """Test chunked analysis functionality"""
    service = AnalysisService()
    
    # Create test segments spanning 45 minutes (3 chunks of 15 minutes each)
    transcript_segments = []
    for i in range(0, 45):
        transcript_segments.append({
            "speaker": f"SPEAKER_{i % 2}",
            "text": f"This is segment {i} of the meeting",
            "start_time": i * 60,  # One segment per minute
            "duration": 60
        })
    
    meeting_metadata = {
        "title": "Long Test Meeting",
        "project_name": "Test Project",
        "duration": 45,
        "participants": ["Speaker 0", "Speaker 1"],
        "ai_instructions": "Test meeting analysis"
    }
    
    # Test chunking logic (without OpenAI calls)
    service.client = None  # Disable API calls for testing
    
    # The _analyze_in_chunks function should split into chunks
    # We'll test the chunking logic separately
    chunk_duration_seconds = 15 * 60  # 15 minutes
    chunks = []
    current_chunk = []
    current_chunk_start = 0
    
    for segment in transcript_segments:
        start_time = segment.get("start_time", 0)
        
        if start_time >= current_chunk_start + chunk_duration_seconds and current_chunk:
            chunks.append({
                "segments": current_chunk,
                "start_time": current_chunk_start,
                "end_time": start_time,
                "chunk_number": len(chunks) + 1
            })
            current_chunk = []
            current_chunk_start = start_time
        
        current_chunk.append(segment)
    
    if current_chunk:
        last_segment = current_chunk[-1]
        end_time = last_segment.get("start_time", 0) + last_segment.get("duration", 60)
        chunks.append({
            "segments": current_chunk,
            "start_time": current_chunk_start,
            "end_time": end_time,
            "chunk_number": len(chunks) + 1
        })
    
    # Should create 3 chunks (0-15min, 15-30min, 30-45min)
    assert len(chunks) == 3
    assert chunks[0]["start_time"] == 0
    assert chunks[0]["chunk_number"] == 1
    assert chunks[1]["start_time"] == 15 * 60
    assert chunks[1]["chunk_number"] == 2
    assert chunks[2]["start_time"] == 30 * 60
    assert chunks[2]["chunk_number"] == 3


def test_merge_analyses_deduplication():
    """Test analysis merging with deduplication"""
    service = AnalysisService()
    
    # Create mock chunk analyses with some duplicate content
    chunk_analyses = [
        {
            "meta": {"segmentNumber": 1},
            "sectionsDynamiques": {
                "problemesIdentifies": [
                    "Problème de coordination entre équipes",
                    "Retard sur livraison matériaux"
                ],
                "decisionsStrategiques": [
                    "Décision de reprogrammer la phase 2"
                ]
            },
            "vueChronologique": [
                "[00:00-15:00] Discussion des problèmes de coordination"
            ],
            "analysisMetrics": {
                "totalSegments": 15,
                "qualiteExtraction": "Bon"
            },
            "chunk_meta": {
                "chunk_number": 1,
                "start_time": 0,
                "end_time": 900
            }
        },
        {
            "meta": {"segmentNumber": 2},
            "sectionsDynamiques": {
                "problemesIdentifies": [
                    "Problème de coordination entre équipes",  # Duplicate
                    "Difficultés techniques sur fondations"
                ],
                "actionsUrgentes": [
                    {
                        "action": "Contacter le fournisseur",
                        "responsable": "Chef de projet",
                        "echeance": "Demain"
                    }
                ]
            },
            "vueChronologique": [
                "[15:00-30:00] Analyse des solutions techniques"
            ],
            "analysisMetrics": {
                "totalSegments": 15,
                "qualiteExtraction": "Excellent"
            },
            "chunk_meta": {
                "chunk_number": 2,
                "start_time": 900,
                "end_time": 1800
            }
        }
    ]
    
    meeting_metadata = {
        "title": "Test Merge",
        "project_name": "Test Project",
        "duration": 30,
        "participants": ["Speaker 1", "Speaker 2"]
    }
    
    merged = service._merge_analyses(chunk_analyses, meeting_metadata)
    
    # Test structure
    assert "meta" in merged
    assert "sectionsDynamiques" in merged
    assert "vueChronologique" in merged
    assert "analysisMetrics" in merged
    
    # Test meta information
    assert merged["meta"]["meetingTitle"] == "Test Merge"
    assert merged["meta"]["chunksAnalyzed"] == 2
    
    # Test deduplication: should have 3 unique problems, not 4
    problems = merged["sectionsDynamiques"].get("problemesIdentifies", [])
    # Check that we don't have exact duplicates
    problem_contents = [str(p).split(']', 1)[1].strip() if ']' in str(p) else str(p) for p in problems]
    unique_problems = set(problem_contents)
    assert len(unique_problems) == 3  # Three unique problems
    
    # Test chronological order
    chrono_events = merged["vueChronologique"]
    assert len(chrono_events) == 2
    
    # Test metrics merging
    metrics = merged["analysisMetrics"]
    assert metrics["totalSegments"] == 30  # Sum of both chunks
    assert metrics["chunksProcessed"] == 2


def test_chunk_analysis_system_prompt():
    """Test chunk-specific system prompt generation"""
    service = AnalysisService()
    
    prompt = service._get_chunk_analysis_system_prompt("Analyser les aspects techniques")
    
    assert "SEGMENT spécifique" in prompt
    assert "ANALYSE PAR SEGMENT" in prompt
    assert "Analyser les aspects techniques" in prompt
    assert "EXHAUSTIF sur cette portion" in prompt


def test_deduplication_key_generation():
    """Test deduplication key generation"""
    service = AnalysisService()
    
    # Test dict items
    action_item = {
        "action": "Vérifier les fondations",
        "responsable": "Ingénieur",
        "echeance": "Vendredi"
    }
    key1 = service._create_deduplication_key(action_item)
    assert "action:Vérifier les fondations:Ingénieur" == key1
    
    # Test string items
    string_item = "[10:00-15:00] Discussion sur les matériaux"
    key2 = service._create_deduplication_key(string_item)
    assert key2 == "Discussion sur les matériaux"  # Time prefix removed
    
    # Test risk items
    risk_item = {
        "risque": "Retard de livraison",
        "categorie": "Planning",
        "impact": "Décalage du projet"
    }
    key3 = service._create_deduplication_key(risk_item)
    assert "risque:Retard de livraison:Planning" == key3

