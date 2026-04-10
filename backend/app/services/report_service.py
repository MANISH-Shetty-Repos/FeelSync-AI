import io
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .history_service import history_service
from ..database import get_database

class ReportService:
    async def generate_pdf_report(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> io.BytesIO:
        # 1. Fetch history for the specific range
        db = get_database()
        query = {
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        cursor = db.analyses.find(query).sort("created_at", 1)
        history = await cursor.to_list(length=100)
        
        # 2. Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # 3. Title & Header
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor("#4A90E2")
        )
        elements.append(Paragraph("FeelSync AI - Emotional Intelligence Report", title_style))
        elements.append(Paragraph(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 4. Summary Table
        table_data = [["Date", "Type", "Mood", "Top Emotion"]]
        for entry in history:
            sentiment = entry.get("sentiment", {}).get("label", "N/A")
            # Extract top emotion
            emot_data = entry.get("emotion", {})
            top_emot = "N/A"
            if isinstance(emot_data, list) and len(emot_data) > 0:
                top_emot = emot_data[0].get("label", "N/A")
            elif isinstance(emot_data, dict):
                top_emot = "Multimodal"
                
            table_data.append([
                entry["created_at"].strftime("%Y-%m- %d %H:%M"),
                entry["input_type"].capitalize(),
                sentiment,
                top_emot
            ])
            
        t = Table(table_data, colWidths=[120, 60, 80, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4A90E2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(t)
        
        # 5. Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

report_service = ReportService()
