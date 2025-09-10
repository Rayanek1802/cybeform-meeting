#!/usr/bin/env python3
"""
Test du formatage HTML avec dictionnaires Python
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.report_generator import ReportGenerator

def test_html_formatting():
    print("🌐 Test du formatage HTML avec objets dict")
    print("=" * 60)
    
    generator = ReportGenerator()
    
    # Données avec objets dict comme retournés par l'AnalysisService
    analysis_data = {
        "meta": {
            "projectName": "Test HTML Formatting",
            "meetingTitle": "Test du formatage",
            "meetingDate": "09/09/2025"
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
                }
            ]
        }
    }
    
    meeting_metadata = {
        "title": "Test HTML",
        "date": "09/09/2025",
        "project": "Test Formatage HTML"
    }
    
    print("📊 Génération du HTML preview...")
    
    try:
        html_content = generator.generate_html_preview(analysis_data, meeting_metadata)
        
        # Sauvegarder le HTML pour inspection
        output_file = "/tmp/test_html_formatting.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML généré: {output_file}")
        
        # Extraire et afficher les parties importantes
        print(f"\n🔍 Extrait du contenu HTML généré:")
        print("-" * 50)
        
        # Chercher les sections de décisions et aspects techniques
        if "Réaliser une inspection ROV" in html_content:
            print("✅ Décision trouvée dans le HTML")
        else:
            print("❌ Décision manquante")
            
        if "Treuils de 10 tonnes recalculés" in html_content:
            print("✅ Détail technique trouvé dans le HTML")
        else:
            print("❌ Détail technique manquant")
            
        # Vérifier qu'il n'y a plus de dictionnaires bruts
        if "{'decision':" in html_content or "{'detail':" in html_content:
            print("❌ PROBLÈME: Des dictionnaires bruts sont encore présents")
        else:
            print("✅ Aucun dictionnaire brut détecté")
        
        # Vérifier la présence de formatage HTML
        if "<strong>" in html_content and "<em>" in html_content:
            print("✅ Formatage HTML présent (strong, em)")
        else:
            print("⚠️  Formatage HTML basique")
            
        print(f"\n🌐 Ouverture du fichier HTML pour inspection visuelle...")
        os.system(f'open "{output_file}"')
        
        print(f"\n📋 Ce qu'il faut vérifier dans le navigateur:")
        print(f"  1. Les décisions sont affichées clairement avec le texte en gras")
        print(f"  2. Le contexte apparaît en italique sous chaque élément")
        print(f"  3. Les moments temporels sont affichés avec l'icône ⏱️")
        print(f"  4. Aucun dictionnaire brut du type '{{'decision': '...''}}' n'est visible")
        print(f"  5. La phrase complète 'Treuils de 10 tonnes...' est entièrement visible")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_formatting()