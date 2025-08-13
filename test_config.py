#!/usr/bin/env python
"""
Script pour tester les configurations avant déploiement
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("🔍 TEST DE CONFIGURATION POUR DÉPLOIEMENT")
print("=" * 60)

# Test des variables essentielles
configs = {
    "OpenAI API Key": os.getenv("OPENAI_API_KEY"),
    "Cloudinary Cloud Name": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "Cloudinary API Key": os.getenv("CLOUDINARY_API_KEY"),
    "Cloudinary API Secret": os.getenv("CLOUDINARY_API_SECRET"),
    "Database URL": os.getenv("DATABASE_URL"),
    "JWT Secret Key": os.getenv("JWT_SECRET_KEY"),
}

all_good = True

for name, value in configs.items():
    if value:
        # Masquer les valeurs sensibles
        if "secret" in name.lower() or "key" in name.lower():
            display_value = value[:5] + "..." + value[-3:] if len(value) > 8 else "***"
        else:
            display_value = value[:20] + "..." if len(value) > 20 else value
        print(f"✅ {name}: {display_value}")
    else:
        print(f"❌ {name}: NON CONFIGURÉ")
        all_good = False

print("\n" + "=" * 60)

if all_good:
    print("✅ TOUTES LES CONFIGURATIONS SONT PRÉSENTES")
    print("\nProcédez au déploiement en suivant le guide !")
else:
    print("⚠️  CONFIGURATIONS MANQUANTES")
    print("\nAssurez-vous de configurer toutes les variables")
    print("dans votre fichier .env ou sur Render")

print("=" * 60)

# Test des imports essentiels
print("\n📦 Test des dépendances Python...")
try:
    import fastapi
    print("✅ FastAPI installé")
except ImportError:
    print("❌ FastAPI non installé")

try:
    import sqlalchemy
    print("✅ SQLAlchemy installé")
except ImportError:
    print("❌ SQLAlchemy non installé")

try:
    import cloudinary
    print("✅ Cloudinary installé")
except ImportError:
    print("❌ Cloudinary non installé")

try:
    import openai
    print("✅ OpenAI installé")
except ImportError:
    print("❌ OpenAI non installé")

print("\n" + "=" * 60)
print("Test terminé !")
print("=" * 60)
