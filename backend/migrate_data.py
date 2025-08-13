#!/usr/bin/env python
"""
Script pour migrer les données existantes vers la base de données PostgreSQL
À utiliser si vous avez déjà des données en local
"""
import os
import json
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import Base, User, Project, Meeting
from app.services.auth_service_db import AuthServiceDB

def migrate_users(session, users_file="./data/users.json"):
    """Migrer les utilisateurs depuis le fichier JSON"""
    if not os.path.exists(users_file):
        print("❌ Pas de fichier users.json trouvé")
        return
    
    print("📥 Migration des utilisateurs...")
    
    with open(users_file, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    for user_id, user_info in users_data.items():
        # Vérifier si l'utilisateur existe déjà
        existing = session.query(User).filter(User.email == user_info['email']).first()
        if existing:
            print(f"⏭️  Utilisateur {user_info['email']} existe déjà")
            continue
        
        # Créer le nouvel utilisateur
        user = User(
            id=user_id,
            email=user_info['email'],
            password_hash=user_info['password_hash'],
            first_name=user_info.get('first_name', ''),
            last_name=user_info.get('last_name', ''),
            company=user_info.get('company', ''),
            created_at=datetime.fromisoformat(user_info['created_at']) if 'created_at' in user_info else datetime.utcnow(),
            is_active=user_info.get('is_active', True)
        )
        
        session.add(user)
        print(f"✅ Utilisateur {user_info['email']} migré")
    
    session.commit()
    print("✅ Migration des utilisateurs terminée")


def migrate_projects(session, data_path="./data"):
    """Migrer les projets depuis les fichiers locaux"""
    projects_path = os.path.join(data_path, "projects")
    if not os.path.exists(projects_path):
        print("❌ Pas de dossier projects trouvé")
        return
    
    print("📥 Migration des projets...")
    
    for project_id in os.listdir(projects_path):
        project_dir = os.path.join(projects_path, project_id)
        if not os.path.isdir(project_dir):
            continue
        
        # Charger les infos du projet
        project_file = os.path.join(project_dir, "project.json")
        if not os.path.exists(project_file):
            continue
        
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Vérifier si le projet existe déjà
        existing = session.query(Project).filter(Project.id == project_id).first()
        if existing:
            print(f"⏭️  Projet {project_data.get('name', project_id)} existe déjà")
            continue
        
        # Trouver l'utilisateur associé
        user = session.query(User).first()  # Prendre le premier utilisateur par défaut
        if not user:
            print(f"❌ Pas d'utilisateur trouvé pour le projet {project_id}")
            continue
        
        # Créer le projet
        project = Project(
            id=project_id,
            user_id=user.id,
            name=project_data.get('name', 'Projet sans nom'),
            description=project_data.get('description'),
            client=project_data.get('client'),
            location=project_data.get('location'),
            created_at=datetime.fromisoformat(project_data['created_at']) if 'created_at' in project_data else datetime.utcnow()
        )
        
        session.add(project)
        print(f"✅ Projet {project_data.get('name', project_id)} migré")
        
        # Migrer les réunions du projet
        meetings_dir = os.path.join(project_dir, "meetings")
        if os.path.exists(meetings_dir):
            migrate_meetings(session, project_id, meetings_dir)
    
    session.commit()
    print("✅ Migration des projets terminée")


def migrate_meetings(session, project_id, meetings_dir):
    """Migrer les réunions d'un projet"""
    for meeting_id in os.listdir(meetings_dir):
        meeting_dir = os.path.join(meetings_dir, meeting_id)
        if not os.path.isdir(meeting_dir):
            continue
        
        # Charger les infos de la réunion
        meeting_file = os.path.join(meeting_dir, "meeting.json")
        if not os.path.exists(meeting_file):
            continue
        
        with open(meeting_file, 'r', encoding='utf-8') as f:
            meeting_data = json.load(f)
        
        # Vérifier si la réunion existe déjà
        existing = session.query(Meeting).filter(Meeting.id == meeting_id).first()
        if existing:
            continue
        
        # Créer la réunion (sans les fichiers audio pour l'instant)
        meeting = Meeting(
            id=meeting_id,
            project_id=project_id,
            title=meeting_data.get('title', 'Réunion sans titre'),
            date=datetime.fromisoformat(meeting_data['date']) if 'date' in meeting_data else datetime.utcnow(),
            location=meeting_data.get('location'),
            participants=json.dumps(meeting_data.get('participants', [])),
            description=meeting_data.get('description'),
            status=meeting_data.get('status', 'completed')
        )
        
        # Ajouter les résultats d'analyse s'ils existent
        analysis_file = os.path.join(meeting_dir, "analysis.json")
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
                meeting.summary = analysis.get('summary')
                meeting.action_items = json.dumps(analysis.get('action_items', []))
                meeting.risks = json.dumps(analysis.get('risks', []))
                meeting.key_points = json.dumps(analysis.get('key_points', []))
        
        session.add(meeting)
        print(f"  ✅ Réunion {meeting_data.get('title', meeting_id)} migrée")


def main():
    """Fonction principale de migration"""
    print("=" * 60)
    print("🔄 MIGRATION DES DONNÉES VERS POSTGRESQL")
    print("=" * 60)
    
    # Obtenir l'URL de la base de données
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL non configurée")
        print("Définissez DATABASE_URL dans votre fichier .env")
        return
    
    # Fix pour Render
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Créer la connexion
        engine = create_engine(database_url)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Connexion à la base de données établie")
        
        # Migrer les données
        migrate_users(session)
        migrate_projects(session)
        
        session.close()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        return


if __name__ == "__main__":
    main()
