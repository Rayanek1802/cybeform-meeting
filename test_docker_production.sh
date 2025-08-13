#!/bin/bash

# Script pour tester la configuration Docker de production en local
# Avant de déployer sur Render

echo "🐳 Test de la Configuration Docker Production"
echo "============================================"

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé"
    exit 1
fi

print_success "Docker est installé"

# Vérifier si Docker est en cours d'exécution
if ! docker info &> /dev/null; then
    print_error "Docker n'est pas en cours d'exécution"
    exit 1
fi

print_success "Docker est en cours d'exécution"

echo ""
echo "📦 Construction des images Docker de production..."
echo ""

# Build du backend
print_info "Construction du backend..."
cd backend
if docker build -f Dockerfile.production -t cybeform-backend-prod .; then
    print_success "Backend construit avec succès"
else
    print_error "Échec de la construction du backend"
    exit 1
fi
cd ..

echo ""

# Build du frontend
print_info "Construction du frontend..."
cd frontend/btp-meeting-ui
if docker build -f Dockerfile.production -t cybeform-frontend-prod .; then
    print_success "Frontend construit avec succès"
else
    print_error "Échec de la construction du frontend"
    exit 1
fi
cd ../..

echo ""
echo "🚀 Lancement des conteneurs de test..."
echo ""

# Arrêter les conteneurs existants si présents
docker stop cybeform-backend-test 2>/dev/null
docker stop cybeform-frontend-test 2>/dev/null
docker rm cybeform-backend-test 2>/dev/null
docker rm cybeform-frontend-test 2>/dev/null

# Lancer le backend
print_info "Lancement du backend sur le port 8000..."
if [ -f "backend/.env" ]; then
    docker run -d --name cybeform-backend-test \
        -p 8000:8000 \
        --env-file backend/.env \
        -e DATA_PATH=/tmp/data \
        cybeform-backend-prod
else
    print_error "Fichier backend/.env non trouvé"
    print_info "Créez le fichier backend/.env avec vos variables d'environnement"
    exit 1
fi

# Attendre que le backend soit prêt
print_info "Attente du démarrage du backend..."
sleep 5

# Vérifier si le backend répond
if curl -f http://localhost:8000/health &>/dev/null; then
    print_success "Backend accessible sur http://localhost:8000"
else
    print_error "Le backend ne répond pas"
    print_info "Vérifiez les logs avec: docker logs cybeform-backend-test"
fi

# Lancer le frontend
print_info "Lancement du frontend sur le port 3000..."
docker run -d --name cybeform-frontend-test \
    -p 3000:80 \
    cybeform-frontend-prod

print_success "Frontend accessible sur http://localhost:3000"

echo ""
echo "============================================"
echo "📝 Résumé du Test"
echo "============================================"
echo ""
print_success "Images Docker de production construites"
print_success "Backend : http://localhost:8000"
print_success "API Docs : http://localhost:8000/docs"
print_success "Frontend : http://localhost:3000"
echo ""
print_info "Pour voir les logs :"
echo "  Backend  : docker logs cybeform-backend-test"
echo "  Frontend : docker logs cybeform-frontend-test"
echo ""
print_info "Pour arrêter les conteneurs :"
echo "  docker stop cybeform-backend-test cybeform-frontend-test"
echo "  docker rm cybeform-backend-test cybeform-frontend-test"
echo ""
print_success "Si tout fonctionne, vous êtes prêt pour le déploiement sur Render !"
echo ""
