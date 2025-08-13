@echo off
REM Script de démarrage pour CybeMeeting MVP (Windows)
REM Automatise la création des données de démo et le lancement de l'application

echo 🚀 Démarrage de CybeMeeting MVP
echo ===============================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker n'est pas démarré. Veuillez lancer Docker Desktop.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose n'est pas disponible.
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

echo 📋 Vérification des fichiers de configuration...

REM Create .env files if they don't exist
if not exist "backend\.env" (
    echo 📝 Création du fichier backend\.env...
    copy "backend\env.example" "backend\.env" >nul
    echo ⚠️  Pensez à configurer les clés API dans backend\.env pour une expérience complète
)

if not exist "frontend\btp-meeting-ui\.env" (
    echo 📝 Création du fichier frontend\.env...
    copy "frontend\btp-meeting-ui\env.example" "frontend\btp-meeting-ui\.env" >nul
)

REM Create data directory
echo 📁 Création du répertoire de données...
if not exist "data\projects" mkdir data\projects

REM Check if demo data exists
dir /b "data\projects" 2>nul | findstr "." >nul
if errorlevel 1 (
    echo 🎭 Génération des données de démonstration...
    
    REM Build backend container first to run demo script
    echo 🔨 Construction de l'image backend...
    %COMPOSE_CMD% build backend
    
    REM Run demo data script
    echo 📊 Création des projets de démonstration...
    %COMPOSE_CMD% run --rm backend python scripts/demo_data.py
) else (
    echo ✅ Données de démonstration déjà présentes
)

echo.
echo 🐳 Lancement des conteneurs Docker...
%COMPOSE_CMD% up --build -d

REM Wait for services to be ready
echo ⏳ Attente du démarrage des services...
timeout /t 10 /nobreak >nul

echo 🔍 Vérification de l'état des services...
echo ✅ Backend: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo ✅ Frontend: http://localhost:5173

echo.
echo 🎉 CybeMeeting MVP est en cours de démarrage!
echo.
echo 📱 Interface utilisateur: http://localhost:5173
echo 🔧 API Backend: http://localhost:8000
echo 📖 Documentation API: http://localhost:8000/docs
echo.
echo 📊 Données de démonstration disponibles:
echo    • Rénovation Immeuble Haussman (2 meetings terminés)
echo    • Construction Centre Commercial (1 meeting en attente)
echo    • Réhabilitation Pont Métallique (1 meeting en traitement)
echo.
echo ⚙️  Configuration des clés API (optionnel mais recommandé):
echo    • Éditez backend\.env
echo    • Ajoutez OPENAI_API_KEY pour l'analyse IA complète
echo    • Ajoutez HUGGINGFACE_TOKEN pour la diarisation avancée
echo.
echo 🔧 Commandes utiles:
echo    • Arrêter: %COMPOSE_CMD% down
echo    • Logs: %COMPOSE_CMD% logs -f
echo    • Redémarrer: %COMPOSE_CMD% restart
echo.
echo ✨ Bon test avec CybeMeeting!
echo.
pause
