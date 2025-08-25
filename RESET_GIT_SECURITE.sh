#!/bin/bash

# Script pour réinitialiser complètement Git et supprimer l'historique avec les clés API

echo "🔐 Réinitialisation Git pour sécurité..."

# Sauvegarder la configuration remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

# Supprimer complètement le dossier .git
rm -rf .git

# Réinitialiser Git
git init

# Ajouter tous les fichiers (sans les clés maintenant)
git add .

# Faire un commit initial propre
git commit -m "Initial commit - Configuration sécurisée pour déploiement Render"

# Rajouter le remote si existait
if [ ! -z "$REMOTE_URL" ]; then
    git remote add origin $REMOTE_URL
    echo "✅ Remote ajouté: $REMOTE_URL"
fi

echo "✅ Git réinitialisé avec succès !"
echo ""
echo "Pour pousser sur GitHub, utilisez :"
echo "  git push --force origin main"
echo ""
echo "⚠️  IMPORTANT: Assurez-vous d'avoir créé votre fichier backend/.env avec vos clés API !"

