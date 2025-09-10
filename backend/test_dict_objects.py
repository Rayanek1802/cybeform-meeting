#!/usr/bin/env python3
"""
Test du traitement des objets dict Python (données déjà structurées) 
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.report_generator import ReportGenerator

def test_dict_objects():
    print("🧪 Test du traitement des objets dict Python")
    print("=" * 60)
    
    generator = ReportGenerator()
    
    # Données comme retournées par l'AnalysisService (objets dict déjà parsés)
    analysis_data_with_dict_objects = {
        "meta": {
            "projectName": "Test Dict Objects",
            "meetingTitle": "Test des objets dict",
            "date": "09/09/2025"
        },
        "sectionsDynamiques": {
            "decisionsStrategiques": [
                {
                    "decision": "Réaliser une inspection ROV après une bathymétrie 3D",
                    "context": "Pour lever les doutes sur le projet",
                    "contexteTemporel": "[00:00-16:07]"
                },
                {
                    "decision": "Valider les calculs avec le bureau d'études spécialisé",
                    "context": "Sécurisation des équipements de levage",
                    "contexteTemporel": "[16:08-24:15]"
                }
            ],
            "aspectsTechniques": [
                {
                    "detail": "Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.",
                    "context": "Calculs surdimensionnés pour les treuils et vérins.",
                    "contexteTemporel": "[32:14 - 48:22]"
                },
                {
                    "detail": "Machine équipée de vérins hydrauliques de 8 tonnes pour supporter une charge de 6 tonnes maximum.",
                    "context": "Sécurité renforcée par surdimensionnement.",
                    "contexteTemporel": "[48:23 - 52:10]"
                }
            ]
        }
    }
    
    print("📊 Données avec objets dict Python:")
    for section, items in analysis_data_with_dict_objects["sectionsDynamiques"].items():
        print(f"  {section}: {len(items)} items")
        for i, item in enumerate(items):
            print(f"    Item {i+1}: {type(item)} - {list(item.keys()) if isinstance(item, dict) else item}")
    
    print("\n📄 Génération du document Word...")
    
    # Test avec données dict structurées
    output_path = "/tmp/test_dict_objects.docx"
    
    transcript_segments = [
        {
            "speaker": "Test Speaker",
            "text": "Test avec objets dict",
            "timestamp": "00:00-00:30"
        }
    ]
    
    meeting_metadata = {
        "title": "Test Dict Objects",
        "date": "09/09/2025",
        "project": "Test Objets Dict",
        "participants": ["Dev", "Test"]
    }
    
    try:
        success = generator.generate_report(analysis_data_with_dict_objects, transcript_segments, meeting_metadata, output_path)
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Document généré avec succès: {output_path}")
            print(f"✅ Taille: {file_size} bytes")
            
            print(f"\n🔍 Vérifications à effectuer:")
            print(f"  1. Les phrases complètes apparaissent-elles dans les tableaux ?")
            print(f"  2. 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.'")
            print(f"  3. 'bureau d'études spécialisé' (avec apostrophe)")
            print(f"  4. Les colonnes Context et Temps sont-elles bien remplies ?")
            
            print(f"\n📄 Ouverture du document pour vérification...")
            os.system(f'open "{output_path}"')
            
        else:
            print("❌ Échec de génération du document")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dict_objects()