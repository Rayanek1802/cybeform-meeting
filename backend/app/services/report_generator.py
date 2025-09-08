"""
Report generation service using python-docx
"""
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_BREAK
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating Word reports"""
    
    def __init__(self):
        self.brand_primary = RGBColor(0x4F, 0x46, 0xE5)  # Indigo
        self.brand_secondary = RGBColor(0x7C, 0x3A, 0xED)  # Purple
        self.brand_accent = RGBColor(0x06, 0xB6, 0xD4)  # Cyan
    
    def generate_report(
        self, 
        analysis_data: Dict[str, Any], 
        transcript_segments: List[Dict[str, Any]],
        meeting_metadata: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Generate complete Word report
        """
        try:
            doc = Document()
            
            # Ensure document is not protected or restricted
            doc.settings.odd_and_even_pages_header_footer = False
            doc.settings.different_first_page_header_footer = False
            
            # Configure document
            self._setup_document_styles(doc)
            
            # Generate content
            self._add_cover_page(doc, analysis_data, meeting_metadata)
            self._add_page_break(doc)
            self._add_table_of_contents(doc, analysis_data)
            self._add_page_break(doc)
            self._add_main_content(doc, analysis_data)
            self._add_page_break(doc)
            self._add_transcript_appendix(doc, transcript_segments)
            
            # Add headers and footers
            self._add_headers_footers(doc, meeting_metadata)
            
            # Save document
            doc.save(output_path)
            
            # Set file permissions to allow modification (666 = rw-rw-rw-)
            try:
                os.chmod(output_path, 0o666)
                logger.info(f"Report generated successfully with write permissions: {output_path}")
            except Exception as e:
                logger.warning(f"Could not set file permissions: {e}")
                logger.info(f"Report generated successfully: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False
    
    def _setup_document_styles(self, doc: Document):
        """Setup custom styles for the document"""
        styles = doc.styles
        
        # Main title style
        try:
            title_style = styles['Title']
        except KeyError:
            title_style = styles.add_style('Title', WD_STYLE_TYPE.PARAGRAPH)
        
        title_style.font.name = 'Arial'
        title_style.font.size = Pt(24)
        title_style.font.color.rgb = self.brand_primary
        title_style.font.bold = True
        
        # Heading styles
        for level in [1, 2, 3]:
            try:
                heading_style = styles[f'Heading {level}']
            except KeyError:
                heading_style = styles.add_style(f'Heading {level}', WD_STYLE_TYPE.PARAGRAPH)
            
            heading_style.font.name = 'Arial'
            heading_style.font.size = Pt(16 - level * 2)
            heading_style.font.color.rgb = self.brand_primary
            heading_style.font.bold = True
            heading_style.paragraph_format.space_before = Pt(12)
            heading_style.paragraph_format.space_after = Pt(6)
    
    def _add_cover_page(self, doc: Document, analysis_data: Dict[str, Any], meeting_metadata: Dict[str, Any]):
        """Add cover page"""
        # Logo/Brand
        title_para = doc.add_paragraph()
        title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        title_run = title_para.add_run("CybeMeeting")
        title_run.font.name = 'Arial'
        title_run.font.size = Pt(28)
        title_run.font.color.rgb = self.brand_primary
        title_run.font.bold = True
        
        # Subtitle
        subtitle_para = doc.add_paragraph()
        subtitle_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        subtitle_run = subtitle_para.add_run("Rapport de Réunion BTP")
        subtitle_run.font.name = 'Arial'
        subtitle_run.font.size = Pt(18)
        subtitle_run.font.color.rgb = self.brand_secondary
        
        # Spacing
        doc.add_paragraph("\n\n")
        
        # Meeting info
        meta = analysis_data.get("meta", {})
        info_lines = [
            f"Projet: {meta.get('projectName', 'Non spécifié')}",
            f"Type de réunion: {meta.get('meetingType', 'Autre')}",
            f"Réunion: {meta.get('meetingTitle', 'Non spécifié')}",
            f"Date: {meta.get('meetingDate', 'Non spécifié')}",
            f"Durée: {meta.get('duration', 0)} minutes",
            f"Participants détectés: {', '.join(meta.get('participantsDetected', []))}",
            f"Participants attendus: {meta.get('participantsExpected', 'Non spécifié')}"
        ]
        
        for line in info_lines:
            para = doc.add_paragraph(line)
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            para.runs[0].font.size = Pt(14)
        
        # Generation date
        doc.add_paragraph("\n\n")
        gen_para = doc.add_paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        gen_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        gen_para.runs[0].font.size = Pt(10)
        gen_para.runs[0].font.italic = True
    
    def _add_table_of_contents(self, doc: Document, analysis_data: Dict[str, Any]):
        """Add dynamic table of contents based on actual sections"""
        toc_para = doc.add_paragraph("SOMMAIRE", style='Heading 1')
        toc_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Always include general information
        toc_items = ["1. Informations générales"]
        
        # Generate TOC based on actual content
        if "sectionsDynamiques" in analysis_data:
            sections_data = analysis_data.get("sectionsDynamiques", {})
            
            # Define section order and French titles
            section_mappings = {
                "etatLieux": "État des lieux",
                "avancementTravaux": "Avancement des travaux", 
                "problemesIdentifies": "Problèmes identifiés",
                "decisionsStrategiques": "Décisions stratégiques",
                "objectifs": "Objectifs de la réunion",
                "actionsUrgentes": "Actions urgentes",
                "actionsReguliers": "Actions de suivi",
                "aspectsTechniques": "Aspects techniques",
                "planningEtDelais": "Planning et délais",
                "aspectsFinanciers": "Aspects financiers",
                "relationsFournisseurs": "Relations fournisseurs",
                "aspectsReglementaires": "Aspects réglementaires", 
                "communicationClient": "Communication client",
                "risquesEtMitigations": "Risques et mitigations",
                "pointsDivers": "Points divers",
                "syntheseDesAccords": "Synthèse des accords",
                "pointsEnSuspens": "Points en suspens"
            }
            
            section_counter = 2
            for section_key, title in section_mappings.items():
                if section_key in sections_data and sections_data[section_key]:
                    toc_items.append(f"{section_counter}. {title}")
                    section_counter += 1
            
            # Add chronological view if available
            if analysis_data.get("vueChronologique"):
                toc_items.append(f"{section_counter}. Vue chronologique de la réunion")
                section_counter += 1
            
            # Add analysis metrics if available
            if analysis_data.get("analysisMetrics"):
                toc_items.append(f"{section_counter}. Métriques d'analyse")
        else:
            # Fallback to legacy TOC
            toc_items.extend([
                "2. Objectifs de la réunion",
                "3. Problèmes identifiés", 
                "4. Décisions prises",
                "5. Plan d'actions",
                "6. Analyse des risques",
                "7. Points techniques BTP",
                "8. Planning et jalons",
                "9. Budget et chiffrage",
                "10. Informations diverses"
            ])
        
        # Add ANNEXE
        toc_items.append("ANNEXE - Transcription complète")
        
        for item in toc_items:
            para = doc.add_paragraph(item)
            para.paragraph_format.left_indent = Inches(0.5)
            para.paragraph_format.space_after = Pt(6)
    
    def _add_main_content(self, doc: Document, analysis_data: Dict[str, Any]):
        """Add main content sections with dynamic structure support"""
        # 1. Always start with general information
        self._add_general_information(doc, analysis_data.get("meta", {}))
        
        # Check if we have dynamic sections (new format)
        if "sectionsDynamiques" in analysis_data:
            self._add_dynamic_sections(doc, analysis_data)
        else:
            # Fallback to old format
            self._add_legacy_sections(doc, analysis_data)
        
        # Add chronological view if available
        if analysis_data.get("vueChronologique"):
            self._add_chronological_view_word(doc, analysis_data.get("vueChronologique", []))
        
        # Add analysis metrics if available
        if analysis_data.get("analysisMetrics"):
            self._add_analysis_metrics_word(doc, analysis_data.get("analysisMetrics", {}))
    
    def _add_dynamic_sections(self, doc: Document, analysis_data: Dict[str, Any]):
        """Add dynamic sections based on actual meeting content"""
        sections_data = analysis_data.get("sectionsDynamiques", {})
        
        # Define section order and French titles
        section_mappings = {
            "etatLieux": "2. État des lieux",
            "avancementTravaux": "3. Avancement des travaux", 
            "problemesIdentifies": "4. Problèmes identifiés",
            "decisionsStrategiques": "5. Décisions stratégiques",
            "objectifs": "6. Objectifs de la réunion",
            "actionsUrgentes": "7. Actions urgentes",
            "actionsReguliers": "8. Actions de suivi",
            "aspectsTechniques": "9. Aspects techniques",
            "planningEtDelais": "10. Planning et délais",
            "aspectsFinanciers": "11. Aspects financiers",
            "relationsFournisseurs": "12. Relations fournisseurs",
            "aspectsReglementaires": "13. Aspects réglementaires", 
            "communicationClient": "14. Communication client",
            "risquesEtMitigations": "15. Risques et mitigations",
            "pointsDivers": "16. Points divers",
            "syntheseDesAccords": "17. Synthèse des accords",
            "pointsEnSuspens": "18. Points en suspens"
        }
        
        section_counter = 2  # Start after general info
        
        # Process sections in logical order
        for section_key, default_title in section_mappings.items():
            if section_key in sections_data and sections_data[section_key]:
                content = sections_data[section_key]
                
                # Use numbered title
                numbered_title = f"{section_counter}. {default_title.split('. ', 1)[1]}"
                
                # Handle different content types
                if section_key in ["actionsUrgentes", "actionsReguliers"]:
                    self._add_actions_table(doc, content, numbered_title)
                elif section_key == "risquesEtMitigations":
                    self._add_risks_table(doc, content, numbered_title)
                else:
                    self._add_section(doc, numbered_title, content)
                
                section_counter += 1
        
        # Add any custom sections not in the predefined list
        for section_key, content in sections_data.items():
            if section_key not in section_mappings and content:
                # Format custom section name
                custom_title = f"{section_counter}. {section_key.replace('_', ' ').title()}"
                self._add_section(doc, custom_title, content)
                section_counter += 1
    
    def _add_legacy_sections(self, doc: Document, analysis_data: Dict[str, Any]):
        """Add sections using legacy format for backward compatibility"""
        # 2. Objectives
        self._add_section(doc, "2. Objectifs de la réunion", analysis_data.get("objectifs", []))
        
        # 3. Problems
        self._add_section(doc, "3. Problèmes identifiés", analysis_data.get("problemes", []))
        
        # 4. Decisions
        self._add_section(doc, "4. Décisions prises", analysis_data.get("decisions", []))
        
        # 5. Actions (table format)
        self._add_actions_table(doc, analysis_data.get("actions", []), "5. Plan d'actions")
        
        # 6. Risks (table format)
        self._add_risks_table(doc, analysis_data.get("risques", []), "6. Analyse des risques")
        
        # 7. Technical points
        self._add_section(doc, "7. Points techniques BTP", analysis_data.get("pointsTechniquesBTP", []))
        
        # 8. Planning
        self._add_section(doc, "8. Planning et jalons", analysis_data.get("planning", []))
        
        # 9. Budget
        self._add_section(doc, "9. Budget et chiffrage", analysis_data.get("budget_chiffrage", []))
        
        # 10. Miscellaneous
        self._add_section(doc, "10. Informations diverses", analysis_data.get("divers", []))
        
        # Exclusions (if any)
        exclusions = analysis_data.get("exclusions", [])
        if exclusions:
            self._add_section(doc, "Éléments non retenus", exclusions)
    
    def _add_chronological_view(self, doc: Document, chronological_data: List[str]):
        """Add chronological timeline of the meeting"""
        if not chronological_data:
            return
            
        doc.add_heading("Vue chronologique de la réunion", level=1)
        
        for event in chronological_data:
            if event and not event.startswith("/*"):
                para = doc.add_paragraph()
                para.style = 'List Bullet'
                para.add_run(event)
    
    def _add_analysis_metrics(self, doc: Document, metrics: Dict[str, Any]):
        """Add analysis quality metrics"""
        if not metrics:
            return
            
        doc.add_heading("Métriques d'analyse", level=1)
        
        metrics_text = [
            f"Segments analysés: {metrics.get('segmentsAnalyses', 0)}/{metrics.get('totalSegments', 0)}",
            f"Niveau de détail: {metrics.get('niveauDetaille', 'Non spécifié')}",
            f"Couverture des sujets: {metrics.get('couvertureSujets', 'Non spécifié')}",
            f"Qualité d'extraction: {metrics.get('qualiteExtraction', 'Non spécifié')}"
        ]
        
        for metric in metrics_text:
            para = doc.add_paragraph()
            para.style = 'List Bullet'
            para.add_run(metric)
    
    def _add_section(self, doc: Document, title: str, content, content_type: str = "list"):
        """Add a content section with enhanced formatting"""
        # Add title
        doc.add_heading(title, level=1)
        
        if content_type == "dict":
            # Handle dictionary content (meta info)
            if not content:
                doc.add_paragraph("Aucune information disponible.")
                return
            
            for key, value in content.items():
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                para = doc.add_paragraph(f"{key}: {value}")
        
        elif content_type == "list":
            # Handle list content
            if not content:
                doc.add_paragraph("Aucun élément identifié.")
                return
            
            # Check if content contains structured data (dictionaries)
            if any(isinstance(item, dict) for item in content):
                self._add_structured_content_table(doc, content)
            else:
                # Simple list items
                for item in content:
                    para = doc.add_paragraph(self._format_content_item(item), style='List Bullet')
        
        doc.add_paragraph()  # Add spacing
    
    def _add_structured_content_table(self, doc: Document, content: List[Dict[str, Any]]):
        """Add structured content as a formatted table"""
        if not content:
            return
            
        # Analyze the structure to determine columns
        all_keys = set()
        for item in content:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        # Define column mapping for better presentation
        column_mappings = {
            'description': 'Description',
            'context': 'Contexte', 
            'details': 'Détails',
            'contexteTemporel': 'Période',
            'action': 'Action',
            'responsable': 'Responsable',
            'echeance': 'Échéance',
            'risque': 'Risque',
            'categorie': 'Catégorie',
            'impact': 'Impact',
            'mitigation': 'Mitigation',
            'mitigations': 'Mitigation',
            'probabilite': 'Probabilité'
        }
        
        # Select relevant columns in priority order
        priority_columns = ['description', 'context', 'details', 'contexteTemporel', 'action', 'responsable', 'echeance', 'risque', 'categorie', 'impact', 'mitigation', 'mitigations', 'probabilite']
        selected_columns = []
        
        for col in priority_columns:
            if col in all_keys:
                selected_columns.append(col)
        
        # Add any remaining columns
        for key in sorted(all_keys):
            if key not in selected_columns:
                selected_columns.append(key)
        
        # Limit to 4-5 columns for readability
        selected_columns = selected_columns[:5]
        
        if not selected_columns:
            return
            
        # Create table
        table = doc.add_table(rows=1, cols=len(selected_columns))
        table.style = 'Table Grid'
        table.allow_autofit = True
        
        # Header row
        header_cells = table.rows[0].cells
        for i, col in enumerate(selected_columns):
            header_cells[i].text = column_mappings.get(col, col.title())
            header_cells[i].paragraphs[0].runs[0].font.bold = True
            header_cells[i].paragraphs[0].runs[0].font.color.rgb = self.brand_primary
            header_cells[i].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
            # Add light background to header
            try:
                from docx.oxml.shared import qn
                tcPr = header_cells[i]._tc.get_or_add_tcPr()
                shd = tcPr.find(qn('w:shd'))
                if shd is None:
                    from docx.oxml.parser import parse_xml
                    from docx.oxml.ns import nsdecls
                    shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                    tcPr.append(shd)
            except:
                pass  # Skip background color if it fails
        
        # Data rows
        for item in content:
            if isinstance(item, dict):
                row_cells = table.add_row().cells
                for i, col in enumerate(selected_columns):
                    value = item.get(col, '')
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    
                    # Format the text nicely
                    formatted_value = self._format_content_item(value)
                    row_cells[i].text = formatted_value
                    row_cells[i].paragraphs[0].runs[0].font.size = Pt(10)
                    
                    # Special formatting for time ranges
                    if col == 'contexteTemporel' and value:
                        row_cells[i].paragraphs[0].runs[0].font.name = 'Consolas'
                        row_cells[i].paragraphs[0].runs[0].font.size = Pt(9)
                        row_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(55, 65, 81)
    
    def _format_content_item(self, item):
        """Format a content item for better presentation"""
        if isinstance(item, dict):
            # For dictionary items, create a readable format
            formatted_parts = []
            
            # Priority order for displaying dict fields
            priority_fields = ['description', 'context', 'details', 'action', 'risque']
            other_fields = []
            
            for field in priority_fields:
                if field in item and item[field]:
                    value = str(item[field]).strip()
                    if value:
                        formatted_parts.append(value)
            
            for key, value in item.items():
                if key not in priority_fields and value:
                    value_str = str(value).strip()
                    if value_str and key != 'contexteTemporel':
                        other_fields.append(f"{key}: {value_str}")
            
            # Combine main content with additional details
            result = '. '.join(formatted_parts)
            if other_fields:
                result += f" ({'; '.join(other_fields)})"
            
            return result
        else:
            # For simple items, just clean up the string representation
            item_str = str(item).strip()
            # Remove any Python dict syntax artifacts
            if item_str.startswith('{') and item_str.endswith('}'):
                return "Données non formatées"
            return item_str
    
    def _add_actions_table(self, doc: Document, actions: List[Dict[str, Any]], title: str = "5. Plan d'actions"):
        """Add enhanced actions table with full information"""
        doc.add_heading(title, level=1)
        
        if not actions:
            doc.add_paragraph("Aucune action définie.")
            return
        
        # Create table with 5 columns including Context and Priority
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Table Grid'
        table.allow_autofit = True
        
        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Action'
        header_cells[1].text = 'Responsable'
        header_cells[2].text = 'Échéance'
        header_cells[3].text = 'Priorité'
        header_cells[4].text = 'Contexte'
        
        # Style header
        for cell in header_cells:
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = self.brand_primary
            cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            # Add light background to header
            try:
                from docx.oxml.shared import qn
                tcPr = cell._tc.get_or_add_tcPr()
                shd = tcPr.find(qn('w:shd'))
                if shd is None:
                    from docx.oxml.parser import parse_xml
                    from docx.oxml.ns import nsdecls
                    shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                    tcPr.append(shd)
            except:
                pass  # Skip background color if it fails
        
        # Add action rows
        for action in actions:
            row_cells = table.add_row().cells
            
            # Action description
            action_text = action.get('action', action.get('tache', ''))
            row_cells[0].text = str(action_text)
            row_cells[0].paragraphs[0].runs[0].font.size = Pt(10)
            
            # Responsible person
            row_cells[1].text = str(action.get('responsable', 'Non assigné'))
            
            # Due date
            echeance = action.get('echeance', 'Non définie')
            row_cells[2].text = str(echeance) if echeance else 'Non définie'
            
            # Priority
            priorite = action.get('priorite', 'Moyenne')
            row_cells[3].text = str(priorite)
            
            # Priority color coding
            if str(priorite).lower() in ['haute', 'urgent', 'urgente']:
                row_cells[3].paragraphs[0].runs[0].font.color.rgb = RGBColor(239, 68, 68)  # Red
                row_cells[3].paragraphs[0].runs[0].font.bold = True
            elif str(priorite).lower() in ['moyenne', 'normal', 'normale']:
                row_cells[3].paragraphs[0].runs[0].font.color.rgb = RGBColor(245, 158, 11)  # Orange
            else:
                row_cells[3].paragraphs[0].runs[0].font.color.rgb = RGBColor(16, 185, 129)  # Green
            
            # Context
            contexte = action.get('contexte', action.get('dependances', ''))
            row_cells[4].text = str(contexte) if contexte else 'Non spécifié'
            row_cells[4].paragraphs[0].runs[0].font.size = Pt(9)
        
        doc.add_paragraph()  # Add spacing
    
    def _add_risks_table(self, doc: Document, risks: List[Dict[str, Any]], title: str = "6. Analyse des risques"):
        """Add enhanced risks table with full information"""
        doc.add_heading(title, level=1)
        
        if not risks:
            doc.add_paragraph("Aucun risque identifié.")
            return
        
        # Create table with 6 columns for complete risk information
        table = doc.add_table(rows=1, cols=6)
        table.style = 'Table Grid'
        table.allow_autofit = True
        
        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Risque'
        header_cells[1].text = 'Catégorie'
        header_cells[2].text = 'Probabilité'
        header_cells[3].text = 'Impact'
        header_cells[4].text = 'Mitigation'
        header_cells[5].text = 'Responsable'
        
        # Style header
        for cell in header_cells:
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = self.brand_primary
            cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            # Add light background to header
            try:
                from docx.oxml.shared import qn
                tcPr = cell._tc.get_or_add_tcPr()
                shd = tcPr.find(qn('w:shd'))
                if shd is None:
                    from docx.oxml.parser import parse_xml
                    from docx.oxml.ns import nsdecls
                    shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                    tcPr.append(shd)
            except:
                pass  # Skip background color if it fails
        
        # Add risk rows
        for risk in risks:
            row_cells = table.add_row().cells
            
            # Risk description
            row_cells[0].text = str(risk.get('risque', 'Non spécifié'))
            row_cells[0].paragraphs[0].runs[0].font.size = Pt(10)
            
            # Category
            row_cells[1].text = str(risk.get('categorie', 'Général'))
            
            # Probability with color coding
            probabilite = risk.get('probabilite', 'Moyenne')
            row_cells[2].text = str(probabilite)
            
            # Color code probability
            if str(probabilite).lower() in ['élevée', 'haute', 'high']:
                row_cells[2].paragraphs[0].runs[0].font.color.rgb = RGBColor(239, 68, 68)  # Red
                row_cells[2].paragraphs[0].runs[0].font.bold = True
            elif str(probabilite).lower() in ['moyenne', 'medium']:
                row_cells[2].paragraphs[0].runs[0].font.color.rgb = RGBColor(245, 158, 11)  # Orange
            else:
                row_cells[2].paragraphs[0].runs[0].font.color.rgb = RGBColor(16, 185, 129)  # Green
            
            # Impact
            row_cells[3].text = str(risk.get('impact', 'Non spécifié'))
            row_cells[3].paragraphs[0].runs[0].font.size = Pt(9)
            
            # Mitigation
            mitigation = risk.get('mitigations', risk.get('mitigation', 'Non spécifié'))
            row_cells[4].text = str(mitigation)
            row_cells[4].paragraphs[0].runs[0].font.size = Pt(9)
            
            # Responsible
            responsable = risk.get('responsableRisque', risk.get('responsable', 'Non assigné'))
            row_cells[5].text = str(responsable)
        
        doc.add_paragraph()  # Add spacing
    
    def _add_transcript_appendix(self, doc: Document, transcript_segments: List[Dict[str, Any]]):
        """Add transcript appendix"""
        doc.add_heading("ANNEXE - Transcription complète", level=1)
        
        if not transcript_segments:
            doc.add_paragraph("Transcription non disponible.")
            return
        
        current_speaker = None
        
        for segment in transcript_segments:
            speaker = segment.get("speaker", "INCONNU")
            text = segment.get("text", "").strip()
            start_time = segment.get("start_time", 0)
            
            if not text:
                continue
            
            # Add speaker header if changed
            if speaker != current_speaker:
                if current_speaker is not None:
                    doc.add_paragraph()  # Add spacing between speakers
                
                speaker_para = doc.add_paragraph(f"{speaker}")
                speaker_para.runs[0].font.bold = True
                speaker_para.runs[0].font.color.rgb = self.brand_primary
                current_speaker = speaker
            
            # Add timestamp and text
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            
            para = doc.add_paragraph(f"{timestamp} {text}")
            para.paragraph_format.left_indent = Inches(0.5)
    
    def _add_headers_footers(self, doc: Document, meeting_metadata: Dict[str, Any]):
        """Add headers and footers"""
        # Header
        header = doc.sections[0].header
        header_para = header.paragraphs[0]
        header_para.text = "CybeMeeting - Rapport de Réunion BTP"
        header_para.runs[0].font.size = Pt(10)
        header_para.runs[0].font.color.rgb = self.brand_primary
        
        # Footer
        footer = doc.sections[0].footer
        footer_para = footer.paragraphs[0]
        project_name = meeting_metadata.get("project_name", "Projet BTP")
        footer_para.text = f"{project_name} - {datetime.now().strftime('%d/%m/%Y')}"
        footer_para.runs[0].font.size = Pt(9)
        footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    def _add_page_break(self, doc: Document):
        """Add page break"""
        doc.add_page_break()
    
    def generate_html_preview(self, analysis_data: Dict[str, Any], meeting_metadata: Dict[str, Any]) -> str:
        """Generate HTML preview of the report"""
        try:
            meta = analysis_data.get("meta", {})
            
            html = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Rapport de Réunion - {meta.get('meetingTitle', 'Réunion')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f8fafc; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #4F46E5; padding-bottom: 20px; }}
                    .brand {{ color: #4F46E5; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                    .subtitle {{ color: #7C3AED; font-size: 18px; margin-bottom: 20px; }}
                    .meta-info {{ background: #f1f5f9; padding: 15px; border-radius: 6px; margin-bottom: 25px; }}
                    .meta-info div {{ margin-bottom: 5px; }}
                    h1 {{ color: #4F46E5; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }}
                    h2 {{ color: #7C3AED; margin-top: 25px; }}
                    .section {{ margin-bottom: 20px; }}
                    ul {{ padding-left: 20px; }}
                    li {{ margin-bottom: 5px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; }}
                    th {{ background: #f8fafc; font-weight: bold; color: #4F46E5; }}
                    .empty-section {{ color: #64748b; font-style: italic; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="brand">CybeMeeting</div>
                        <div class="subtitle">Rapport de Réunion BTP</div>
                    </div>
                    
                    <div class="meta-info">
                        <div><strong>Projet:</strong> {meta.get('projectName', 'Non spécifié')}</div>
                        <div><strong>Réunion:</strong> {meta.get('meetingTitle', 'Non spécifié')}</div>
                        <div><strong>Date:</strong> {meta.get('meetingDate', 'Non spécifié')}</div>
                        <div><strong>Durée:</strong> {meta.get('duration', 0)} minutes</div>
                        <div><strong>Participants:</strong> {', '.join(meta.get('participantsDetected', []))}</div>
                    </div>
            """
            
            # Add user instructions if present
            user_instructions = meta.get('userInstructions', '')
            if user_instructions:
                html += f"""
                    <div class="user-instructions" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
                        <strong style="color: #f1f5f9;">Instructions spécifiques:</strong> {user_instructions}
                    </div>
                """
            
            # Check if we have dynamic sections (new format)
            if "sectionsDynamiques" in analysis_data:
                html += self._generate_dynamic_sections_html(analysis_data.get("sectionsDynamiques", {}))
            else:
                # Fallback to old format
                html += self._generate_legacy_sections_html(analysis_data)
            
            # Add chronological view if available
            if analysis_data.get("vueChronologique"):
                html += self._generate_chronological_html(analysis_data.get("vueChronologique", []))
            
            # Add analysis metrics if available
            if analysis_data.get("analysisMetrics"):
                html += self._generate_metrics_html(analysis_data.get("analysisMetrics", {}))
            
            html += """
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 12px;">
                        Rapport généré par CybeMeeting le """ + datetime.now().strftime('%d/%m/%Y à %H:%M') + """
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error generating HTML preview: {e}")
            return "<html><body><h1>Erreur lors de la génération de l'aperçu</h1></body></html>"
    
    def _generate_dynamic_sections_html(self, sections_data: Dict[str, Any]) -> str:
        """Generate HTML for dynamic sections"""
        html = ""
        
        # Define section order and French titles
        section_mappings = {
            "etatLieux": "État des lieux",
            "avancementTravaux": "Avancement des travaux", 
            "problemesIdentifies": "Problèmes identifiés",
            "decisionsStrategiques": "Décisions stratégiques",
            "objectifs": "Objectifs de la réunion",
            "actionsUrgentes": "Actions urgentes",
            "actionsReguliers": "Actions de suivi",
            "aspectsTechniques": "Aspects techniques",
            "planningEtDelais": "Planning et délais",
            "aspectsFinanciers": "Aspects financiers",
            "relationsFournisseurs": "Relations fournisseurs",
            "aspectsReglementaires": "Aspects réglementaires", 
            "communicationClient": "Communication client",
            "risquesEtMitigations": "Risques et mitigations",
            "pointsDivers": "Points divers",
            "syntheseDesAccords": "Synthèse des accords",
            "pointsEnSuspens": "Points en suspens"
        }
        
        # Process sections in logical order
        for section_key, title in section_mappings.items():
            if section_key in sections_data and sections_data[section_key]:
                content = sections_data[section_key]
                html += f'<div class="section"><h2 style="color: #7C3AED; margin-top: 25px; border-left: 4px solid #7C3AED; padding-left: 15px;">{title}</h2>'
                html += '<div class="section-content" style="background: #fafafa; padding: 15px; border-radius: 6px;">'
                
                # Handle different content types
                if section_key in ["actionsUrgentes", "actionsReguliers"]:
                    html += self._generate_actions_table_html(content, section_key == "actionsUrgentes")
                elif section_key == "risquesEtMitigations":
                    html += self._generate_risks_table_html(content)
                else:
                    html += self._generate_list_html(content)
                
                html += '</div></div>'
        
        # Add any custom sections not in the predefined list
        for section_key, content in sections_data.items():
            if section_key not in section_mappings and content:
                custom_title = section_key.replace('_', ' ').title()
                html += f'<div class="section"><h2 style="color: #7C3AED; margin-top: 25px; border-left: 4px solid #7C3AED; padding-left: 15px;">{custom_title}</h2>'
                html += '<div class="section-content" style="background: #fafafa; padding: 15px; border-radius: 6px;">'
                html += self._generate_list_html(content)
                html += '</div></div>'
        
        return html
    
    def _generate_legacy_sections_html(self, analysis_data: Dict[str, Any]) -> str:
        """Generate HTML for legacy format"""
        html = ""
        sections = [
            ("Objectifs de la réunion", analysis_data.get("objectifs", []), "list"),
            ("Problèmes identifiés", analysis_data.get("problemes", []), "list"),
            ("Décisions prises", analysis_data.get("decisions", []), "list"),
            ("Plan d'actions", analysis_data.get("actions", []), "actions_table"),
            ("Analyse des risques", analysis_data.get("risques", []), "risks_table"),
            ("Points techniques BTP", analysis_data.get("pointsTechniquesBTP", []), "list"),
            ("Planning et jalons", analysis_data.get("planning", []), "list"),
            ("Budget et chiffrage", analysis_data.get("budget_chiffrage", []), "list"),
            ("Informations diverses", analysis_data.get("divers", []), "list")
        ]
        
        for title, content, content_type in sections:
            html += f'<div class="section"><h2 style="color: #7C3AED; margin-top: 25px;">{title}</h2>'
            html += '<div class="section-content" style="background: #fafafa; padding: 15px; border-radius: 6px;">'
            
            if not content:
                html += '<div style="color: #64748b; font-style: italic; text-align: center; padding: 20px;">Aucun élément identifié.</div>'
            elif content_type == "list":
                html += self._generate_list_html(content)
            elif content_type == "actions_table":
                html += self._generate_actions_table_html(content, False)
            elif content_type == "risks_table":
                html += self._generate_risks_table_html(content)
            
            html += '</div></div>'
        
        return html
    
    def _generate_list_html(self, items: list) -> str:
        """Generate HTML for list items"""
        if not items:
            return '<div style="color: #64748b; font-style: italic; text-align: center; padding: 20px;">Aucun élément identifié.</div>'
        
        html = "<ul style='padding-left: 20px;'>"
        for item in items:
            if item and not str(item).startswith("/*"):
                html += f"<li style='margin-bottom: 8px; line-height: 1.4;'>{item}</li>"
        html += "</ul>"
        return html
    
    def _generate_actions_table_html(self, actions: list, is_urgent: bool = False) -> str:
        """Generate HTML table for actions"""
        if not actions:
            return '<div style="color: #64748b; font-style: italic; text-align: center; padding: 20px;">Aucune action définie.</div>'
        
        html = """
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <thead>
                <tr><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Action</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Responsable</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Échéance</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Contexte</th></tr>
            </thead>
            <tbody>
        """
        
        for action in actions:
            border_color = "#ef4444" if is_urgent else "#f59e0b"
            bg_color = "#fef2f2" if is_urgent else "#fefbf2"
            html += f"""
            <tr style="border-left: 4px solid {border_color}; background: {bg_color};">
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{action.get('action', action.get('tache', ''))}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{action.get('responsable', '')}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{action.get('echeance', 'Non définie')}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{action.get('contexte', '')}</td>
            </tr>
            """
        
        html += "</tbody></table>"
        return html
    
    def _generate_risks_table_html(self, risks: list) -> str:
        """Generate HTML table for risks"""
        if not risks:
            return '<div style="color: #64748b; font-style: italic; text-align: center; padding: 20px;">Aucun risque identifié.</div>'
        
        html = """
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <thead>
                <tr><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Risque</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Catégorie</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Probabilité</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Impact</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Mitigation</th><th style="border: 1px solid #e2e8f0; padding: 12px; text-align: left; background: #f8fafc; font-weight: bold; color: #4F46E5;">Responsable</th></tr>
            </thead>
            <tbody>
        """
        
        for risk in risks:
            prob = risk.get('probabilite', 'Moyenne')
            if prob == "Élevée":
                border_color = "#ef4444"
                bg_color = "#fef2f2"
            elif prob == "Moyenne":
                border_color = "#f59e0b"
                bg_color = "#fefbf2"
            else:
                border_color = "#10b981"
                bg_color = "#f0fdf4"
            
            html += f"""
            <tr style="border-left: 4px solid {border_color}; background: {bg_color};">
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{risk.get('risque', '')}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{risk.get('categorie', 'Général')}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{risk.get('probabilite', 'Moyenne')}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{risk.get('impact', '')}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{risk.get('mitigations', risk.get('mitigation', ''))}</td>
                <td style="border: 1px solid #e2e8f0; padding: 12px;">{risk.get('responsableRisque', risk.get('responsable', ''))}</td>
            </tr>
            """
        
        html += "</tbody></table>"
        return html
    
    def _generate_chronological_html(self, chronological_data: list) -> str:
        """Generate HTML for chronological view"""
        html = '<div class="section" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px;"><h2 style="color: white; border-left: 4px solid white; padding-left: 15px;">Vue chronologique de la réunion</h2>'
        
        if chronological_data:
            html += "<ul style='padding-left: 20px;'>"
            for event in chronological_data:
                if event and not event.startswith("/*"):
                    html += f"<li style='margin-bottom: 8px; line-height: 1.4;'>{event}</li>"
            html += "</ul>"
        else:
            html += '<div style="text-align: center; padding: 20px;">Aucune information chronologique.</div>'
        
        html += "</div>"
        return html
    
    def _generate_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for analysis metrics"""
        html = '<div class="section" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px;"><h2 style="color: white; border-left: 4px solid white; padding-left: 15px;">Métriques d\'analyse</h2>'
        
        metrics_list = [
            f"Segments analysés: {metrics.get('segmentsAnalyses', 0)}/{metrics.get('totalSegments', 0)}",
            f"Niveau de détail: {metrics.get('niveauDetaille', 'Non spécifié')}",
            f"Couverture des sujets: {metrics.get('couvertureSujets', 'Non spécifié')}",
            f"Qualité d'extraction: {metrics.get('qualiteExtraction', 'Non spécifié')}"
        ]
        
        html += "<ul style='padding-left: 20px;'>"
        for metric in metrics_list:
            html += f"<li style='margin-bottom: 8px; line-height: 1.4;'>{metric}</li>"
        html += "</ul>"
        
        html += "</div>"
        return html
    
    def _add_general_information(self, doc: Document, meta_data: Dict[str, Any]):
        """Add beautifully formatted general information section"""
        # Add title
        doc.add_heading("1. Informations générales", level=1)
        
        # Create a formatted table for meta information
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.allow_autofit = True
        
        # Header row
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Élément'
        hdr_cells[1].text = 'Information'
        
        # Style header
        for cell in hdr_cells:
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = self.brand_primary
            cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            # Add light background to header
            try:
                from docx.oxml.shared import qn
                tcPr = cell._tc.get_or_add_tcPr()
                shd = tcPr.find(qn('w:shd'))
                if shd is None:
                    from docx.oxml.parser import parse_xml
                    from docx.oxml.ns import nsdecls
                    shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                    tcPr.append(shd)
            except:
                pass  # Skip background color if it fails
        
        # Data rows
        info_items = [
            ("Projet", meta_data.get('projectName', 'Non spécifié')),
            ("Titre de la réunion", meta_data.get('meetingTitle', 'Non spécifié')),
            ("Type de réunion", meta_data.get('meetingType', 'Non spécifié')),
            ("Date de la réunion", self._format_date(meta_data.get('meetingDate', ''))),
            ("Durée", f"{meta_data.get('duration', 0)} minutes"),
            ("Participants attendus", str(meta_data.get('participantsExpected', 'Non spécifié'))),
            ("Participants détectés", ', '.join(meta_data.get('participantsDetected', []))),
        ]
        
        # Add instructions if present
        user_instructions = meta_data.get('userInstructions', '')
        if user_instructions:
            info_items.append(("Instructions spécifiques", user_instructions))
        
        # Add attendance analysis if present
        attendance_analysis = meta_data.get('attendanceAnalysis', '')
        if attendance_analysis:
            info_items.append(("Analyse de présence", attendance_analysis))
        
        for label, value in info_items:
            row_cells = table.add_row().cells
            row_cells[0].text = label
            row_cells[1].text = str(value)
            
            # Style label cell
            row_cells[0].paragraphs[0].runs[0].font.bold = True
            row_cells[0].paragraphs[0].runs[0].font.color.rgb = self.brand_secondary
            
            # Handle long text in value cell
            if len(str(value)) > 50:
                row_cells[1].paragraphs[0].runs[0].font.size = Pt(10)
        
        doc.add_paragraph()  # Add spacing
    
    def _format_date(self, date_str: str) -> str:
        """Format date string to be more readable"""
        if not date_str:
            return "Non spécifié"
        
        try:
            # Try to parse ISO format
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%d/%m/%Y à %H:%M')
            else:
                return date_str
        except:
            return date_str
    
    def _add_chronological_view_word(self, doc: Document, chronological_data: list):
        """Add chronological timeline section to Word document"""
        if not chronological_data:
            return
            
        doc.add_heading("Vue chronologique de la réunion", level=1)
        
        for event in chronological_data:
            if event and not event.startswith("/*"):
                para = doc.add_paragraph()
                para.style = 'List Bullet'
                run = para.add_run(event)
                run.font.size = Pt(11)
        
        doc.add_paragraph()  # Add spacing
    
    def _add_analysis_metrics_word(self, doc: Document, metrics: Dict[str, Any]):
        """Add analysis quality metrics section to Word document"""
        if not metrics:
            return
            
        doc.add_heading("Métriques d'analyse", level=1)
        
        # Create a nice table for metrics
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.allow_autofit = True
        
        # Header row
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Métrique'
        hdr_cells[1].text = 'Valeur'
        
        # Style header
        for cell in hdr_cells:
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = self.brand_primary
            cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            # Add light background to header
            try:
                from docx.oxml.shared import qn
                tcPr = cell._tc.get_or_add_tcPr()
                shd = tcPr.find(qn('w:shd'))
                if shd is None:
                    from docx.oxml.parser import parse_xml
                    from docx.oxml.ns import nsdecls
                    shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                    tcPr.append(shd)
            except:
                pass  # Skip background color if it fails
        
        # Metrics data
        metrics_items = [
            ("Segments analysés", f"{metrics.get('segmentsAnalyses', 0)}/{metrics.get('totalSegments', 0)}"),
            ("Niveau de détail", metrics.get('niveauDetaille', 'Non spécifié')),
            ("Couverture des sujets", metrics.get('couvertureSujets', 'Non spécifié')),
            ("Qualité d'extraction", metrics.get('qualiteExtraction', 'Non spécifié'))
        ]
        
        for label, value in metrics_items:
            row_cells = table.add_row().cells
            row_cells[0].text = label
            row_cells[1].text = str(value)
            
            # Style label cell
            row_cells[0].paragraphs[0].runs[0].font.bold = True
            row_cells[0].paragraphs[0].runs[0].font.color.rgb = self.brand_secondary
        
        doc.add_paragraph()  # Add spacing
