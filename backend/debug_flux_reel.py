#!/usr/bin/env python3
"""
Debug du flux réel de l'application pour comprendre pourquoi les phrases sont encore tronquées
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.analysis_service import AnalysisService
from services.report_generator import ReportGenerator

def debug_real_flow():
    print("🔍 DEBUG DU FLUX RÉEL DE L'APPLICATION")
    print("=" * 60)
    
    # 1. Simuler des données comme celles retournées par l'AnalysisService
    print("\n📊 1. Simulation des données d'analyse IA")
    print("-" * 50)
    
    # Structure typique retournée par l'AnalysisService (fallback ou réel)
    analysis_result = {
        "meta": {
            "projectName": "Test Projet",
            "meetingTitle": "Test Meeting",
            "duration": "1h30"
        },
        "sectionsDynamiques": {
            "decisionsStrategiques": [
                "{'decision': 'Réaliser une inspection ROV après une bathymétrie 3D', 'context': 'Pour lever les doutes sur le projet', 'contexteTemporel': '[00:00-16:07]'}",
                "{'decision': 'Valider les calculs de charge avec le bureau d\\'études spécialisé', 'context': 'Sécurisation des équipements de levage', 'contexteTemporel': '[16:08-24:15]'}"
            ],
            "aspectsTechniques": [
                "{'detail': 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.', 'context': 'Calculs surdimensionnés pour les treuils et vérins.', 'contexteTemporel': '[32:14 - 48:22]'}",
                "{'detail': 'Machine équipée de vérins hydrauliques de 8 tonnes pour supporter une charge de 6 tonnes maximum.', 'context': 'Sécurité renforcée par surdimensionnement.', 'contexteTemporel': '[48:23 - 52:10]'}"
            ]
        }
    }
    
    print("✅ Données d'analyse simulées créées")
    
    # 2. Test de la détection des dictionnaires
    print("\n🔍 2. Test de détection des dictionnaires")
    print("-" * 50)
    
    generator = ReportGenerator()
    
    test_string = "{'detail': 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.', 'context': 'Calculs surdimensionnés pour les treuils et vérins.', 'contexteTemporel': '[32:14 - 48:22]'}"
    
    print(f"String à tester:")
    print(f"  {test_string}")
    
    is_dict_like = generator._is_dict_like_string(test_string)
    print(f"\n  Détecté comme dict-like: {'✅ OUI' if is_dict_like else '❌ NON'}")
    
    if is_dict_like:
        parsed = generator._parse_dict_string(test_string)
        print(f"  Résultat du parsing:")
        for key, value in parsed.items():
            print(f"    {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    # 3. Test du flux complet de génération
    print("\n📄 3. Test de génération de document Word")
    print("-" * 50)
    
    output_path = "/tmp/debug_flux_reel.docx"
    
    try:
        # Simuler les transcript_segments
        transcript_segments = [
            {
                "speaker": "Speaker 1",
                "text": "Discussion sur les treuils et vérins",
                "timestamp": "00:30-01:00"
            }
        ]
        
        # Simuler meeting_metadata
        meeting_metadata = {
            "title": "Debug Flux Réel",
            "date": "09/09/2025",
            "project": "Test Debug",
            "participants": ["Dev", "Test"]
        }
        
        success = generator.generate_report(analysis_result, transcript_segments, meeting_metadata, output_path)
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Document généré: {output_path}")
            print(f"✅ Taille: {file_size} bytes")
            
            print(f"\n🔍 Analyse du contenu généré:")
            print(f"  - Le document contient-il des phrases complètes ?")
            print(f"  - Les tableaux sont-ils correctement formatés ?")
            print(f"  - Ouvrez le fichier pour vérification manuelle")
            
        else:
            print("❌ Échec de génération du document")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

    # 4. Test spécifique du problème des données déjà structurées
    print("\n🧪 4. Test avec données déjà structurées (cas réel)")
    print("-" * 50)
    
    # Cas où l'AnalysisService retourne des données déjà parsées
    already_structured_data = {
        "meta": {"projectName": "Test Structuré"},
        "sectionsDynamiques": {
            "decisionsStrategiques": [
                {
                    "decision": "Réaliser une inspection ROV après une bathymétrie 3D",
                    "context": "Pour lever les doutes sur le projet",
                    "contexteTemporel": "[00:00-16:07]"
                }
            ]
        }
    }
    
    print("Structure avec données déjà parsées:")
    for section, content in already_structured_data["sectionsDynamiques"].items():
        print(f"  {section}: {type(content[0])} - {content[0] if isinstance(content[0], dict) else 'string'}")
    
    print("\n💡 Diagnostic:")
    print("  - Si l'AnalysisService retourne des dicts, notre parsing n'est pas appliqué")
    print("  - Si l'AnalysisService retourne des strings, notre parsing devrait fonctionner")
    print("  - Il faut vérifier quel format l'AnalysisService retourne réellement")

if __name__ == "__main__":
    debug_real_flow()