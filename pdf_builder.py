import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm

def create_pdf(title, student_name, university, company, specialty, supervisor, academic_year, logo_path, sections_dict, section_options, selected_ids, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=1*cm,
        textColor="black"
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=12,
        spaceAfter=0.3*cm,
        leading=16
    )
    
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=normal_style,
        alignment=TA_CENTER
    )
    
    heading1 = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceBefore=0.5*cm,
        spaceAfter=0.5*cm,
        textColor="black"
    )
    
    heading2 = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=0.4*cm,
        spaceAfter=0.4*cm,
        textColor="black"
    )
    
    heading3 = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=0.3*cm,
        spaceAfter=0.3*cm,
        textColor="black"
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=normal_style,
        leftIndent=20,
        firstLineIndent=-10
    )

    Story = []
    
    # --- PAGE DE GARDE ---
    if logo_path and os.path.exists(logo_path):
        try:
            im = Image(logo_path, width=4*cm, height=4*cm)
            Story.append(im)
            Story.append(Spacer(1, 1*cm))
        except Exception:
            pass
            
    if university:
        Story.append(Paragraph(f"<b>{university}</b>", center_style))
        Story.append(Spacer(1, 1*cm))
        
    Story.append(Paragraph("<b>RAPPORT DE PROJET DE FIN D'ÉTUDES</b>", center_style))
    Story.append(Spacer(1, 2*cm))
    
    if title:
        Story.append(Paragraph(f"<b>{title}</b>", title_style))
        Story.append(Spacer(1, 2*cm))
        
    info_text = ""
    if student_name:
        info_text += f"<b>Réalisé par :</b> {student_name}<br/><br/>"
    if specialty:
        info_text += f"<b>Spécialité / Filière :</b> {specialty}<br/><br/>"
    if company:
        info_text += f"<b>Entreprise d'accueil :</b> {company}<br/><br/>"
    if supervisor:
        info_text += f"<b>Encadré par :</b> {supervisor}<br/><br/>"

    if info_text:
        Story.append(Paragraph(info_text, normal_style))
        
    Story.append(Spacer(1, 3*cm))
    
    if academic_year:
        Story.append(Paragraph(f"<b>Année universitaire : {academic_year}</b>", center_style))
        
    Story.append(PageBreak())

    # --- SECTIONS ---
    for idx, sid in enumerate(selected_ids):
        if sid in sections_dict:
            if idx > 0:
                # Page break for all sections except the first one
                Story.append(PageBreak())
                    
            section_title = section_options[sid]['title']
            Story.append(Paragraph(f"<b>{section_title}</b>", heading1))
            
            content = sections_dict[sid]
            
            # Markdown to ReportLab basic conversion
            # Bold
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            # Italic
            content = re.sub(r'\*(.*?)\*', r'<i>\1</i>', content)
            
            paragraphs = content.split('\n')
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                if p.startswith('### '):
                    Story.append(Paragraph(f"<b>{p[4:]}</b>", heading3))
                elif p.startswith('## '):
                    Story.append(Paragraph(f"<b>{p[3:]}</b>", heading2))
                elif p.startswith('# '):
                    Story.append(Paragraph(f"<b>{p[2:]}</b>", heading1))
                elif p.startswith('- ') or p.startswith('* '):
                    # Remove the dash/asterisk but keep HTML bullet symbol, left indented
                    bullet_text = p[2:].strip()
                    Story.append(Paragraph(f"• {bullet_text}", bullet_style))
                else:
                    Story.append(Paragraph(p, normal_style))
            
            Story.append(Spacer(1, 0.5*cm))
            
    try:
        doc.build(Story)
    except Exception as e:
        raise Exception(f"Erreur lors de la construction du PDF via ReportLab: {e}")
