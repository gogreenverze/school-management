"""
Utility functions for generating PDF documents like invoices and receipts.
"""
import os
import logging
import pdfkit
from datetime import datetime
from flask import current_app, render_template
from app.models.finance import Invoice, InvoiceItem, InvoicePayment
from app.models.user import StudentProfile, User

# Configure logging
logger = logging.getLogger(__name__)

def generate_invoice_pdf(invoice_id):
    """
    Generate a PDF invoice and save it to the file system

    Args:
        invoice_id (int): ID of the invoice to generate

    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Get invoice data
        invoice = Invoice.query.get_or_404(invoice_id)
        student = StudentProfile.query.get_or_404(invoice.student_id)
        items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()

        # Create directory if it doesn't exist
        if 'UPLOAD_FOLDER' not in current_app.config:
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')

        upload_folder = current_app.config['UPLOAD_FOLDER']

        # Make sure upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        invoice_dir = os.path.join(upload_folder, 'invoices')
        if not os.path.exists(invoice_dir):
            os.makedirs(invoice_dir)

        # Generate filename
        filename = f"invoice_{invoice.invoice_number.replace('-', '_')}.pdf"
        filepath = os.path.join(invoice_dir, filename)

        # Render HTML template
        html_content = render_template(
            'pdf/invoice.html',
            invoice=invoice,
            student=student,
            items=items,
            school_name=current_app.config.get('SCHOOL_NAME', 'School Management System'),
            school_address=current_app.config.get('SCHOOL_ADDRESS', '123 School Street, Tamil Nadu, India'),
            school_phone=current_app.config.get('SCHOOL_PHONE', '+91 1234567890'),
            school_email=current_app.config.get('SCHOOL_EMAIL', 'info@school.edu'),
            generation_date=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        )

        # Generate PDF using pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
            'encoding': 'UTF-8',
            'no-outline': None
        }

        try:
            # Try to generate PDF with wkhtmltopdf
            pdfkit.from_string(html_content, filepath, options=options)
        except Exception as e:
            logger.error(f"Error generating PDF with pdfkit: {str(e)}")

            # Fallback: Just save the HTML file
            html_filepath = filepath.replace('.pdf', '.html')
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Saved HTML file instead: {html_filepath}")
            return os.path.join('invoices', os.path.basename(html_filepath))

        # Update invoice with PDF path
        relative_path = os.path.join('invoices', filename)
        invoice.pdf_path = relative_path
        from app import db
        db.session.commit()

        logger.info(f"Generated invoice PDF: {filepath}")
        return relative_path

    except Exception as e:
        logger.error(f"Error generating invoice PDF: {str(e)}")
        return None

def generate_receipt_pdf(payment_id, payment_type):
    """
    Generate a PDF receipt for a payment

    Args:
        payment_id (int): ID of the payment
        payment_type (str): Type of payment (fee_payments, sport_fee_payments, etc.)

    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Get payment data based on type
        payment = None
        from app.models.finance import FeePayment, SportFeePayment, TransportationFeePayment

        if payment_type == 'fee_payments':
            payment = FeePayment.query.get_or_404(payment_id)
            student = StudentProfile.query.get_or_404(payment.student_id)
            payment_for = f"Tuition Fee - {payment.fee_structure.name}"
        elif payment_type == 'sport_fee_payments':
            payment = SportFeePayment.query.get_or_404(payment_id)
            student = StudentProfile.query.get_or_404(payment.student_id)
            payment_for = f"Sports Fee - {payment.sport.name} ({payment.sport_fee.name})"
        elif payment_type == 'transportation_fee_payments':
            payment = TransportationFeePayment.query.get_or_404(payment_id)
            student = StudentProfile.query.get_or_404(payment.student_id)
            payment_for = f"Transportation Fee - {payment.transportation_fee.name}"
        else:
            raise ValueError(f"Invalid payment type: {payment_type}")

        # Create directory if it doesn't exist
        if 'UPLOAD_FOLDER' not in current_app.config:
            current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')

        upload_folder = current_app.config['UPLOAD_FOLDER']

        # Make sure upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        receipt_dir = os.path.join(upload_folder, 'receipts')
        if not os.path.exists(receipt_dir):
            os.makedirs(receipt_dir)

        # Generate filename
        filename = f"receipt_{payment.receipt_number.replace('-', '_')}.pdf"
        filepath = os.path.join(receipt_dir, filename)

        # Render HTML template
        html_content = render_template(
            'pdf/receipt.html',
            payment=payment,
            student=student,
            payment_for=payment_for,
            payment_type=payment_type,
            school_name=current_app.config.get('SCHOOL_NAME', 'School Management System'),
            school_address=current_app.config.get('SCHOOL_ADDRESS', '123 School Street, Tamil Nadu, India'),
            school_phone=current_app.config.get('SCHOOL_PHONE', '+91 1234567890'),
            school_email=current_app.config.get('SCHOOL_EMAIL', 'info@school.edu'),
            generation_date=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        )

        # Generate PDF using pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
            'encoding': 'UTF-8',
            'no-outline': None
        }

        try:
            # Try to generate PDF with wkhtmltopdf
            pdfkit.from_string(html_content, filepath, options=options)
        except Exception as e:
            logger.error(f"Error generating PDF with pdfkit: {str(e)}")

            # Fallback: Just save the HTML file
            html_filepath = filepath.replace('.pdf', '.html')
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Saved HTML file instead: {html_filepath}")
            return os.path.join('receipts', os.path.basename(html_filepath))

        logger.info(f"Generated receipt PDF: {filepath}")
        return os.path.join('receipts', filename)

    except Exception as e:
        logger.error(f"Error generating receipt PDF: {str(e)}")
        return None
