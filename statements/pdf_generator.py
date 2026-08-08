import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from xml.sax.saxutils import escape

def sanitize_text(text):
    """Escapes XML characters to prevent ReportLab parsing errors."""
    if not isinstance(text, str):
        return str(text)
    return escape(text)

def generate_audit_pdf(statement, audit_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    # Register font that supports Unicode (Rupee symbol)
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        font_regular = 'DejaVuSans'
        font_bold = 'DejaVuSans-Bold'
    except Exception:
        font_regular = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_bold,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontName=font_bold,
        textColor=colors.HexColor("#333333"),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=10,
        leading=14
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10,
        leading=14
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph("FinSight", title_style))
    elements.append(Paragraph("Financial Audit Report", title_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"<b>Statement:</b> {sanitize_text(statement.file_name)}", normal_style))
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"<b>Audit Generation Date:</b> {date_str}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Risk Assessment
    if 'risk_level' in audit_data:
        elements.append(Paragraph("Risk Assessment", subtitle_style))
        elements.append(Paragraph(f"<b>Risk Level:</b> {sanitize_text(audit_data['risk_level'])}", normal_style))
        elements.append(Spacer(1, 15))
        
    # Executive Summary
    if 'overall_summary' in audit_data:
        elements.append(Paragraph("Executive Summary", subtitle_style))
        elements.append(Paragraph(sanitize_text(audit_data['overall_summary']), normal_style))
        elements.append(Spacer(1, 15))
        
    # Strengths
    if 'strengths' in audit_data and audit_data['strengths']:
        elements.append(Paragraph("Strengths", subtitle_style))
        bullet_list = [ListItem(Paragraph(sanitize_text(s), normal_style)) for s in audit_data['strengths']]
        elements.append(ListFlowable(bullet_list, bulletType='bullet'))
        elements.append(Spacer(1, 15))
        
    # Concerns
    if 'concerns' in audit_data and audit_data['concerns']:
        elements.append(Paragraph("Concerns", subtitle_style))
        bullet_list = [ListItem(Paragraph(sanitize_text(c), normal_style)) for c in audit_data['concerns']]
        elements.append(ListFlowable(bullet_list, bulletType='bullet'))
        elements.append(Spacer(1, 15))
        
    # Suspicious Activity
    if 'suspicious_activity' in audit_data and audit_data['suspicious_activity']:
        elements.append(Paragraph("Suspicious Activity", subtitle_style))
        bullet_list = [ListItem(Paragraph(sanitize_text(act), normal_style)) for act in audit_data['suspicious_activity']]
        elements.append(ListFlowable(bullet_list, bulletType='bullet'))
        elements.append(Spacer(1, 15))
        
    # Recommendations
    if 'recommendations' in audit_data and audit_data['recommendations']:
        elements.append(Paragraph("Recommendations", subtitle_style))
        bullet_list = [ListItem(Paragraph(sanitize_text(rec), normal_style)) for rec in audit_data['recommendations']]
        elements.append(ListFlowable(bullet_list, bulletType='bullet'))
        elements.append(Spacer(1, 15))
        
    # Final Verdict
    if 'final_verdict' in audit_data:
        elements.append(Paragraph("Final Verdict", subtitle_style))
        elements.append(Paragraph(sanitize_text(audit_data['final_verdict']), normal_style))
        elements.append(Spacer(1, 15))
        
    # Build doc
    doc.build(elements)
    buffer.seek(0)
    return buffer
