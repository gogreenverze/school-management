"""
Student routes for viewing invoices.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models.user import StudentProfile
from app.models.finance import (
    Invoice, InvoiceItem, InvoicePayment,
    INVOICE_STATUS_DRAFT, INVOICE_STATUS_SENT, INVOICE_STATUS_PAID, 
    INVOICE_STATUS_PARTIALLY_PAID, INVOICE_STATUS_OVERDUE, INVOICE_STATUS_CANCELLED
)
from app.utils.decorators import student_required
from app.utils.pdf_utils import generate_invoice_pdf
from datetime import datetime, date
import os

student_invoices_bp = Blueprint('student_invoices', __name__, url_prefix='/student/invoices')

@student_invoices_bp.route('/')
@login_required
@student_required
def list():
    """List all invoices for the current student"""
    # Get student profile
    student_profile = current_user.student_profile
    
    # Get invoices
    invoices = Invoice.query.filter_by(student_id=student_profile.id).filter(
        Invoice.status != INVOICE_STATUS_DRAFT  # Don't show draft invoices to students
    ).order_by(Invoice.created_at.desc()).all()
    
    # Get statistics
    total_invoices = len(invoices)
    total_amount = sum(invoice.total_amount for invoice in invoices)
    total_paid = sum(invoice.amount_paid for invoice in invoices)
    total_balance = sum(invoice.balance for invoice in invoices)
    
    # Separate invoices by status
    pending_invoices = [inv for inv in invoices if inv.status in [INVOICE_STATUS_SENT, INVOICE_STATUS_PARTIALLY_PAID]]
    overdue_invoices = [inv for inv in invoices if inv.status == INVOICE_STATUS_OVERDUE]
    paid_invoices = [inv for inv in invoices if inv.status == INVOICE_STATUS_PAID]
    
    return render_template('student/invoices/list.html',
                          title='My Invoices',
                          invoices=invoices,
                          pending_invoices=pending_invoices,
                          overdue_invoices=overdue_invoices,
                          paid_invoices=paid_invoices,
                          total_invoices=total_invoices,
                          total_amount=total_amount,
                          total_paid=total_paid,
                          total_balance=total_balance)

@student_invoices_bp.route('/<int:id>/view')
@login_required
@student_required
def view(id):
    """View an invoice"""
    # Get student profile
    student_profile = current_user.student_profile
    
    # Get invoice
    invoice = Invoice.query.filter_by(id=id, student_id=student_profile.id).first_or_404()
    
    # Don't allow viewing draft invoices
    if invoice.status == INVOICE_STATUS_DRAFT:
        flash('This invoice is not available for viewing.', 'warning')
        return redirect(url_for('student_invoices.list'))
    
    # Get invoice items and payments
    items = InvoiceItem.query.filter_by(invoice_id=id).all()
    payments = InvoicePayment.query.filter_by(invoice_id=id).all()
    
    return render_template('student/invoices/view.html',
                          title=f'Invoice #{invoice.invoice_number}',
                          invoice=invoice,
                          items=items,
                          payments=payments)

@student_invoices_bp.route('/<int:id>/download_pdf')
@login_required
@student_required
def download_pdf(id):
    """Download PDF for an invoice"""
    # Get student profile
    student_profile = current_user.student_profile
    
    # Get invoice
    invoice = Invoice.query.filter_by(id=id, student_id=student_profile.id).first_or_404()
    
    # Don't allow downloading draft invoices
    if invoice.status == INVOICE_STATUS_DRAFT:
        flash('This invoice is not available for download.', 'warning')
        return redirect(url_for('student_invoices.list'))
    
    if not invoice.pdf_path:
        # Generate PDF if not already generated
        pdf_path = generate_invoice_pdf(id)
        if not pdf_path:
            flash('Error generating invoice PDF!', 'danger')
            return redirect(url_for('student_invoices.view', id=id))
    
    # Get the directory and filename
    directory = os.path.dirname(invoice.pdf_path)
    filename = os.path.basename(invoice.pdf_path)
    
    # Serve the file
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER'], directory),
        filename,
        as_attachment=True,
        download_name=f"Invoice_{invoice.invoice_number}.pdf"
    )
