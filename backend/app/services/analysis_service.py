"""
AI analysis service using OpenAI GPT models
"""
import json
import openai
from typing import Dict, Any, List, Optional
import logging

from app.core.config import settings
from app.models.schemas import MeetingAnalysis, ActionItem, RiskItem

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for AI-powered meeting analysis"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if settings.is_openai_available:
            try:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized for analysis")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def analyze_meeting(
        self, 
        transcript_segments: List[Dict[str, Any]], 
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze meeting transcript and extract structured information
        """
        if not self.client:
            return self._create_fallback_analysis(transcript_segments, meeting_metadata)
        
        try:
            # Prepare transcript text
            full_transcript = self._format_transcript_for_analysis(transcript_segments)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(full_transcript, meeting_metadata)
            
            # Call OpenAI API
            ai_instructions = meeting_metadata.get('ai_instructions', '')
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(ai_instructions)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Très déterministe pour la cohérence
                max_tokens=12000  # Beaucoup plus de tokens pour les rapports ultra-détaillés
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            analysis_data = json.loads(analysis_text)
            
            # Validate and clean analysis
            cleaned_analysis = self._validate_and_clean_analysis(analysis_data)
            
            logger.info("Meeting analysis completed successfully")
            return cleaned_analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._create_fallback_analysis(transcript_segments, meeting_metadata)
    
    def _get_system_prompt(self, user_instructions: str = None) -> str:
        """Get system prompt for analysis based on user instructions"""
        
        base_prompt = """Tu es un expert en analyse de réunions BTP avec 15 ans d'expérience. Tu analyses les transcriptions de réunions pour extraire TOUTES les informations importantes selon un format JSON strict.

PRINCIPES FONDAMENTAUX:
- NE JAMAIS omettre d'informations importantes
- Extraire TOUS les détails techniques, même mineurs
- Capturer TOUTES les décisions, même implicites
- Identifier TOUS les points d'action mentionnés
- Noter TOUS les problèmes soulevés
- Documenter TOUS les aspects budgétaires/planning évoqués

CONTEXTE BTP GÉNÉRAL:
- Focus projets construction, chantiers, planning, matériaux, normes, sécurité
- Identifier problèmes techniques, contraintes réglementaires, autorisations
- Extraire risques spécifiques BTP (sécurité, retards, surcoûts, météo, coordination)
- Distinguer éléments pertinents des bavardages informels"""

        # Instructions spécifiques de l'utilisateur
        user_specific_guidance = ""
        if user_instructions and user_instructions.strip():
            user_specific_guidance = f"""
INSTRUCTIONS SPÉCIFIQUES DE L'UTILISATEUR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{user_instructions.strip()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: Respecte scrupuleusement ces instructions utilisateur dans ton analyse.
Adapte ton focus, ton angle d'approche et tes priorités selon ces directives.
"""

        return f"""{base_prompt}

{user_specific_guidance}

QUALITÉ DE L'EXTRACTION:
- Être EXHAUSTIF: aucun détail important omis
- Être PRÉCIS: noms, dates, quantités exactes
- Être CONTEXTUEL: replacer dans le contexte projet
- Distinguer: décisions prises vs points à trancher
- Hiérarchiser: urgent vs important vs informatif
- ADAPTER L'ANALYSE selon les instructions spécifiques de l'utilisateur

EXIGENCES TECHNIQUES:
- Format JSON strict respecté
- Réponse UNIQUEMENT en JSON valide
- Pas de commentaires en dehors du JSON
- Toutes les sections remplies (même si vides)"""
    
    def _create_analysis_prompt(self, transcript: str, metadata: Dict[str, Any]) -> str:
        """Create analysis prompt with adaptive sections"""
        participants_detected = metadata.get('participants', [])
        expected_speakers = metadata.get('expected_speakers', len(participants_detected))
        ai_instructions = metadata.get('ai_instructions', '')
        duration_minutes = metadata.get('duration', 0)
        
        # Analysis of participant attendance
        attendance_analysis = ""
        if expected_speakers != len(participants_detected):
            if len(participants_detected) < expected_speakers:
                attendance_analysis = f"\n⚠️ ATTENTION: {expected_speakers} participants attendus mais seulement {len(participants_detected)} détectés (possibles absences)"
            else:
                attendance_analysis = f"\n📈 NOTE: {len(participants_detected)} participants détectés vs {expected_speakers} attendus (participants supplémentaires)"
        
        instructions_display = f"\n📋 Instructions utilisateur: {ai_instructions}" if ai_instructions and ai_instructions.strip() else ""
        
        # Deduce meeting type from AI instructions or use default
        meeting_type = "Autre"
        if ai_instructions:
            ai_lower = ai_instructions.lower()
            if "chantier" in ai_lower:
                meeting_type = "Réunion de chantier"
            elif "avancement" in ai_lower or "suivi" in ai_lower:
                meeting_type = "Point d'avancement"
            elif "coordination" in ai_lower:
                meeting_type = "Réunion de coordination"
            elif "sécurité" in ai_lower:
                meeting_type = "Réunion sécurité"
            elif "livraison" in ai_lower:
                meeting_type = "Réunion de livraison"
            else:
                meeting_type = "Réunion personnalisée"
        
        return f"""Tu es un expert en analyse de réunions BTP. Analyse EXHAUSTIVEMENT cette transcription et crée un rapport ULTRA-COMPLET qui capture TOUS les points abordés.

CONTEXTE DE LA RÉUNION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Projet: {metadata.get('project_name', 'Non spécifié')}
📝 Titre: {metadata.get('title', 'Non spécifié')}
📅 Date: {metadata.get('date', 'Non spécifié')}
⏱️ Durée: {duration_minutes} minutes
👥 Participants détectés: {', '.join(participants_detected) if participants_detected else 'Aucun'}
👤 Participants attendus: {expected_speakers}{attendance_analysis}{instructions_display}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MISSION CRITIQUE:
🎯 EXTRAIRE ABSOLUMENT TOUT: Ne laisser aucun point important, aucune décision, aucun problème sans le documenter
🎯 SECTIONS DYNAMIQUES: Créer autant de sous-sections que nécessaire selon le contenu réel de la réunion
🎯 DÉTAIL MAXIMUM: Chaque point doit être développé avec son contexte, ses enjeux, ses acteurs
🎯 FIDÉLITÉ TOTALE: Refléter fidèlement l'intensité et la priorité donnée à chaque sujet dans la discussion

TRANSCRIPTION COMPLÈTE À ANALYSER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{transcript}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRUCTURE JSON ATTENDUE - SECTIONS ADAPTATIVES ET EXHAUSTIVES:
{{
  "meta": {{
    "projectName": "{metadata.get('project_name', 'Non spécifié')}",
    "meetingTitle": "{metadata.get('title', 'Non spécifié')}",
    "meetingType": "{meeting_type}",
    "meetingDate": "{metadata.get('date', 'Non spécifié')}",
    "duration": {duration_minutes},
    "participantsExpected": {expected_speakers},
    "participantsDetected": {participants_detected},
    "userInstructions": "{ai_instructions}",
    "attendanceAnalysis": "{attendance_analysis.replace(chr(10), ' ').strip()}"
  }},
  "sectionsDynamiques": {{
    "/* CRÉER AUTANT DE SECTIONS QUE NÉCESSAIRE SELON LE CONTENU RÉEL */": "Exemples ci-dessous",
    "etatLieux": [
      "/* SI la réunion fait un état des lieux */",
      "Point d'état 1 avec détails et mesures concrètes",
      "Constat 2 avec chiffres et responsables concernés",
      "Situation 3 avec impact sur la suite du projet"
    ],
    "avancementTravaux": [
      "/* SI des avancements de travaux sont discutés */",
      "Avancement lot 1: détails précis, pourcentage, planning",
      "Progression technique sur section X: méthodes, résultats, difficultés",
      "Finitions en cours: état, qualité, corrections à apporter"
    ],
    "problemesIdentifies": [
      "/* TOUS les problèmes, même mineurs */",
      "Problème technique détaillé: cause, impact, solutions proposées",
      "Difficulté organisationnelle: nature, responsables, échéances",
      "Contrainte externe: origine, influence sur planning, contournements"
    ],
    "decisionsStrategiques": [
      "/* Décisions importantes avec contexte de prise de décision */",
      "Décision majeure 1: motivations, alternatives étudiées, mise en œuvre",
      "Arbitrage technique: critères, conséquences, responsables de l'exécution",
      "Choix organisationnel: justification, impact, suivi nécessaire"
    ],
    "actionsUrgentes": [
      {{
        "action": "Description complète de l'action urgente",
        "responsable": "Nom exact ou fonction précise",
        "echeance": "Date/délai précis",
        "contexte": "Pourquoi cette urgence, enjeux, risques si non fait",
        "moyens": "Ressources nécessaires, support requis"
      }}
    ],
    "actionsReguliers": [
      {{
        "action": "Description de l'action de suivi régulier",
        "responsable": "Qui doit s'en occuper",
        "echeance": "Périodicité ou date limite",
        "contexte": "Objectif, méthode, critères de succès",
        "dependances": "Ce qui doit être fait avant/après"
      }}
    ],
    "aspectsTechniques": [
      "/* TOUS les points techniques abordés, avec niveau de détail */",
      "Spécification technique 1: normes, contraintes, mise en œuvre",
      "Innovation/méthode particulière: avantages, risques, formation nécessaire",
      "Interface entre lots: coordination, responsabilités, planning"
    ],
    "planningEtDelais": [
      "/* Tout ce qui concerne le temps et les échéances */",
      "Jalon critique: date, dépendances, risques de décalage",
      "Réajustement de planning: raisons, nouvelles dates, impacts",
      "Chemin critique: étapes clés, goulots d'étranglement identifiés"
    ],
    "aspectsFinanciers": [
      "/* Budget, coûts, économies, dépassements */",
      "Poste budgétaire discuté: montant, évolution, justification",
      "Avenant potentiel: raison, estimation, processus de validation",
      "Optimisation proposée: économies attendues, investissement requis"
    ],
    "relationsFournisseurs": [
      "/* SI discussions avec/sur fournisseurs, sous-traitants */",
      "Négociation en cours: objet, positions, échéances",
      "Problème fournisseur: nature, impact, solutions alternatives",
      "Nouveau partenaire: évaluation, critères, décision attendue"
    ],
    "aspectsReglementaires": [
      "/* Normes, autorisations, conformité */",
      "Conformité réglementaire: exigences, état d'avancement, actions requises",
      "Autorisation nécessaire: type, délais, démarches en cours",
      "Contrôle qualité: standards, vérifications, corrections"
    ],
    "communicationClient": [
      "/* SI interaction client évoquée */",
      "Demande client: nature, faisabilité, impact sur projet",
      "Présentation prévue: contenu, date, responsables",
      "Feedback client: retours, demandes d'ajustement, validation"
    ],
    "risquesEtMitigations": [
      {{
        "risque": "Description précise du risque identifié",
        "categorie": "Technique/Planning/Budget/Externe/Humain",
        "probabilite": "Élevée/Moyenne/Faible avec justification",
        "impact": "Conséquences détaillées sur projet/planning/budget",
        "mitigations": "Actions concrètes pour réduire/éviter le risque",
        "responsableRisque": "Qui surveille et gère ce risque",
        "echeanceAction": "Quand agir pour prévenir le risque"
      }}
    ],
    "pointsDivers": [
      "/* Tout autre point important ne rentrant pas ailleurs */",
      "Information externe pertinente: source, impact, actions à prendre",
      "Retour d'expérience: leçon apprise, amélioration possible",
      "Coordination avec autres projets: interfaces, synergies, conflits"
    ],
    "syntheseDesAccords": [
      "/* Résumé des consensus et validation */",
      "Accord majeur 1: nature, participants validants, modalités application",
      "Consensus technique: solution retenue, arguments, mise en œuvre",
      "Validation procesuelle: étapes validées, prochaines étapes"
    ],
    "pointsEnSuspens": [
      "/* Ce qui reste à clarifier/décider */",
      "Question ouverte 1: enjeux, options possibles, qui doit trancher, quand",
      "Étude complémentaire requise: objectifs, responsable, délais",
      "Décision reportée: raisons, nouvelle échéance, éléments manquants"
    ]
  }},
  "vueChronologique": [
    "/* Séquence des événements/discussions dans l'ordre chronologique */",
    "[00:00-05:00] Introduction et tour de table: participants, objectifs annoncés",
    "[05:00-15:00] Point d'avancement: sections A, B, C avec détails et chiffres",
    "[15:00-25:00] Problèmes techniques identifiés: nature, causes, solutions",
    "[25:00-40:00] Décisions prises: choix X, Y, Z avec argumentaires",
    "[40:00-fin] Actions et planning: qui fait quoi, quand, avec quelles ressources"
  ],
  "analysisMetrics": {{
    "totalSegments": nombre_total_segments_transcript,
    "segmentsAnalyses": nombre_segments_avec_contenu_pertinent,
    "niveauDetaille": "Très élevé/Élevé/Moyen/Basique",
    "couvertureSujets": "Exhaustive/Large/Partielle/Limitée",
    "qualiteExtraction": "Excellent/Bon/Moyen/Insuffisant"
  }}
}}

🚨 RÈGLES ABSOLUES:
1. N'OMETTRE AUCUN POINT mentionné dans la transcription, même brièvement
2. CRÉER LES SECTIONS qui correspondent au contenu réel (supprimer celles vides, ajouter celles nécessaires)
3. DÉTAILLER chaque point avec son contexte, ses acteurs, ses enjeux
4. DISTINGUER l'urgent de l'important, le décidé du proposé, le factuel de l'opinion
5. RESPECTER PRIORITAIREMENT les instructions utilisateur: {ai_instructions}

Génère maintenant le JSON le plus exhaustif possible:"""
    
    def _format_transcript_for_analysis(self, segments: List[Dict[str, Any]]) -> str:
        """Format transcript segments for analysis"""
        formatted_lines = []
        
        for segment in segments:
            speaker = segment.get("speaker", "UNKNOWN")
            text = segment.get("text", "").strip()
            start_time = segment.get("start_time", 0)
            
            if text:
                # Format: [MM:SS] SPEAKER: text
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                
                formatted_lines.append(f"{timestamp} {speaker}: {text}")
        
        return "\n".join(formatted_lines)
    
    def _validate_and_clean_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean analysis data with dynamic sections support"""
        # Ensure basic structure exists
        if "meta" not in analysis_data:
            analysis_data["meta"] = {}
        
        # Handle new dynamic sections structure or fallback to old structure
        if "sectionsDynamiques" in analysis_data:
            # New format with dynamic sections
            sections_data = analysis_data["sectionsDynamiques"]
            
            # Clean dynamic sections - remove comment keys and empty sections
            cleaned_sections = {}
            for section_name, section_content in sections_data.items():
                if not section_name.startswith("/*") and section_content:
                    if isinstance(section_content, list) and len(section_content) > 0:
                        # Filter out comment items
                        cleaned_content = [item for item in section_content if not str(item).startswith("/*")]
                        if cleaned_content:
                            cleaned_sections[section_name] = cleaned_content
                    elif isinstance(section_content, dict):
                        cleaned_sections[section_name] = section_content
            
            analysis_data["sectionsDynamiques"] = cleaned_sections
            
            # Ensure chronological view exists
            if "vueChronologique" not in analysis_data:
                analysis_data["vueChronologique"] = []
            
            # Ensure analysis metrics exist
            if "analysisMetrics" not in analysis_data:
                analysis_data["analysisMetrics"] = {
                    "totalSegments": 0,
                    "segmentsAnalyses": 0,
                    "niveauDetaille": "Moyen",
                    "couvertureSujets": "Partielle",
                    "qualiteExtraction": "Bon"
                }
        else:
            # Old format - convert to new format for compatibility
            default_analysis = {
                "objectifs": [],
                "problemes": [],
                "decisions": [],
                "actions": [],
                "risques": [],
                "pointsTechniquesBTP": [],
                "planning": [],
                "budget_chiffrage": [],
                "divers": [],
                "exclusions": []
            }
            
            # Merge with defaults
            for key, default_value in default_analysis.items():
                if key not in analysis_data:
                    analysis_data[key] = default_value
            
            # Convert old format to new dynamic sections format
            dynamic_sections = {}
            
            if analysis_data.get("objectifs"):
                dynamic_sections["objectifs"] = analysis_data["objectifs"]
            if analysis_data.get("problemes"):
                dynamic_sections["problemesIdentifies"] = analysis_data["problemes"]
            if analysis_data.get("decisions"):
                dynamic_sections["decisionsStrategiques"] = analysis_data["decisions"]
            if analysis_data.get("pointsTechniquesBTP"):
                dynamic_sections["aspectsTechniques"] = analysis_data["pointsTechniquesBTP"]
            if analysis_data.get("planning"):
                dynamic_sections["planningEtDelais"] = analysis_data["planning"]
            if analysis_data.get("budget_chiffrage"):
                dynamic_sections["aspectsFinanciers"] = analysis_data["budget_chiffrage"]
            if analysis_data.get("divers"):
                dynamic_sections["pointsDivers"] = analysis_data["divers"]
            
            # Handle actions - convert to new format
            if analysis_data.get("actions"):
                actions_urgentes = []
                actions_reguliers = []
                for action in analysis_data["actions"]:
                    if isinstance(action, dict):
                        priorite = action.get("priorite", "").lower()
                        if priorite in ["haute", "urgent", "urgente"]:
                            actions_urgentes.append(action)
                        else:
                            actions_reguliers.append(action)
                    else:
                        # Old string format
                        actions_reguliers.append({
                            "action": str(action),
                            "responsable": "Non assigné",
                            "echeance": "Non définie",
                            "contexte": "",
                            "dependances": ""
                        })
                
                if actions_urgentes:
                    dynamic_sections["actionsUrgentes"] = actions_urgentes
                if actions_reguliers:
                    dynamic_sections["actionsReguliers"] = actions_reguliers
            
            # Handle risks
            if analysis_data.get("risques"):
                cleaned_risks = []
                for risk in analysis_data["risques"]:
                    if isinstance(risk, dict) and "risque" in risk:
                        cleaned_risk = {
                            "risque": str(risk.get("risque", "")).strip(),
                            "categorie": risk.get("categorie", "Général"),
                            "impact": str(risk.get("impact", "Non spécifié")).strip(),
                            "probabilite": str(risk.get("probabilite", "Moyenne")).strip(),
                            "mitigations": str(risk.get("mitigation", risk.get("mitigations", "Non spécifié"))).strip(),
                            "responsableRisque": str(risk.get("responsable", risk.get("responsableRisque", "Non assigné"))).strip(),
                            "echeanceAction": risk.get("echeanceAction", "Non définie")
                        }
                        if cleaned_risk["risque"]:
                            cleaned_risks.append(cleaned_risk)
                
                if cleaned_risks:
                    dynamic_sections["risquesEtMitigations"] = cleaned_risks
            
            analysis_data["sectionsDynamiques"] = dynamic_sections
            analysis_data["vueChronologique"] = []
            analysis_data["analysisMetrics"] = {
                "totalSegments": 0,
                "segmentsAnalyses": 0,
                "niveauDetaille": "Converti de l'ancien format",
                "couvertureSujets": "Partielle",
                "qualiteExtraction": "Bon"
            }
        
        return analysis_data
    
    def _create_fallback_analysis(
        self, 
        transcript_segments: List[Dict[str, Any]], 
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback analysis when AI service is not available"""
        logger.warning("Creating fallback analysis")
        
        # Extract basic info from transcript
        total_text = " ".join([seg.get("text", "") for seg in transcript_segments])
        word_count = len(total_text.split())
        speakers = list(set([seg.get("speaker", "UNKNOWN") for seg in transcript_segments]))
        
        return {
            "meta": {
                "projectName": meeting_metadata.get("project_name", "Projet BTP"),
                "meetingTitle": meeting_metadata.get("title", "Réunion"),
                "meetingDate": meeting_metadata.get("date", ""),
                "duration": meeting_metadata.get("duration", 0),
                "participantsDetected": speakers
            },
            "objectifs": ["[Analyse IA non disponible - Quota dépassé]"],
            "problemes": [],
            "decisions": [],
            "actions": [
                {
                    "tache": "Configurer l'analyse IA pour extraire automatiquement les informations",
                    "responsable": "Administrateur système",
                    "echeance": "Prochaine réunion"
                }
            ],
            "risques": [
                {
                    "risque": "Analyse manuelle requise sans IA",
                    "impact": "Perte de temps et risque d'omission d'informations",
                    "mitigation": "Configuration des services IA"
                }
            ],
            "pointsTechniquesBTP": [],
            "planning": [],
            "budget_chiffrage": [],
            "divers": [
                f"Transcription disponible ({word_count} mots)",
                f"Participants détectés: {', '.join(speakers)}"
            ],
            "exclusions": [],
            "fullTranscriptRef": "transcript.json"
        }
