#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Test loading settings
from core.config import settings
from services.analysis_service import AnalysisService

print("🔑 Test de configuration OpenAI")
print("=" * 50)

print(f"OPENAI_API_KEY présent: {'✅' if settings.OPENAI_API_KEY else '❌'}")
print(f"Longueur de la clé: {len(settings.OPENAI_API_KEY)} caractères")
print(f"is_openai_available: {'✅' if settings.is_openai_available else '❌'}")

print("\n🤖 Test de l'AnalysisService")
print("=" * 50)

try:
    service = AnalysisService()
    print(f"Service.client initialisé: {'✅' if service.client else '❌'}")
    
    if service.client:
        print("✅ AnalysisService prêt à utiliser l'API OpenAI")
    else:
        print("❌ AnalysisService utilise le fallback - pas d'analyse IA")
        
except Exception as e:
    print(f"❌ Erreur lors de l'initialisation: {e}")