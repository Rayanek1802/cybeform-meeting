#!/usr/bin/env python3
"""
Test script pour tester le parsing des dictionnaires dans report_generator.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.report_generator import ReportGenerator

# Test data similaire à ce que tu as montré dans ton screenshot
test_data = """
Technicaldetails
    {'detail': 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.', 'context': 'Calculs surdimensionnés pour les treuils et vérins.', 'contexteTemporel': '[32:14 - 48:22]'}

Decisions
    {'decision': 'Réaliser une inspection ROV après une bathymétrie 3D', 'context': 'Pour lever les doutes sur le projet', 'contexteTemporel': '[00:00-16:07]'}
"""

def test_parsing():
    print("🧪 Test du parsing des dictionnaires Python")
    print("=" * 50)
    
    generator = ReportGenerator()
    
    # Test du parsing d'un dictionnaire simple
    test_dict = "{'detail': 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.', 'context': 'Calculs surdimensionnés pour les treuils et vérins.', 'contexteTemporel': '[32:14 - 48:22]'}"
    
    print(f"📝 Dictionnaire d'entrée:")
    print(test_dict)
    print()
    
    result = generator._parse_dict_string(test_dict)
    
    print(f"✅ Résultat du parsing:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\n📊 Statistiques:")
    print(f"  - Nombre de clés extraites: {len(result)}")
    print(f"  - Phrase complète capturée: {'Oui' if len(result.get('detail', '')) > 50 else 'Non'}")
    
    # Test avec le détecteur de structure dict-like
    print(f"\n🔍 Test de détection de structure dict-like:")
    is_dict_like = generator._is_dict_like_string(test_dict)
    print(f"  Structure détectée comme dict-like: {is_dict_like}")

if __name__ == "__main__":
    test_parsing()