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
        Analyze meeting transcript and extract structured information using chunked analysis
        """
        if not self.client:
            return self._create_fallback_analysis(transcript_segments, meeting_metadata)
        
        try:
            # Use chunked analysis for better detail and consistency
            chunk_analyses = self._analyze_in_chunks(transcript_segments, meeting_metadata)
            
            if not chunk_analyses:
                logger.warning("No chunk analyses produced, falling back to single analysis")
                return self._single_analysis_fallback(transcript_segments, meeting_metadata)
            
            # Merge all chunk analyses into a comprehensive report
            merged_analysis = self._merge_analyses(chunk_analyses, meeting_metadata)
            
            logger.info(f"Meeting analysis completed successfully with {len(chunk_analyses)} chunks")
            return merged_analysis
            
        except Exception as e:
            logger.error(f"Chunked analysis failed: {e}")
            return self._single_analysis_fallback(transcript_segments, meeting_metadata)
    
    def _analyze_in_chunks(
        self, 
        transcript_segments: List[Dict[str, Any]], 
        meeting_metadata: Dict[str, Any],
        chunk_duration_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Analyze meeting transcript by splitting it into chunks and analyzing each separately
        
        Args:
            transcript_segments: List of transcript segments
            meeting_metadata: Meeting metadata
            chunk_duration_minutes: Duration of each chunk in minutes (default: 15)
            
        Returns:
            List of analysis results for each chunk
        """
        chunk_duration_seconds = chunk_duration_minutes * 60
        chunks = []
        chunk_analyses = []
        
        # Group segments into chunks by time
        current_chunk = []
        current_chunk_start = 0
        
        for segment in transcript_segments:
            start_time = segment.get("start_time", 0)
            
            # If this segment starts a new chunk
            if start_time >= current_chunk_start + chunk_duration_seconds and current_chunk:
                chunks.append({
                    "segments": current_chunk,
                    "start_time": current_chunk_start,
                    "end_time": start_time,
                    "chunk_number": len(chunks) + 1
                })
                current_chunk = []
                current_chunk_start = start_time
            
            current_chunk.append(segment)
        
        # Add the last chunk if it has content
        if current_chunk:
            last_segment = current_chunk[-1]
            end_time = last_segment.get("start_time", 0) + last_segment.get("duration", 60)
            chunks.append({
                "segments": current_chunk,
                "start_time": current_chunk_start,
                "end_time": end_time,
                "chunk_number": len(chunks) + 1
            })
        
        # Analyze each chunk separately
        for chunk in chunks:
            chunk_metadata = meeting_metadata.copy()
            chunk_metadata['chunk_info'] = {
                'chunk_number': chunk['chunk_number'],
                'total_chunks': len(chunks),
                'start_time': chunk['start_time'],
                'end_time': chunk['end_time'],
                'duration_minutes': (chunk['end_time'] - chunk['start_time']) / 60
            }
            
            try:
                chunk_analysis = self._analyze_single_chunk(chunk['segments'], chunk_metadata)
                if chunk_analysis:
                    chunk_analyses.append(chunk_analysis)
                    logger.info(f"Successfully analyzed chunk {chunk['chunk_number']}/{len(chunks)}")
            except Exception as e:
                logger.error(f"Failed to analyze chunk {chunk['chunk_number']}: {e}")
                # Continue with other chunks even if one fails
                continue
        
        return chunk_analyses
    
    def _analyze_single_chunk(
        self, 
        chunk_segments: List[Dict[str, Any]], 
        chunk_metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a single chunk of transcript segments
        """
        if not chunk_segments:
            return None
            
        # Format chunk transcript
        chunk_transcript = self._format_transcript_for_analysis(chunk_segments)
        
        # Create specialized prompt for chunk analysis
        prompt = self._create_chunk_analysis_prompt(chunk_transcript, chunk_metadata)
        
        # Call OpenAI API with chunk-specific settings
        ai_instructions = chunk_metadata.get('ai_instructions', '')
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": self._get_chunk_analysis_system_prompt(ai_instructions)
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,  # Très déterministe pour la cohérence
            max_tokens=8000   # Limite raisonnable par chunk
        )
        
        # Parse and validate response
        analysis_text = response.choices[0].message.content
        analysis_data = json.loads(analysis_text)
        
        # Add chunk metadata to analysis
        analysis_data['chunk_meta'] = chunk_metadata['chunk_info']
        
        return self._validate_and_clean_analysis(analysis_data)
    
    def _single_analysis_fallback(
        self, 
        transcript_segments: List[Dict[str, Any]], 
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback to single analysis when chunked analysis fails
        """
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
                temperature=0.1,
                max_tokens=12000
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            analysis_data = json.loads(analysis_text)
            
            # Validate and clean analysis
            cleaned_analysis = self._validate_and_clean_analysis(analysis_data)
            
            return cleaned_analysis
            
        except Exception as e:
            logger.error(f"Single analysis fallback failed: {e}")
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
    
    def _get_chunk_analysis_system_prompt(self, user_instructions: str = None) -> str:
        """Get system prompt optimized for chunk analysis"""
        base_prompt = """Tu es un expert en analyse de réunions BTP. Tu analyses un SEGMENT spécifique d'une réunion pour extraire TOUS les détails importants de cette portion.

CONTEXTE PARTICULIER - ANALYSE PAR SEGMENT:
- Tu reçois seulement une partie (chunk) d'une réunion plus longue
- Ton objectif: extraire TOUS les détails de ce segment avec un maximum de précision
- Ne pas essayer de déduire ce qui s'est passé avant ou après ce segment
- Se concentrer uniquement sur le contenu de cette portion temporelle

PRINCIPES POUR L'ANALYSE DE SEGMENT:
- Extraire TOUS les détails techniques mentionnés dans ce segment
- Capturer TOUTES les décisions prises ou évoquées dans cette portion
- Identifier TOUS les points d'action évoqués dans ce créneau
- Noter TOUS les problèmes soulevés durant cette période
- Documenter TOUS les aspects budgétaires/planning de ce segment
- Être EXHAUSTIF sur cette portion même si elle semble répétitive"""

        user_specific_guidance = ""
        if user_instructions and user_instructions.strip():
            user_specific_guidance = f"""

INSTRUCTIONS SPÉCIFIQUES DE L'UTILISATEUR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{user_instructions.strip()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: Respecte ces instructions dans l'analyse de ce segment particulier."""

        return f"""{base_prompt}

{user_specific_guidance}

QUALITÉ REQUISE POUR CE SEGMENT:
- Être EXHAUSTIF sur cette portion temporelle
- Être PRÉCIS sur les détails de ce créneau
- Ne pas omettre d'informations parce qu'elles semblent répétitives
- Capturer même les nuances et sous-entendus de ce segment

FORMAT JSON REQUIS:
- Même structure que l'analyse complète mais focalisée sur ce segment
- Toutes les sections présentes même si certaines sont vides pour ce chunk
- Indiquer dans chaque élément qu'il provient de ce segment temporel spécifique"""

    def _create_chunk_analysis_prompt(self, chunk_transcript: str, chunk_metadata: Dict[str, Any]) -> str:
        """Create analysis prompt specifically for a chunk"""
        chunk_info = chunk_metadata.get('chunk_info', {})
        chunk_number = chunk_info.get('chunk_number', 1)
        total_chunks = chunk_info.get('total_chunks', 1)
        start_time = chunk_info.get('start_time', 0)
        end_time = chunk_info.get('end_time', 0)
        
        start_minutes = int(start_time // 60)
        start_seconds = int(start_time % 60)
        end_minutes = int(end_time // 60)
        end_seconds = int(end_time % 60)
        
        ai_instructions = chunk_metadata.get('ai_instructions', '')
        instructions_display = f"\n📋 Instructions utilisateur: {ai_instructions}" if ai_instructions and ai_instructions.strip() else ""
        
        return f"""Tu analyses le SEGMENT {chunk_number}/{total_chunks} d'une réunion BTP.

INFORMATIONS SUR CE SEGMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Projet: {chunk_metadata.get('project_name', 'Non spécifié')}
📝 Titre: {chunk_metadata.get('title', 'Non spécifié')}
⏱️ Segment temporel: [{start_minutes:02d}:{start_seconds:02d}] - [{end_minutes:02d}:{end_seconds:02d}]
🔢 Segment: {chunk_number} sur {total_chunks} au total
📅 Date: {chunk_metadata.get('date', 'Non spécifié')}{instructions_display}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MISSION POUR CE SEGMENT:
🎯 Extraire TOUS les détails de cette portion temporelle uniquement
🎯 Capturer TOUTES les informations même si elles semblent redondantes
🎯 Se concentrer sur cette tranche horaire spécifique: [{start_minutes:02d}:{start_seconds:02d}] - [{end_minutes:02d}:{end_seconds:02d}]
🎯 Ne pas essayer de faire du lien avec le reste de la réunion

TRANSCRIPTION DU SEGMENT À ANALYSER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chunk_transcript}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyse EXHAUSTIVEMENT ce segment en respectant la même structure JSON que pour une analyse complète:
{{
  "meta": {{
    "segmentNumber": {chunk_number},
    "totalSegments": {total_chunks},
    "timeRange": "[{start_minutes:02d}:{start_seconds:02d}] - [{end_minutes:02d}:{end_seconds:02d}]",
    "projectName": "{chunk_metadata.get('project_name', 'Non spécifié')}",
    "meetingTitle": "{chunk_metadata.get('title', 'Non spécifié')}",
    "userInstructions": "{ai_instructions}"
  }},
  "sectionsDynamiques": {{
    // Créer toutes les sections nécessaires selon le contenu de CE SEGMENT
    // Même structure que l'analyse complète mais focalisée sur cette portion
  }},
  "vueChronologique": [
    // Séquence des événements dans ce segment uniquement
    "[{start_minutes:02d}:{start_seconds:02d}-XX:XX] Description de ce qui se passe dans cette sous-période"
  ],
  "analysisMetrics": {{
    "segmentAnalyzed": {chunk_number},
    "timeRangeMinutes": "{(end_time - start_time) / 60:.1f}",
    "niveauDetaille": "Très élevé/Élevé/Moyen",
    "qualiteSegment": "Riche/Moyen/Pauvre en informations"
  }}
}}

🚨 IMPORTANT: Extrais TOUT de ce segment, même les détails qui pourraient sembler répétitifs par rapport à d'autres segments."""
    
    def _merge_analyses(
        self, 
        chunk_analyses: List[Dict[str, Any]], 
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge multiple chunk analyses into a single comprehensive analysis
        Eliminates exact duplicates while preserving all unique technical details
        """
        if not chunk_analyses:
            return self._create_fallback_analysis([], meeting_metadata)
        
        # If only one chunk, return it directly but clean up the format
        if len(chunk_analyses) == 1:
            return self._format_single_chunk_as_full_analysis(chunk_analyses[0], meeting_metadata)
        
        # Initialize merged analysis structure
        merged = {
            "meta": self._merge_meta_sections(chunk_analyses, meeting_metadata),
            "sectionsDynamiques": {},
            "vueChronologique": [],
            "analysisMetrics": self._merge_analysis_metrics(chunk_analyses)
        }
        
        # Merge dynamic sections
        merged["sectionsDynamiques"] = self._merge_dynamic_sections(chunk_analyses)
        
        # Merge chronological view
        merged["vueChronologique"] = self._merge_chronological_views(chunk_analyses)
        
        logger.info(f"Successfully merged {len(chunk_analyses)} chunk analyses into comprehensive report")
        return merged
    
    def _merge_meta_sections(
        self, 
        chunk_analyses: List[Dict[str, Any]], 
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge meta information from all chunks"""
        # Use meeting metadata as base and enrich with chunk information
        participants_detected = meeting_metadata.get('participants', [])
        expected_speakers = meeting_metadata.get('expected_speakers', len(participants_detected))
        ai_instructions = meeting_metadata.get('ai_instructions', '')
        duration_minutes = meeting_metadata.get('duration', 0)
        
        # Calculate total analysis coverage
        total_chunks = len(chunk_analyses)
        time_ranges = []
        
        for analysis in chunk_analyses:
            chunk_meta = analysis.get('chunk_meta', {})
            if chunk_meta:
                start = chunk_meta.get('start_time', 0)
                end = chunk_meta.get('end_time', 0)
                time_ranges.append((start, end))
        
        coverage_analysis = ""
        if time_ranges:
            total_covered_time = sum(end - start for start, end in time_ranges)
            coverage_percentage = (total_covered_time / (duration_minutes * 60)) * 100 if duration_minutes > 0 else 0
            coverage_analysis = f"Analyse par chunks: {total_chunks} segments couvrant {coverage_percentage:.1f}% de la réunion"
        
        return {
            "projectName": meeting_metadata.get('project_name', 'Non spécifié'),
            "meetingTitle": meeting_metadata.get('title', 'Non spécifié'),
            "meetingType": self._deduce_meeting_type(ai_instructions),
            "meetingDate": meeting_metadata.get('date', 'Non spécifié'),
            "duration": duration_minutes,
            "participantsExpected": expected_speakers,
            "participantsDetected": participants_detected,
            "userInstructions": ai_instructions,
            "analysisMethod": "Analyse par chunks avec fusion intelligente",
            "chunksAnalyzed": total_chunks,
            "coverageAnalysis": coverage_analysis
        }
    
    def _merge_dynamic_sections(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge dynamic sections from all chunks, eliminating duplicates"""
        merged_sections = {}
        
        # Collect all unique section names across chunks
        all_section_names = set()
        for analysis in chunk_analyses:
            sections = analysis.get('sectionsDynamiques', {})
            all_section_names.update(sections.keys())
        
        # For each section type, merge content from all chunks
        for section_name in all_section_names:
            merged_sections[section_name] = self._merge_section_content(
                section_name, chunk_analyses
            )
        
        # Remove empty sections
        return {k: v for k, v in merged_sections.items() if v}
    
    def _merge_section_content(self, section_name: str, chunk_analyses: List[Dict[str, Any]]) -> List:
        """Merge content for a specific section across all chunks"""
        all_items = []
        seen_items = set()  # For deduplication
        
        for analysis in chunk_analyses:
            sections = analysis.get('sectionsDynamiques', {})
            section_content = sections.get(section_name, [])
            
            if not isinstance(section_content, list):
                continue
                
            chunk_info = analysis.get('chunk_meta', {})
            chunk_number = chunk_info.get('chunk_number', 0)
            time_range = chunk_info.get('start_time', 0), chunk_info.get('end_time', 0)
            
            for item in section_content:
                # Add time context to each item
                enriched_item = self._enrich_item_with_context(item, chunk_number, time_range)
                
                # Create a key for deduplication
                dedup_key = self._create_deduplication_key(enriched_item)
                
                if dedup_key not in seen_items:
                    seen_items.add(dedup_key)
                    all_items.append(enriched_item)
                else:
                    # If similar item exists, merge additional details
                    self._merge_similar_items(all_items, enriched_item, dedup_key)
        
        return all_items
    
    def _enrich_item_with_context(self, item: Any, chunk_number: int, time_range: tuple) -> Any:
        """Add temporal context to items"""
        start_time, end_time = time_range
        start_minutes = int(start_time // 60)
        start_seconds = int(start_time % 60)
        end_minutes = int(end_time // 60) 
        end_seconds = int(end_time % 60)
        time_context = f"[{start_minutes:02d}:{start_seconds:02d}-{end_minutes:02d}:{end_seconds:02d}]"
        
        if isinstance(item, dict):
            # For structured items (like actions, risks), add time context
            enriched = item.copy()
            if 'contexte' in enriched:
                enriched['contexte'] = f"{time_context} {enriched['contexte']}"
            else:
                enriched['contexteTemporel'] = time_context
            return enriched
        else:
            # For string items, prepend time context
            return f"{time_context} {str(item)}"
    
    def _create_deduplication_key(self, item: Any) -> str:
        """Create a key for deduplication based on content"""
        if isinstance(item, dict):
            # For structured items, use main content fields
            if 'action' in item:
                return f"action:{item.get('action', '')}:{item.get('responsable', '')}"
            elif 'risque' in item:
                return f"risque:{item.get('risque', '')}:{item.get('categorie', '')}"
            else:
                # Generic approach for other dict items
                main_keys = ['titre', 'description', 'probleme', 'decision', 'point']
                for key in main_keys:
                    if key in item:
                        return f"{key}:{str(item[key])[:100]}"
                return str(item)[:100]
        else:
            # For string items, use content without time prefix for comparison
            content = str(item)
            # Remove time context for comparison
            if content.startswith('[') and ']' in content:
                content = content.split(']', 1)[1].strip()
            return content[:100]
    
    def _merge_similar_items(self, all_items: List, new_item: Any, dedup_key: str):
        """Merge details from similar items to enrich existing ones"""
        # Find the existing item with the same dedup_key
        for i, existing_item in enumerate(all_items):
            if self._create_deduplication_key(existing_item) == dedup_key:
                if isinstance(existing_item, dict) and isinstance(new_item, dict):
                    # Merge dictionary items by combining unique information
                    merged = existing_item.copy()
                    
                    # Combine context information
                    existing_context = merged.get('contexte', merged.get('contexteTemporel', ''))
                    new_context = new_item.get('contexte', new_item.get('contexteTemporel', ''))
                    
                    if new_context and new_context not in existing_context:
                        merged['contexte'] = f"{existing_context} | {new_context}"
                    
                    # Merge other fields that might have additional information
                    for key, value in new_item.items():
                        if key not in merged or not merged[key]:
                            merged[key] = value
                        elif key not in ['contexte', 'contexteTemporel'] and str(value) not in str(merged[key]):
                            # Combine values if they're different
                            merged[key] = f"{merged[key]} | {value}"
                    
                    all_items[i] = merged
                break
    
    def _merge_chronological_views(self, chunk_analyses: List[Dict[str, Any]]) -> List[str]:
        """Merge chronological views from all chunks in temporal order"""
        all_events = []
        
        for analysis in chunk_analyses:
            chunk_events = analysis.get('vueChronologique', [])
            chunk_meta = analysis.get('chunk_meta', {})
            chunk_number = chunk_meta.get('chunk_number', 0)
            
            for event in chunk_events:
                if isinstance(event, str):
                    all_events.append({
                        'event': event,
                        'chunk': chunk_number,
                        'original_time': self._extract_time_from_event(event)
                    })
        
        # Sort events by time
        all_events.sort(key=lambda x: x['original_time'])
        
        # Return just the event descriptions in chronological order
        return [event['event'] for event in all_events]
    
    def _extract_time_from_event(self, event: str) -> float:
        """Extract timestamp from chronological event string"""
        import re
        # Look for patterns like [MM:SS] or [MM:SS-MM:SS]
        time_pattern = r'\[(\d{1,2}):(\d{2})'
        match = re.search(time_pattern, event)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        return 0
    
    def _merge_analysis_metrics(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge analysis metrics from all chunks"""
        total_segments = sum(
            analysis.get('analysisMetrics', {}).get('totalSegments', 0) 
            for analysis in chunk_analyses
        )
        
        analyzed_segments = sum(
            analysis.get('analysisMetrics', {}).get('segmentsAnalyses', 0) 
            for analysis in chunk_analyses
        )
        
        # Determine overall quality level
        quality_levels = [
            analysis.get('analysisMetrics', {}).get('qualiteExtraction', 'Moyen')
            for analysis in chunk_analyses
        ]
        
        # Map quality to numeric values for averaging
        quality_map = {'Excellent': 4, 'Bon': 3, 'Moyen': 2, 'Insuffisant': 1}
        reverse_quality_map = {4: 'Excellent', 3: 'Bon', 2: 'Moyen', 1: 'Insuffisant'}
        
        avg_quality = sum(quality_map.get(q, 2) for q in quality_levels) / len(quality_levels)
        overall_quality = reverse_quality_map[round(avg_quality)]
        
        return {
            "totalSegments": total_segments,
            "segmentsAnalyses": analyzed_segments,
            "chunksProcessed": len(chunk_analyses),
            "niveauDetaille": "Très élevé (analyse par chunks)",
            "couvertureSujets": "Exhaustive (fusion intelligente)",
            "qualiteExtraction": overall_quality,
            "methodologie": "Analyse segmentée avec déduplication et fusion contextuelle"
        }
    
    def _format_single_chunk_as_full_analysis(
        self, 
        chunk_analysis: Dict[str, Any], 
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format a single chunk analysis as a complete meeting analysis"""
        # Remove chunk-specific metadata and reformat as full analysis
        formatted = chunk_analysis.copy()
        
        # Update meta to reflect full meeting context
        formatted["meta"] = self._merge_meta_sections([chunk_analysis], meeting_metadata)
        
        # Update analysis metrics
        if "analysisMetrics" in formatted:
            formatted["analysisMetrics"]["methodologie"] = "Analyse complète (réunion courte)"
            formatted["analysisMetrics"]["chunksProcessed"] = 1
        
        # Clean up chunk-specific fields
        if "chunk_meta" in formatted:
            del formatted["chunk_meta"]
        
        return formatted
    
    def _deduce_meeting_type(self, ai_instructions: str) -> str:
        """Deduce meeting type from AI instructions"""
        if not ai_instructions:
            return "Autre"
            
        ai_lower = ai_instructions.lower()
        if "chantier" in ai_lower:
            return "Réunion de chantier"
        elif "avancement" in ai_lower or "suivi" in ai_lower:
            return "Point d'avancement"
        elif "coordination" in ai_lower:
            return "Réunion de coordination"
        elif "sécurité" in ai_lower:
            return "Réunion sécurité"
        elif "livraison" in ai_lower:
            return "Réunion de livraison"
        else:
            return "Réunion personnalisée"
    
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
