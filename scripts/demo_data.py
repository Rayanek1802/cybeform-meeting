#!/usr/bin/env python3
"""
Script to create demo data for CybeMeeting MVP
Creates sample projects and meetings for testing and demonstration
"""
import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Change to backend directory for imports
os.chdir(backend_path)

from app.core.config import settings


def create_demo_data():
    """Create demo projects and meetings"""
    
    # Ensure data directory exists
    data_dir = Path(settings.DATA_PATH)
    projects_dir = data_dir / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    print("🏗️  Création des données de démonstration...")
    
    # Demo projects
    demo_projects = [
        {
            "name": "Rénovation Immeuble Haussman",
            "meetings": [
                {
                    "title": "Réunion de lancement projet",
                    "expected_speakers": 4,
                    "status": "Terminé",
                    "duration": 1800,  # 30 minutes
                    "participants_detected": ["Chef de projet", "Architecte", "Maître d'ouvrage", "Coordinateur BTP"]
                },
                {
                    "title": "Point sécurité chantier",
                    "expected_speakers": 3,
                    "status": "Terminé", 
                    "duration": 900,   # 15 minutes
                    "participants_detected": ["Responsable sécurité", "Chef de chantier", "Coordinateur SPS"]
                }
            ]
        },
        {
            "name": "Construction Centre Commercial",
            "meetings": [
                {
                    "title": "Réunion planning phase 1",
                    "expected_speakers": 5,
                    "status": "En attente",
                    "duration": None,
                    "participants_detected": []
                }
            ]
        },
        {
            "name": "Réhabilitation Pont Métallique",
            "meetings": [
                {
                    "title": "Diagnostic structure existante",
                    "expected_speakers": 3,
                    "status": "En cours de traitement",
                    "duration": 2400,  # 40 minutes
                    "participants_detected": ["Ingénieur structure", "Expert matériaux", "Géomètre"]
                }
            ]
        }
    ]
    
    created_projects = []
    
    for project_data in demo_projects:
        # Create project
        project_id = str(uuid.uuid4())
        project_dir = projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Create meetings directory
        meetings_dir = project_dir / "meetings"
        meetings_dir.mkdir(exist_ok=True)
        
        # Create project metadata
        project = {
            "id": project_id,
            "name": project_data["name"],
            "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
            "meetings": []
        }
        
        # Create meetings
        for i, meeting_data in enumerate(project_data["meetings"]):
            meeting_id = str(uuid.uuid4())
            meeting_dir = meetings_dir / meeting_id
            meeting_dir.mkdir(exist_ok=True)
            
            # Create meeting metadata
            meeting = {
                "id": meeting_id,
                "title": meeting_data["title"],
                "date": (datetime.now() - timedelta(days=20-i*5)).isoformat(),
                "expected_speakers": meeting_data["expected_speakers"],
                "status": meeting_data["status"],
                "progress": 100 if meeting_data["status"] == "Terminé" else 45 if meeting_data["status"] == "En cours de traitement" else 0,
                "duration": meeting_data["duration"],
                "participants_detected": meeting_data["participants_detected"],
                "audio_file": "demo_audio.wav" if meeting_data["status"] != "En attente" else None,
                "report_file": "report.docx" if meeting_data["status"] == "Terminé" else None,
                "created_at": (datetime.now() - timedelta(days=20-i*5)).isoformat()
            }
            
            # Save meeting
            meeting_file = meeting_dir / "meeting.json"
            with open(meeting_file, "w", encoding="utf-8") as f:
                json.dump(meeting, f, ensure_ascii=False, indent=2)
            
            # Create demo analysis for completed meetings
            if meeting_data["status"] == "Terminé":
                create_demo_analysis(meeting_dir, meeting_data, project_data["name"])
            
            # Create demo status for processing meetings
            if meeting_data["status"] == "En cours de traitement":
                create_demo_status(meeting_dir)
            
            project["meetings"].append(meeting)
        
        # Save project
        project_file = project_dir / "project.json"
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        created_projects.append(project)
        print(f"✅ Projet créé: {project_data['name']} ({len(project_data['meetings'])} meetings)")
    
    print(f"\n🎉 {len(created_projects)} projets de démonstration créés avec succès!")
    print(f"📁 Données sauvegardées dans: {data_dir}")
    print("\n🚀 Vous pouvez maintenant démarrer l'application avec: docker compose up")


def create_demo_analysis(meeting_dir, meeting_data, project_name):
    """Create demo analysis data for a meeting"""
    
    # Sample analysis based on meeting type
    if "lancement" in meeting_data["title"].lower():
        analysis = {
            "meta": {
                "projectName": project_name,
                "meetingTitle": meeting_data["title"],
                "meetingDate": datetime.now().strftime("%Y-%m-%d"),
                "duration": meeting_data["duration"] // 60,
                "participantsDetected": meeting_data["participants_detected"]
            },
            "objectifs": [
                "Lancer officiellement le projet de rénovation",
                "Définir les rôles et responsabilités de chaque intervenant",
                "Établir le planning général des travaux",
                "Valider les contraintes techniques et réglementaires"
            ],
            "problemes": [
                "Délai serré pour obtention du permis de construire",
                "Accès difficile au chantier en centre-ville",
                "Nécessité de maintenir l'activité dans une partie du bâtiment"
            ],
            "decisions": [
                "Validation du planning en 3 phases distinctes",
                "Mise en place d'une coordination hebdomadaire",
                "Engagement d'un coordinateur SPS dédié",
                "Utilisation de matériaux éco-responsables"
            ],
            "actions": [
                {"tache": "Déposer la demande de permis de construire", "responsable": "Architecte", "echeance": "Dans 2 semaines"},
                {"tache": "Établir le plan de sécurité détaillé", "responsable": "Coordinateur SPS", "echeance": "Avant démarrage travaux"},
                {"tache": "Organiser réunion avec riverains", "responsable": "Maître d'ouvrage", "echeance": "Semaine prochaine"},
                {"tache": "Finaliser étude géotechnique", "responsable": "Bureau d'études", "echeance": "Fin du mois"}
            ],
            "risques": [
                {"risque": "Retard dans l'obtention des autorisations", "impact": "Décalage planning de 4-6 semaines", "mitigation": "Anticiper les démarches et prévoir solutions alternatives"},
                {"risque": "Découverte d'amiante dans structure existante", "impact": "Surcoût et délai supplémentaire", "mitigation": "Diagnostic amiante complémentaire avant travaux"},
                {"risque": "Conditions météo défavorables", "impact": "Ralentissement des travaux extérieurs", "mitigation": "Planifier travaux intérieurs en priorité"}
            ],
            "pointsTechniquesBTP": [
                "Renforcement de la structure porteuse par micro-pieux",
                "Isolation thermique par l'extérieur (ITE) avec finition enduit",
                "Remplacement intégral des menuiseries par du double vitrage",
                "Mise aux normes électriques et installation VMC double flux",
                "Étanchéité toiture-terrasse avec végétalisation extensive"
            ],
            "planning": [
                "Phase 1: Gros œuvre et structure (3 mois)",
                "Phase 2: Corps d'état secondaires (4 mois)", 
                "Phase 3: Finitions et aménagements (2 mois)",
                "Réception provisoire prévue en septembre",
                "Période de parfait achèvement: 1 an"
            ],
            "budget_chiffrage": [
                "Enveloppe totale: 850 000€ HT",
                "Gros œuvre: 350 000€ HT (41%)",
                "Second œuvre: 400 000€ HT (47%)",
                "Aménagements: 100 000€ HT (12%)",
                "Provision pour aléas: 5% du montant total"
            ],
            "divers": [
                "Coordination avec services urbains pour occupation voirie",
                "Mise en place d'une signalétique chantier adaptée",
                "Communication régulière avec copropriété",
                "Suivi qualité par bureau de contrôle agréé"
            ],
            "exclusions": [
                "Discussions sur le choix du restaurant pour le pot de fin de chantier",
                "Anecdotes personnelles des intervenants",
                "Commentaires sur la météo du jour"
            ],
            "fullTranscriptRef": "transcript.json"
        }
    elif "sécurité" in meeting_data["title"].lower():
        analysis = {
            "meta": {
                "projectName": project_name,
                "meetingTitle": meeting_data["title"],
                "meetingDate": datetime.now().strftime("%Y-%m-%d"),
                "duration": meeting_data["duration"] // 60,
                "participantsDetected": meeting_data["participants_detected"]
            },
            "objectifs": [
                "Faire le point sur les mesures de sécurité en place",
                "Identifier les risques spécifiques à la phase en cours",
                "Vérifier la conformité des équipements de protection",
                "Planifier les formations sécurité nécessaires"
            ],
            "problemes": [
                "Signalisation temporaire insuffisante aux abords du chantier",
                "Quelques EPI non conformes détectés",
                "Zone de stockage matériaux mal délimitée"
            ],
            "decisions": [
                "Renforcement immédiat de la signalisation",
                "Remplacement des EPI défaillants sous 48h",
                "Mise en place d'un périmètre sécurisé pour stockage",
                "Formation recyclage pour 3 ouvriers"
            ],
            "actions": [
                {"tache": "Commander nouveaux panneaux de signalisation", "responsable": "Chef de chantier", "echeance": "Aujourd'hui"},
                {"tache": "Remplacer EPI défaillants", "responsable": "Responsable sécurité", "echeance": "48h"},
                {"tache": "Organiser session formation sécurité", "responsable": "Coordinateur SPS", "echeance": "Semaine prochaine"},
                {"tache": "Délimiter zone stockage", "responsable": "Chef de chantier", "echeance": "Demain"}
            ],
            "risques": [
                {"risque": "Chute de hauteur lors travaux en façade", "impact": "Accident grave potentiel", "mitigation": "Vérification systématique harnais et lignes de vie"},
                {"risque": "Circulation piétons à proximité grue", "impact": "Risque d'accident avec tiers", "mitigation": "Balisage renforcé et signaleur"},
                {"risque": "Manutention manuelle charges lourdes", "impact": "TMS ouvriers", "mitigation": "Utilisation systématique d'équipements de levage"}
            ],
            "pointsTechniquesBTP": [
                "Installation échafaudages de façade conformes NF P93-350",
                "Mise en place garde-corps périphériques 1,10m minimum",
                "Vérification mensuelle des équipements de levage",
                "Contrôle quotidien des lignes de vie temporaires",
                "Zone de repli sécurisée en cas d'intempéries"
            ],
            "planning": [
                "Inspection sécurité hebdomadaire tous les mardis 8h",
                "Formation nouveau arrivant obligatoire J+1",
                "Contrôle APAVE prévu fin de semaine",
                "Exercice évacuation planifié mois prochain"
            ],
            "budget_chiffrage": [
                "Coût EPI additionnels: 1 200€",
                "Formation sécurité: 800€",
                "Signalisation renforcée: 600€",
                "Total mesures correctives: 2 600€"
            ],
            "divers": [
                "Bonne implication générale des équipes",
                "Météo favorable pour travaux extérieurs",
                "Livraison matériaux respectée"
            ],
            "exclusions": [
                "Discussion sur match de football",
                "Commentaires sur embouteillages matinaux"
            ],
            "fullTranscriptRef": "transcript.json"
        }
    else:
        # Generic analysis
        analysis = {
            "meta": {
                "projectName": project_name,
                "meetingTitle": meeting_data["title"],
                "meetingDate": datetime.now().strftime("%Y-%m-%d"),
                "duration": meeting_data["duration"] // 60,
                "participantsDetected": meeting_data["participants_detected"]
            },
            "objectifs": [
                "Point d'avancement du projet",
                "Validation des étapes franchies",
                "Identification des points de vigilance"
            ],
            "problemes": [
                "Léger retard sur certaines tâches",
                "Coordination à améliorer entre corps d'état"
            ],
            "decisions": [
                "Réajustement du planning",
                "Mise en place de points quotidiens"
            ],
            "actions": [
                {"tache": "Mettre à jour le planning", "responsable": "Chef de projet", "echeance": "Cette semaine"},
                {"tache": "Organiser réunion coordination", "responsable": "Coordinateur", "echeance": "Demain"}
            ],
            "risques": [
                {"risque": "Retard livraison matériaux", "impact": "Décalage planning", "mitigation": "Anticiper les commandes"}
            ],
            "pointsTechniquesBTP": [
                "Avancement conforme aux spécifications techniques",
                "Contrôle qualité en cours"
            ],
            "planning": [
                "Respect du planning général",
                "Quelques ajustements nécessaires"
            ],
            "budget_chiffrage": [
                "Budget maîtrisé à ce stade"
            ],
            "divers": [
                "Bonne coordination générale",
                "Conditions de travail satisfaisantes"
            ],
            "exclusions": [],
            "fullTranscriptRef": "transcript.json"
        }
    
    # Save analysis
    analysis_file = meeting_dir / "analysis.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # Create demo transcript
    create_demo_transcript(meeting_dir, meeting_data)


def create_demo_transcript(meeting_dir, meeting_data):
    """Create demo transcript data"""
    
    # Sample transcript segments
    if "lancement" in meeting_data["title"].lower():
        segments = [
            {"speaker": "Chef de projet", "start_time": 0, "end_time": 45, "text": "Bonjour à tous, merci d'être présents pour cette réunion de lancement du projet de rénovation de l'immeuble Haussman. Nous allons passer en revue les objectifs, le planning et les responsabilités de chacun."},
            {"speaker": "Maître d'ouvrage", "start_time": 45, "end_time": 78, "text": "Merci. L'objectif principal est de moderniser complètement ce bâtiment tout en respectant son caractère architectural. Nous avons un budget de 850 000 euros et un délai de 9 mois."},
            {"speaker": "Architecte", "start_time": 78, "end_time": 120, "text": "J'ai finalisé les plans. Nous devons obtenir le permis de construire rapidement. Il y a quelques contraintes liées aux Bâtiments de France qu'il faut intégrer."},
            {"speaker": "Coordinateur BTP", "start_time": 120, "end_time": 165, "text": "Pour la coordination, je propose des réunions hebdomadaires. Il faut aussi prévoir l'impact sur le voisinage et la circulation. L'accès au chantier sera compliqué."},
            {"speaker": "Chef de projet", "start_time": 165, "end_time": 200, "text": "Très bien. Nous allons procéder en 3 phases distinctes. La première phase concerne le gros œuvre, ensuite les corps d'état secondaires, et enfin les finitions."}
        ]
    elif "sécurité" in meeting_data["title"].lower():
        segments = [
            {"speaker": "Responsable sécurité", "start_time": 0, "end_time": 30, "text": "Bonjour, faisons le point sur les mesures de sécurité. J'ai identifié quelques points à améliorer lors de ma visite hier."},
            {"speaker": "Chef de chantier", "start_time": 30, "end_time": 55, "text": "Oui, on a eu quelques soucis avec la signalisation. Les panneaux ont été endommagés par le vent. Il faut les remplacer rapidement."},
            {"speaker": "Coordinateur SPS", "start_time": 55, "end_time": 85, "text": "J'ai aussi remarqué que certains EPI n'étaient pas conformes. Il faut faire le point sur les équipements de chaque ouvrier."},
            {"speaker": "Responsable sécurité", "start_time": 85, "end_time": 120, "text": "Exactement. Je propose qu'on organise une formation de recyclage pour rappeler les consignes. La sécurité est la priorité absolue."},
            {"speaker": "Chef de chantier", "start_time": 120, "end_time": 145, "text": "D'accord. Je vais commander les nouveaux panneaux dès aujourd'hui et on délimitera mieux la zone de stockage des matériaux."}
        ]
    else:
        segments = [
            {"speaker": "Participant 1", "start_time": 0, "end_time": 30, "text": "Bonjour, commençons par faire le point sur l'avancement du projet."},
            {"speaker": "Participant 2", "start_time": 30, "end_time": 60, "text": "Nous avons respecté globalement le planning, avec quelques ajustements mineurs à prévoir."},
            {"speaker": "Participant 3", "start_time": 60, "end_time": 90, "text": "Il y a eu un léger retard sur la livraison des matériaux, mais cela reste gérable."},
            {"speaker": "Participant 1", "start_time": 90, "end_time": 120, "text": "Très bien, mettons en place des points quotidiens pour améliorer la coordination."}
        ]
    
    transcript = {
        "full_text": " ".join([seg["text"] for seg in segments]),
        "language": "fr",
        "segments": segments,
        "service": "demo"
    }
    
    # Save transcript
    transcript_file = meeting_dir / "transcript.json"
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)


def create_demo_status(meeting_dir):
    """Create demo status for processing meeting"""
    status = {
        "stage": "transcription",
        "progress": 65,
        "message": "Transcription en cours...",
        "estimated_time_remaining": 180,
        "updated_at": datetime.now().isoformat()
    }
    
    status_file = meeting_dir / "status.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    create_demo_data()
