# CybeMeeting - MVP BTP

Plateforme complète d'analyse de réunions BTP avec IA intégrée.

## 🚀 Démarrage rapide

### Méthode automatique (recommandée)

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### Méthode manuelle

```bash
# Cloner et démarrer
cd MVP
docker compose up --build

# Accès
Frontend: http://localhost:5173
Backend API: http://localhost:8000/docs
```

### Premier lancement
1. **Données de démonstration** : Le script automatique crée des projets et meetings d'exemple
2. **Configuration optionnelle** : Ajoutez vos clés API dans `backend/.env` pour une expérience complète
3. **Interface web** : Rendez-vous sur http://localhost:5173 pour commencer

## 📋 Prérequis

- Docker & Docker Compose
- Configuration des clés API (optionnel)

## ⚙️ Configuration

### Backend (.env)
```bash
cp backend/.env.example backend/.env
```

Variables importantes:
- `OPENAI_API_KEY`: Pour transcription et analyse IA
- `HUGGINGFACE_TOKEN`: Pour diarisation des intervenants
- `MODEL_NAME`: Modèle OpenAI (défaut: gpt-4o)

### Frontend (.env)
```bash
cp frontend/btp-meeting-ui/.env.example frontend/btp-meeting-ui/.env
```

## 🏗️ Architecture

### Stack Technique
- **Frontend**: React + Vite + TypeScript + Tailwind + shadcn/ui
- **Backend**: FastAPI + Python 3.11
- **IA**: OpenAI Whisper + pyannote.audio + GPT-4o
- **Stockage**: Local filesystem

### Pipeline IA
1. **Normalisation audio** (ffmpeg)
2. **Diarisation** (pyannote.audio)
3. **Transcription** (Whisper API/Local)
4. **Analyse IA** (GPT-4o)
5. **Génération rapport** (.docx)

## 📊 Fonctionnalités

### ✅ Implémenté
- Création et gestion de projets BTP
- Enregistrement audio en direct
- Import de fichiers audio (mp3, wav, m4a, webm)
- Pipeline IA complet (diarisation, transcription, analyse)
- Génération de rapports Word structurés
- Interface moderne et responsive
- Données de démonstration intégrées

### 🎯 Parcours utilisateur
1. Créer un projet BTP
2. Créer un nouveau meeting
3. Enregistrer ou importer l'audio
4. Lancer l'analyse IA
5. Consulter et télécharger le rapport

### 🎭 Données de démonstration
Le MVP inclut 3 projets d'exemple avec meetings :
- **Rénovation Immeuble Haussman** : 2 meetings terminés avec rapports complets
- **Construction Centre Commercial** : 1 meeting en attente
- **Réhabilitation Pont Métallique** : 1 meeting en cours de traitement

Ces données permettent de tester immédiatement toutes les fonctionnalités sans créer de contenu.

## 📁 Structure

```
MVP/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── main.py      # Point d'entrée
│   │   ├── api/         # Endpoints
│   │   ├── core/        # Configuration
│   │   ├── models/      # Modèles Pydantic
│   │   ├── services/    # Logique métier
│   │   └── utils/       # Utilitaires
│   └── Dockerfile
├── frontend/btp-meeting-ui/  # Interface React
│   ├── src/
│   │   ├── components/  # Composants UI
│   │   ├── pages/       # Pages principales
│   │   ├── lib/         # Configuration
│   │   └── store/       # State management
│   └── Dockerfile
├── data/                 # Données persistantes
└── docker-compose.yml
```

## 🛠️ Développement

### Démarrage local
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend/btp-meeting-ui
npm install
npm run dev
```

### Tests
```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend/btp-meeting-ui
npm run test
```

## 📄 API Documentation

Documentation interactive disponible sur: http://localhost:8000/docs

### Endpoints principaux
- `POST /api/projects` - Créer un projet
- `POST /api/projects/{id}/meetings` - Créer un meeting
- `POST /api/meetings/{id}/audio` - Upload audio
- `POST /api/meetings/{id}/process` - Lancer l'analyse
- `GET /api/meetings/{id}/status` - État de traitement
- `GET /api/meetings/{id}/report.docx` - Télécharger rapport

## 🎨 Design System

Interface moderne avec:
- Palette de couleurs professionnelle (tokens CSS variables)
- Composants shadcn/ui
- Animations Framer Motion
- Design responsive
- Accessibilité intégrée

## 🔧 Personnalisation

### Couleurs de marque
Modifier les tokens CSS dans `frontend/btp-meeting-ui/src/index.css`:
```css
:root {
  --brand-primary: #votre-couleur;
  --brand-secondary: #votre-couleur;
  /* ... */
}
```

## 📞 Support

Pour toute question ou problème, consulter les logs:
```bash
docker compose logs backend
docker compose logs frontend
```

## 🚀 Production

Pour déploiement production:
1. Configurer les variables d'environnement
2. Utiliser un serveur web (nginx) en proxy
3. Configurer SSL/TLS
4. Mettre en place monitoring et sauvegardes
