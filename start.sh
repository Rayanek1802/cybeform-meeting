#!/bin/bash

# Script de démarrage pour CybeMeeting MVP
# Automatise la création des données de démo et le lancement de l'application

set -e

echo "🚀 Démarrage de CybeMeeting MVP"
echo "==============================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker n'est pas démarré. Veuillez lancer Docker Desktop."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    echo "❌ Docker Compose n'est pas disponible."
    exit 1
fi

# Use docker compose or docker-compose based on availability
COMPOSE_CMD="docker compose"
if ! docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi

echo "📋 Vérification des fichiers de configuration..."

# Create .env files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Création du fichier backend/.env..."
    cp backend/env.example backend/.env
    echo "⚠️  Pensez à configurer les clés API dans backend/.env pour une expérience complète"
fi

if [ ! -f "frontend/btp-meeting-ui/.env" ]; then
    echo "📝 Création du fichier frontend/.env..."
    cp frontend/btp-meeting-ui/env.example frontend/btp-meeting-ui/.env
fi

# Create data directory
echo "📁 Création du répertoire de données..."
mkdir -p data/projects

# Check if demo data exists
if [ ! -d "data/projects" ] || [ -z "$(ls -A data/projects 2>/dev/null)" ]; then
    echo "🎭 Génération des données de démonstration..."
    
    # Build backend container first to run demo script
    echo "🔨 Construction de l'image backend..."
    $COMPOSE_CMD build backend
    
    # Run demo data script
    echo "📊 Création des projets de démonstration..."
    $COMPOSE_CMD run --rm backend python scripts/demo_data.py
else
    echo "✅ Données de démonstration déjà présentes"
fi

echo ""
echo "🐳 Lancement des conteneurs Docker..."
$COMPOSE_CMD up --build -d

# Wait for services to be ready
echo "⏳ Attente du démarrage des services..."
sleep 10

# Check if services are running
echo "🔍 Vérification de l'état des services..."

# Check backend
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
else
    echo "⚠️  Backend: En cours de démarrage..."
fi

# Check frontend
if curl -f http://localhost:5173 >/dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:5173"
else
    echo "⚠️  Frontend: En cours de démarrage..."
fi

echo ""
echo "🎉 CybeMeeting MVP est en cours de démarrage!"
echo ""
echo "📱 Interface utilisateur: http://localhost:5173"
echo "🔧 API Backend: http://localhost:8000"
echo "📖 Documentation API: http://localhost:8000/docs"
echo ""
echo "📊 Données de démonstration disponibles:"
echo "   • Rénovation Immeuble Haussman (2 meetings terminés)"
echo "   • Construction Centre Commercial (1 meeting en attente)"
echo "   • Réhabilitation Pont Métallique (1 meeting en traitement)"
echo ""
echo "⚙️  Configuration des clés API (optionnel mais recommandé):"
echo "   • Éditez backend/.env"
echo "   • Ajoutez OPENAI_API_KEY pour l'analyse IA complète"
echo "   • Ajoutez HUGGINGFACE_TOKEN pour la diarisation avancée"
echo ""
echo "🔧 Commandes utiles:"
echo "   • Arrêter: $COMPOSE_CMD down"
echo "   • Logs: $COMPOSE_CMD logs -f"
echo "   • Redémarrer: $COMPOSE_CMD restart"
echo ""
echo "✨ Bon test avec CybeMeeting!"
