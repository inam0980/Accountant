from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime


class InvoicePDFGenerator:
    """
    Generate professional PDF invoices with QR codes and Arabic support
    """
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.width, self.height = A4
        self.margin = 2 * cm
        
    def arabic_text(self, text):
        """Convert Arabic text for proper display in PDF"""
        if not text:
            return ''
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text
    
    def generate_qr_code(self):
        """Generate QR code for invoice"""
        # Create QR code with invoice details
        qr_data = f"""
Invoice: {self.invoice.invoice_number}
Student: {self.invoice.student.name_english}
Amount: {self.invoice.total_amount} SAR
Date: {self.invoice.invoice_date}
Status: {self.invoice.get_status_display()}
        """.strip()
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def draw_header(self, c):
        """Draw invoice header with school information"""
        # School name
        c.setFont("Helvetica-Bold", 20)
        c.drawString(self.margin, self.height - self.margin, "SCHOOL ERP SYSTEM")
        
        # School details
        c.setFont("Helvetica", 10)
        y = self.height - self.margin - 0.5*cm
        c.drawString(self.margin, y, "123 Education Street, Riyadh, Saudi Arabia")
        y -= 0.4*cm
        c.drawString(self.margin, y, "Tel: +966 11 234 5678 | Email: info@schoolerp.sa")
        y -= 0.4*cm
        c.drawString(self.margin, y, "VAT Registration: 300000000000003")
        
        # Invoice title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(self.width - self.margin - 3*cm, self.height - self.margin, "TAX INVOICE")
        c.drawString(self.width - self.margin - 3.5*cm, self.height - self.margin - 0.5*cm, "فاتورة ضريبية")
        
        # Horizontal line
        c.setStrokeColor(colors.HexColor("#3B82F6"))
        c.setLineWidth(2)
        c.line(self.margin, self.height - self.margin - 1.5*cm, 
               self.width - self.margin, self.height - self.margin - 1.5*cm)
    
    def draw_invoice_info(self, c):
        """Draw invoice and student information"""
        y = self.height - self.margin - 3*cm
        
        # Left side - Invoice info
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Invoice Number:")
        c.setFont("Helvetica", 10)
        c.drawString(self.margin + 3*cm, y, str(self.invoice.invoice_number))
        
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Invoice Date:")
        c.setFont("Helvetica", 10)
        c.drawString(self.margin + 3*cm, y, self.invoice.invoice_date.strftime('%d %B %Y'))
        
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Due Date:")
        c.setFont("Helvetica", 10)
        c.drawString(self.margin + 3*cm, y, self.invoice.due_date.strftime('%d %B %Y'))
        
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Academic Year:")
        c.setFont("Helvetica", 10)
        c.drawString(self.margin + 3*cm, y, self.invoice.academic_year)
        
        # Right side - Student info
        y = self.height - self.margin - 3*cm
        x_right = self.width / 2 + 1*cm
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_right, y, "Student Information")
        
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_right, y, "Student ID:")
        c.setFont("Helvetica", 10)
        c.drawString(x_right + 2.5*cm, y, self.invoice.student.student_id)
        
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_right, y, "Name (English):")
        c.setFont("Helvetica", 10)
        c.drawString(x_right + 2.5*cm, y, self.invoice.student.name_english)
        
        y -= 0.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_right, y, "Name (Arabic):")
        c.setFont("Helvetica", 10)
        # Note: Arabic text would need special font support
        c.drawString(x_right + 2.5*cm, y, self.invoice.student.name_arabic)
        
        try:
            grade = self.invoice.student.academic_history.grade
            section = self.invoice.student.academic_history.section
            y -= 0.5*cm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x_right, y, "Grade/Section:")
            c.setFont("Helvetica", 10)
            c.drawString(x_right + 2.5*cm, y, f"{grade} - {section}")
        except:
            pass
    
    def draw_items_table(self, c):
        """Draw invoice items table"""
        y_start = self.height - self.margin - 8*cm
        
        # Table headers
        headers = [['#', 'Description', 'Qty', 'Unit Price (SAR)', 'Amount (SAR)']]
        
        # Table data
        data = headers
        for idx, item in enumerate(self.invoice.items.all(), 1):
            data.append([
                str(idx),
                f"{item.fee_category.category_name}\n{item.description or ''}",
                str(item.quantity),
                f"{item.unit_price:,.2f}",
                f"{item.total_amount:,.2f}"
            ])
        
        # Create table
        table = Table(data, colWidths=[1*cm, 8*cm, 1.5*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B82F6")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # First column center
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numbers right aligned
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Draw table
        table.wrapOn(c, self.width, self.height)
        table_height = table._height
        table.drawOn(c, self.margin, y_start - table_height)
        
        return y_start - table_height - 1*cm
    
    def draw_totals(self, c, y_position):
        """Draw invoice totals section"""
        x_label = self.width - self.margin - 7*cm
        x_value = self.width - self.margin - 3*cm
        
        c.setFont("Helvetica", 10)
        
        # Subtotal
        c.drawString(x_label, y_position, "Subtotal:")
        c.drawRightString(x_value, y_position, f"{self.invoice.subtotal:,.2f} SAR")
        
        # Discount
        if self.invoice.discount_amount > 0:
            y_position -= 0.5*cm
            c.setFillColor(colors.HexColor("#EF4444"))
            c.drawString(x_label, y_position, "Discount:")
            c.drawRightString(x_value, y_position, f"-{self.invoice.discount_amount:,.2f} SAR")
            c.setFillColor(colors.black)
        
        # VAT
        y_position -= 0.5*cm
        c.drawString(x_label, y_position, "VAT (15%):")
        c.drawRightString(x_value, y_position, f"{self.invoice.vat_amount:,.2f} SAR")
        
        # Line before total
        y_position -= 0.3*cm
        c.setLineWidth(1)
        c.line(x_label, y_position, x_value, y_position)
        
        # Total
        y_position -= 0.5*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_label, y_position, "Total Amount:")
        c.drawRightString(x_value, y_position, f"{self.invoice.total_amount:,.2f} SAR")
        
        # Paid amount
        if self.invoice.paid_amount > 0:
            y_position -= 0.6*cm
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#10B981"))
            c.drawString(x_label, y_position, "Paid Amount:")
            c.drawRightString(x_value, y_position, f"{self.invoice.paid_amount:,.2f} SAR")
            c.setFillColor(colors.black)
        
        # Balance
        if self.invoice.balance_amount > 0:
            y_position -= 0.5*cm
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#EF4444"))
            c.drawString(x_label, y_position, "Balance Due:")
            c.drawRightString(x_value, y_position, f"{self.invoice.balance_amount:,.2f} SAR")
            c.setFillColor(colors.black)
        
        return y_position
    
    def draw_qr_code(self, c):
        """Draw QR code on invoice"""
        qr_buffer = self.generate_qr_code()
        
        # Draw QR code at bottom left
        c.drawImage(qr_buffer, 
                   self.margin, 
                   self.margin, 
                   width=3*cm, 
                   height=3*cm)
        
        c.setFont("Helvetica", 8)
        c.drawString(self.margin, self.margin - 0.5*cm, "Scan for verification")
    
    def draw_footer(self, c):
        """Draw invoice footer"""
        y = self.margin + 4*cm
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Payment Terms:")
        
        c.setFont("Helvetica", 9)
        y -= 0.5*cm
        c.drawString(self.margin, y, "• Payment is due within 30 days of invoice date")
        y -= 0.4*cm
        c.drawString(self.margin, y, "• Late payments may incur additional charges")
        y -= 0.4*cm
        c.drawString(self.margin, y, "• For payment inquiries, contact our billing department")
        
        # Status indicator
        status_colors = {
            'paid': colors.HexColor("#10B981"),
            'pending': colors.HexColor("#F59E0B"),
            'overdue': colors.HexColor("#EF4444"),
            'partial': colors.HexColor("#3B82F6"),
        }
        
        status_color = status_colors.get(self.invoice.status, colors.grey)
        
        c.setFillColor(status_color)
        c.setFont("Helvetica-Bold", 12)
        status_text = f"STATUS: {self.invoice.get_status_display().upper()}"
        c.drawRightString(self.width - self.margin, self.margin + 4*cm, status_text)
        
        # Footer line
        c.setStrokeColor(colors.HexColor("#3B82F6"))
        c.setLineWidth(1)
        c.line(self.margin, self.margin - 1*cm, 
               self.width - self.margin, self.margin - 1*cm)
        
        # Thank you message
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(self.width / 2, self.margin - 1.5*cm, 
                           "Thank you for your business!")
    
    def generate(self, output_path=None):
        """Generate the PDF invoice"""
        if output_path is None:
            output_path = f"invoice_{self.invoice.invoice_number}.pdf"
        
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # Draw all sections
        self.draw_header(c)
        self.draw_invoice_info(c)
        y_after_table = self.draw_items_table(c)
        y_after_totals = self.draw_totals(c, y_after_table)
        self.draw_qr_code(c)
        self.draw_footer(c)
        
        # Save PDF
        c.save()
        
        return output_path
    
    def generate_to_buffer(self):
        """Generate PDF to BytesIO buffer for HTTP response"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Draw all sections
        self.draw_header(c)
        self.draw_invoice_info(c)
        y_after_table = self.draw_items_table(c)
        y_after_totals = self.draw_totals(c, y_after_table)
        self.draw_qr_code(c)
        self.draw_footer(c)
        
        # Save to buffer
        c.save()
        buffer.seek(0)
        
        return buffer


def generate_invoice_pdf(invoice):
    """
    Convenience function to generate invoice PDF
    Usage: generate_invoice_pdf(invoice_object)
    """
    generator = InvoicePDFGenerator(invoice)
    return generator.generate_to_buffer()
