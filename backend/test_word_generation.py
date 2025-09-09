#!/usr/bin/env python3
"""
Test script pour tester la génération complète de documents Word avec les phrases complètes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.report_generator import ReportGenerator

def test_word_generation():
    print("📄 Test de génération de document Word")
    print("=" * 50)
    
    generator = ReportGenerator()
    
    # Données de test similaires au problème rencontré
    test_analysis = """
Technicaldetails
    {'detail': 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.', 'context': 'Calculs surdimensionnés pour les treuils et vérins.', 'contexteTemporel': '[32:14 - 48:22]'}
    {'detail': 'Machine équipée de vérins hydrauliques de 8 tonnes pour supporter une charge de 6 tonnes maximum.', 'context': 'Sécurité renforcée par surdimensionnement.', 'contexteTemporel': '[48:23 - 52:10]'}

Decisions
    {'decision': 'Réaliser une inspection ROV après une bathymétrie 3D', 'context': 'Pour lever les doutes sur le projet', 'contexteTemporel': '[00:00-16:07]'}
    {'decision': 'Valider les calculs de charge avec le bureau d\'études spécialisé', 'context': 'Sécurisation des équipements de levage', 'contexteTemporel': '[16:08-24:15]'}

Recommendations
    {'recommendation': 'Effectuer un contrôle technique approfondi avant mise en service', 'context': 'Sécurité des opérations de levage', 'contexteTemporel': '[52:11-58:30]'}
"""
    
    print("📊 Génération du rapport Word...")
    
    try:
        # Génération du document Word
        output_path = "/tmp/test_rapport_complet.docx"
        
        # Préparer les métadonnées de la réunion
        meeting_metadata = {
            "title": "Réunion Test - Vérification Phrases Complètes",
            "date": "09/09/2025",
            "project": "Test des améliorations de parsing",
            "participants": ["Développeur", "Testeur"],
            "duration": "1h30",
            "location": "Local Test"
        }
        
        # Préparer les données d'analyse avec sections parsées manuellement
        analysis_data = {
            "summary": "Test de génération de rapport avec phrases complètes",
            "decisions": [
                {
                    "decision": "Réaliser une inspection ROV après une bathymétrie 3D",
                    "context": "Pour lever les doutes sur le projet",
                    "contexteTemporel": "[00:00-16:07]"
                },
                {
                    "decision": "Valider les calculs de charge avec le bureau d'études spécialisé",
                    "context": "Sécurisation des équipements de levage",
                    "contexteTemporel": "[16:08-24:15]"
                }
            ],
            "technical_details": [
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
            ],
            "recommendations": [
                {
                    "recommendation": "Effectuer un contrôle technique approfondi avant mise en service",
                    "context": "Sécurité des opérations de levage",
                    "contexteTemporel": "[52:11-58:30]"
                }
            ],
            "risks": [],
            "participants": [
                {"name": "Développeur", "role": "Développement"},
                {"name": "Testeur", "role": "Tests"}
            ],
            "chronological_data": [],
            "metrics": {
                "total_speakers": 2,
                "total_duration": "1h30",
                "key_topics": 3
            }
        }
        
        # Segments de transcription factice pour le test
        transcript_segments = [
            {
                "speaker": "Développeur",
                "text": "Nous devons vérifier que les phrases complètes apparaissent dans le document Word généré.",
                "timestamp": "00:00-00:30"
            },
            {
                "speaker": "Testeur", 
                "text": "Effectivement, les treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes doivent être affichés complètement.",
                "timestamp": "32:14-48:22"
            }
        ]
        
        generator.generate_report(analysis_data, transcript_segments, meeting_metadata, output_path)
        
        print(f"✅ Document généré avec succès: {output_path}")
        print()
        print("🔍 Vérifications à effectuer manuellement:")
        print("1. Ouvrir le fichier Word généré")
        print("2. Vérifier que les phrases dans les tableaux sont complètes:")
        print("   - 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.'")
        print("   - 'Machine équipée de vérins hydrauliques de 8 tonnes pour supporter une charge de 6 tonnes maximum.'")
        print("   - 'Réaliser une inspection ROV après une bathymétrie 3D'")
        print("   - 'Valider les calculs de charge avec le bureau d\\'études spécialisé'")
        print("   - 'Effectuer un contrôle technique approfondi avant mise en service'")
        print("3. Vérifier que les colonnes Context et Temps sont bien remplies")
        print("4. Vérifier que le texte n'est pas tronqué dans les cellules")
        
        # Test additionnel: parsing des données
        print("\n🧪 Test du parsing sur les données complètes:")
        sections = generator._extract_sections(test_analysis)
        
        for section_name, items in sections.items():
            if items:
                print(f"\n📋 {section_name.upper()}:")
                for i, item in enumerate(items, 1):
                    if isinstance(item, dict):
                        main_key = next(iter(item.keys()))
                        main_value = item[main_key]
                        print(f"   {i}. {main_value[:80]}{'...' if len(main_value) > 80 else ''}")
                        print(f"      Longueur: {len(main_value)} caractères")
    
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_word_generation()