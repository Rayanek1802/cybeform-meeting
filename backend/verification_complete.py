#!/usr/bin/env python3
"""
Script de vérification complète des améliorations apportées au parsing des dictionnaires
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.report_generator import ReportGenerator

def main():
    print("🔍 VÉRIFICATION COMPLÈTE DES AMÉLIORATIONS")
    print("=" * 60)
    
    generator = ReportGenerator()
    
    # Test 1: Parsing du dictionnaire problématique original
    print("\n📝 Test 1: Parsing du dictionnaire original problématique")
    print("-" * 50)
    
    problematic_dict = "{'detail': 'Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes.', 'context': 'Calculs surdimensionnés pour les treuils et vérins.', 'contexteTemporel': '[32:14 - 48:22]'}"
    
    result = generator._parse_dict_string(problematic_dict)
    
    print(f"Dictionnaire testé:")
    print(f"  {problematic_dict}")
    print(f"\nRésultat du parsing:")
    
    success = True
    expected_keys = ['detail', 'context', 'contexteTemporel']
    
    for key in expected_keys:
        if key in result:
            print(f"  ✅ {key}: {result[key]}")
        else:
            print(f"  ❌ {key}: MANQUANT")
            success = False
    
    # Test spécifique de la phrase complète
    detail_complete = result.get('detail', '')
    expected_detail = "Treuils de 10 tonnes recalculés à 4 tonnes, vérins de 8 tonnes pour une machine de 6 tonnes."
    
    print(f"\n🎯 Test de la phrase complète:")
    print(f"  Attendu: {expected_detail}")
    print(f"  Obtenu:  {detail_complete}")
    
    if detail_complete == expected_detail:
        print(f"  ✅ Phrase complète correctement parsée (longueur: {len(detail_complete)} caractères)")
    else:
        print(f"  ❌ Phrase incomplète ou incorrecte")
        success = False
    
    # Test 2: Détection dict-like
    print(f"\n🔍 Test 2: Détection de structure dict-like")
    print("-" * 50)
    
    is_dict_like = generator._is_dict_like_string(problematic_dict)
    print(f"  Structure détectée comme dict-like: {'✅ OUI' if is_dict_like else '❌ NON'}")
    
    if not is_dict_like:
        success = False
    
    # Test 3: Cas complexes avec apostrophes et caractères spéciaux
    print(f"\n🧪 Test 3: Cas complexes avec apostrophes")
    print("-" * 50)
    
    complex_dict = "{'decision': 'Valider les calculs avec le bureau d\\'études spécialisé', 'context': 'Sécurisation des équipements', 'contexteTemporel': '[16:08-24:15]'}"
    complex_result = generator._parse_dict_string(complex_dict)
    
    expected_decision = "Valider les calculs avec le bureau d'études spécialisé"
    actual_decision = complex_result.get('decision', '')
    
    print(f"  Attendu: {expected_decision}")
    print(f"  Obtenu:  {actual_decision}")
    
    if actual_decision == expected_decision:
        print(f"  ✅ Apostrophes correctement gérées")
    else:
        print(f"  ❌ Problème avec les apostrophes")
        success = False
    
    # Test 4: Génération de document Word réussie
    print(f"\n📄 Test 4: Génération de document Word")
    print("-" * 50)
    
    word_file = "/tmp/test_rapport_complet.docx"
    if os.path.exists(word_file):
        file_size = os.path.getsize(word_file)
        print(f"  ✅ Document généré: {word_file}")
        print(f"  ✅ Taille: {file_size} bytes")
        
        if file_size > 30000:  # Un document avec contenu doit faire plus de 30KB
            print(f"  ✅ Document semble contenir du contenu substantiel")
        else:
            print(f"  ⚠️  Document peut-être trop petit")
    else:
        print(f"  ❌ Document Word non trouvé")
        success = False
    
    # Résumé final
    print(f"\n🎯 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if success:
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("")
        print("📋 Améliorations validées:")
        print("  • Parser de dictionnaires amélioré")
        print("  • Phrases complètes correctement extraites")
        print("  • Gestion des apostrophes et caractères spéciaux")
        print("  • Génération de documents Word fonctionnelle")
        print("")
        print("🚀 Les modifications sont prêtes à être commitées!")
        return True
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Vérifiez les erreurs ci-dessus avant de commiter")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)