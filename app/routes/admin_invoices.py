"""
Admin routes for invoice management.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, StudentProfile
from app.models.academic_structure import Standard, Section
from app.models.finance import (
    Invoice, InvoiceItem, InvoicePayment, FeePayment, SportFeePayment, TransportationFeePayment,
    FeeSchedule, SportFeeSchedule, TransportationFeeSchedule,
    INVOICE_STATUS_DRAFT, INVOICE_STATUS_SENT, INVOICE_STATUS_PAID,
    INVOICE_STATUS_PARTIALLY_PAID, INVOICE_STATUS_OVERDUE, INVOICE_STATUS_CANCELLED,
    INVOICE_TYPE_TUITION, INVOICE_TYPE_SPORTS, INVOICE_TYPE_TRANSPORTATION, INVOICE_TYPE_COMBINED
)
from app.forms.invoices import (
    InvoiceForm, InvoiceItemForm, InvoiceFilterForm, InvoiceStatusForm,
    InvoicePaymentForm, GenerateInvoicesForm
)
from app.utils.decorators import admin_required
from app.utils.pdf_utils import generate_invoice_pdf, generate_receipt_pdf
from app.models.academic import Notification
from datetime import datetime, date
import os

admin_invoices_bp = Blueprint('admin_invoices', __name__, url_prefix='/admin_dashboard/invoices')

@admin_invoices_bp.route('/')
@login_required
@admin_required
def index():
    """Invoice management dashboard"""
    # Get invoice statistics
    total_invoices = Invoice.query.count()
    draft_invoices = Invoice.query.filter_by(status=INVOICE_STATUS_DRAFT).count()
    sent_invoices = Invoice.query.filter_by(status=INVOICE_STATUS_SENT).count()
    paid_invoices = Invoice.query.filter_by(status=INVOICE_STATUS_PAID).count()
    partially_paid_invoices = Invoice.query.filter_by(status=INVOICE_STATUS_PARTIALLY_PAID).count()
    overdue_invoices = Invoice.query.filter_by(status=INVOICE_STATUS_OVERDUE).count()

    # Get total amounts
    total_amount = db.session.query(db.func.sum(Invoice.total_amount)).scalar() or 0
    total_paid = db.session.query(db.func.sum(Invoice.amount_paid)).scalar() or 0
    total_balance = db.session.query(db.func.sum(Invoice.balance)).scalar() or 0

    # Get recent invoices
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()

    return render_template('admin/invoices/dashboard.html',
                          title='Invoice Management',
                          total_invoices=total_invoices,
                          draft_invoices=draft_invoices,
                          sent_invoices=sent_invoices,
                          paid_invoices=paid_invoices,
                          partially_paid_invoices=partially_paid_invoices,
                          overdue_invoices=overdue_invoices,
                          total_amount=total_amount,
                          total_paid=total_paid,
                          total_balance=total_balance,
                          recent_invoices=recent_invoices)

@admin_invoices_bp.route('/list')
@login_required
@admin_required
def list():
    """List all invoices with filtering options"""
    form = InvoiceFilterForm()

    # Populate student choices
    form.student_id.choices = [(0, 'All Students')] + [
        (s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
        for s in StudentProfile.query.join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()
    ]

    # Get filter parameters
    student_id = request.args.get('student_id', type=int)
    invoice_type = request.args.get('invoice_type', '')
    status = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    academic_year = request.args.get('academic_year', '')

    # Build query with eager loading of relationships
    query = Invoice.query.options(db.joinedload(Invoice.student).joinedload(StudentProfile.user))

    if student_id and student_id > 0:
        query = query.filter(Invoice.student_id == student_id)
        form.student_id.data = student_id

    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
        form.invoice_type.data = invoice_type

    if status:
        query = query.filter(Invoice.status == status)
        form.status.data = status

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date >= date_from_obj)
            form.date_from.data = date_from_obj
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date <= date_to_obj)
            form.date_to.data = date_to_obj
        except ValueError:
            pass

    if academic_year:
        query = query.filter(Invoice.academic_year == academic_year)
        form.academic_year.data = academic_year

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 invoices per page
    try:
        # Try Flask-SQLAlchemy 3.x style pagination
        pagination = query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=per_page)
        invoices = pagination.items
    except TypeError:
        # Fall back to Flask-SQLAlchemy 2.x style pagination
        pagination = query.order_by(Invoice.created_at.desc()).paginate(page, per_page)
        invoices = pagination.items

    return render_template('admin/invoices/list.html',
                          title='Invoices',
                          invoices=invoices,
                          pagination=pagination,
                          form=form)

@admin_invoices_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create a new invoice"""
    form = InvoiceForm()

    # Populate student choices with eager loading
    students = StudentProfile.query.options(
        db.joinedload(StudentProfile.user),
        db.joinedload(StudentProfile.standard),
        db.joinedload(StudentProfile.section)
    ).join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()

    form.student_id.choices = [
        (s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
        for s in students if s.user  # Only include students with valid user relationships
    ]

    # Check if we have any students
    if not form.student_id.choices:
        flash('No active students found. Please create students first.', 'warning')
        return redirect(url_for('admin_invoices.index'))

    if form.validate_on_submit():
        # Generate invoice number
        invoice_number = Invoice.generate_invoice_number()

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            student_id=form.student_id.data,
            invoice_type=form.invoice_type.data,
            invoice_date=form.invoice_date.data,
            due_date=form.due_date.data,
            status=INVOICE_STATUS_DRAFT,
            subtotal=form.subtotal.data,
            discount=form.discount.data,
            tax=form.tax.data,
            late_fee=form.late_fee.data,
            total_amount=form.total_amount.data,
            amount_paid=form.amount_paid.data,
            balance=form.balance.data,
            notes=form.notes.data,
            terms=form.terms.data,
            created_by=current_user.id,
            academic_year=form.academic_year.data
        )

        db.session.add(invoice)
        db.session.commit()

        flash(f'Invoice {invoice_number} created successfully!', 'success')
        return redirect(url_for('admin_invoices.edit', id=invoice.id))

    # Default values
    if not form.academic_year.data:
        form.academic_year.data = f"{date.today().year}-{date.today().year + 1}"

    return render_template('admin/invoices/create.html',
                          title='Create Invoice',
                          form=form)

@admin_invoices_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit an invoice"""
    # Use joinedload to eagerly load relationships
    invoice = Invoice.query.options(
        db.joinedload(Invoice.student).joinedload(StudentProfile.user)
    ).get_or_404(id)

    form = InvoiceForm(obj=invoice)
    item_form = InvoiceItemForm()

    # Populate student choices
    form.student_id.choices = [
        (s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
        for s in StudentProfile.query.join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()
    ]

    # Populate sports choices for item form
    from app.models.attendance import Sport
    item_form.sport_id.choices = [(0, 'Select Sport')] + [(s.id, s.name) for s in Sport.query.filter_by(is_active=True).all()]

    # Get invoice items with eager loading of sport relationship
    items = InvoiceItem.query.options(
        db.joinedload(InvoiceItem.sport)
    ).filter_by(invoice_id=id).all()

    if form.validate_on_submit():
        # Update invoice
        invoice.student_id = form.student_id.data
        invoice.invoice_type = form.invoice_type.data
        invoice.invoice_date = form.invoice_date.data
        invoice.due_date = form.due_date.data
        invoice.subtotal = form.subtotal.data
        invoice.discount = form.discount.data
        invoice.tax = form.tax.data
        invoice.late_fee = form.late_fee.data
        invoice.total_amount = form.total_amount.data
        invoice.amount_paid = form.amount_paid.data
        invoice.balance = form.balance.data
        invoice.notes = form.notes.data
        invoice.terms = form.terms.data
        invoice.academic_year = form.academic_year.data

        db.session.commit()

        flash('Invoice updated successfully!', 'success')
        return redirect(url_for('admin_invoices.view', id=invoice.id))

    return render_template('admin/invoices/edit.html',
                          title='Edit Invoice',
                          invoice=invoice,
                          form=form,
                          item_form=item_form,
                          items=items)

@admin_invoices_bp.route('/<int:id>/view')
@login_required
@admin_required
def view(id):
    """View an invoice"""
    # Use joinedload to eagerly load relationships
    invoice = Invoice.query.options(
        db.joinedload(Invoice.student).joinedload(StudentProfile.user),
        db.joinedload(Invoice.creator)
    ).get_or_404(id)

    items = InvoiceItem.query.options(
        db.joinedload(InvoiceItem.sport)
    ).filter_by(invoice_id=id).all()

    payments = InvoicePayment.query.filter_by(invoice_id=id).all()

    # Get student details (already loaded via joinedload)
    student = invoice.student

    # Handle case where student might be None
    if not student:
        flash('Student information not found for this invoice.', 'warning')
        student = None

    # Create status update form
    status_form = InvoiceStatusForm()
    status_form.status.data = invoice.status  # Pre-select current status

    return render_template('admin/invoices/view.html',
                          title=f'Invoice #{invoice.invoice_number}',
                          invoice=invoice,
                          items=items,
                          payments=payments,
                          student=student,
                          status_form=status_form)

@admin_invoices_bp.route('/<int:id>/add_item', methods=['POST'])
@login_required
@admin_required
def add_item(id):
    """Add an item to an invoice"""
    try:
        # Get invoice with eager loading
        invoice = Invoice.query.options(
            db.joinedload(Invoice.student).joinedload(StudentProfile.user)
        ).get_or_404(id)

        form = InvoiceItemForm()

        # Populate sports choices
        from app.models.attendance import Sport
        form.sport_id.choices = [(0, 'Select Sport')] + [(s.id, s.name) for s in Sport.query.filter_by(is_active=True).all()]

        if form.validate_on_submit():
            try:
                item = InvoiceItem(
                    invoice_id=id,
                    description=form.description.data,
                    quantity=form.quantity.data,
                    unit_price=form.unit_price.data,
                    discount=form.discount.data,
                    total=form.total.data,
                    fee_type=form.fee_type.data,
                    fee_schedule_id=form.fee_schedule_id.data or None,
                    fee_schedule_type=form.fee_schedule_type.data or None
                )

                # Add sport_id if fee type is sports and sport is selected
                if form.fee_type.data == 'sports' and form.sport_id.data and form.sport_id.data > 0:
                    # Verify sport exists
                    sport = Sport.query.get(form.sport_id.data)
                    if sport:
                        item.sport_id = form.sport_id.data
                    else:
                        flash(f'Selected sport not found. Item added without sport reference.', 'warning')

                db.session.add(item)

                # Update invoice totals
                invoice.subtotal += item.total
                invoice.total_amount = invoice.subtotal - invoice.discount + invoice.tax + invoice.late_fee
                invoice.balance = invoice.total_amount - invoice.amount_paid

                db.session.commit()

                flash('Item added to invoice!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding item to invoice: {str(e)}', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}', 'danger')
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'danger')

    return redirect(url_for('admin_invoices.edit', id=id))

@admin_invoices_bp.route('/<int:id>/remove_item/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def remove_item(id, item_id):
    """Remove an item from an invoice"""
    try:
        invoice = Invoice.query.get_or_404(id)
        item = InvoiceItem.query.get_or_404(item_id)

        if item.invoice_id != id:
            flash('Item does not belong to this invoice!', 'danger')
            return redirect(url_for('admin_invoices.edit', id=id))

        try:
            # Update invoice totals
            invoice.subtotal -= item.total
            invoice.total_amount = invoice.subtotal - invoice.discount + invoice.tax + invoice.late_fee
            invoice.balance = invoice.total_amount - invoice.amount_paid

            db.session.delete(item)
            db.session.commit()

            flash('Item removed from invoice!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error removing item: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'danger')

    return redirect(url_for('admin_invoices.edit', id=id))

@admin_invoices_bp.route('/<int:id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_status(id):
    """Update invoice status"""
    try:
        # Get invoice with eager loading
        invoice = Invoice.query.options(
            db.joinedload(Invoice.student).joinedload(StudentProfile.user)
        ).get_or_404(id)

        form = InvoiceStatusForm()

        if form.validate_on_submit():
            try:
                old_status = invoice.status
                invoice.status = form.status.data

                if form.notes.data:
                    if invoice.notes:
                        invoice.notes += f"\n\n{datetime.now().strftime('%d-%m-%Y %H:%M')} - Status changed from {old_status} to {invoice.status}: {form.notes.data}"
                    else:
                        invoice.notes = f"{datetime.now().strftime('%d-%m-%Y %H:%M')} - Status changed from {old_status} to {invoice.status}: {form.notes.data}"

                db.session.commit()

                # If status changed to sent, generate PDF if not already generated
                if invoice.status == INVOICE_STATUS_SENT and not invoice.pdf_path:
                    try:
                        generate_invoice_pdf(invoice.id)
                    except Exception as e:
                        flash(f'Error generating PDF: {str(e)}. Status updated but PDF generation failed.', 'warning')

                # Create notification for student and parent if student exists
                if invoice.student and invoice.student.user:
                    student = invoice.student
                    try:
                        notification = Notification(
                            user_id=student.user_id,
                            title="Invoice Status Updated",
                            message=f"Your invoice #{invoice.invoice_number} status has been updated to {invoice.status.upper()}.",
                            category="invoice",
                            related_id=invoice.id
                        )
                        db.session.add(notification)

                        if student.parent_id and student.parent_profile and student.parent_profile.user:
                            parent_notification = Notification(
                                user_id=student.parent_profile.user_id,
                                title="Invoice Status Updated",
                                message=f"Invoice #{invoice.invoice_number} for {student.user.first_name} status has been updated to {invoice.status.upper()}.",
                                category="invoice",
                                related_id=invoice.id
                            )
                            db.session.add(parent_notification)

                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Error creating notifications: {str(e)}. Status updated but notifications failed.', 'warning')

                flash(f'Invoice status updated to {invoice.status.upper()}!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating status: {str(e)}', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}', 'danger')
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'danger')

    return redirect(url_for('admin_invoices.view', id=id))

@admin_invoices_bp.route('/<int:id>/generate_pdf')
@login_required
@admin_required
def generate_pdf(id):
    """Generate PDF for an invoice"""
    try:
        # Get invoice with eager loading
        invoice = Invoice.query.options(
            db.joinedload(Invoice.student).joinedload(StudentProfile.user),
            db.joinedload(Invoice.creator)
        ).get_or_404(id)

        try:
            pdf_path = generate_invoice_pdf(id)

            if pdf_path:
                flash('Invoice PDF generated successfully!', 'success')
            else:
                flash('Error generating invoice PDF!', 'danger')
        except Exception as e:
            flash(f'Error generating PDF: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'danger')

    return redirect(url_for('admin_invoices.view', id=id))

@admin_invoices_bp.route('/<int:id>/download_pdf')
@login_required
@admin_required
def download_pdf(id):
    """Download PDF for an invoice"""
    try:
        # Get invoice with eager loading
        invoice = Invoice.query.options(
            db.joinedload(Invoice.student).joinedload(StudentProfile.user),
            db.joinedload(Invoice.creator)
        ).get_or_404(id)

        if not invoice.pdf_path:
            # Generate PDF if not already generated
            try:
                pdf_path = generate_invoice_pdf(id)
                if not pdf_path:
                    flash('Error generating invoice PDF!', 'danger')
                    return redirect(url_for('admin_invoices.view', id=id))
            except Exception as e:
                flash(f'Error generating PDF: {str(e)}', 'danger')
                return redirect(url_for('admin_invoices.view', id=id))

        try:
            # Get the directory and filename
            directory = os.path.dirname(invoice.pdf_path)
            filename = os.path.basename(invoice.pdf_path)

            # Make sure UPLOAD_FOLDER is defined in config
            if 'UPLOAD_FOLDER' not in current_app.config:
                current_app.config['UPLOAD_FOLDER'] = os.path.join(current_app.root_path, 'static', 'uploads')
                # Create directory if it doesn't exist
                if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                    os.makedirs(current_app.config['UPLOAD_FOLDER'])

            # Check if file exists
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], directory, filename)
            if not os.path.exists(full_path):
                flash('PDF file not found. Generating a new one...', 'warning')
                pdf_path = generate_invoice_pdf(id)
                if not pdf_path:
                    flash('Error generating invoice PDF!', 'danger')
                    return redirect(url_for('admin_invoices.view', id=id))

                # Update directory and filename
                directory = os.path.dirname(invoice.pdf_path)
                filename = os.path.basename(invoice.pdf_path)

            # Serve the file
            return send_from_directory(
                os.path.join(current_app.config['UPLOAD_FOLDER'], directory),
                filename,
                as_attachment=True,
                download_name=f"Invoice_{invoice.invoice_number}.pdf"
            )
        except Exception as e:
            flash(f'Error downloading PDF: {str(e)}', 'danger')
            return redirect(url_for('admin_invoices.view', id=id))
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'danger')
        return redirect(url_for('admin_invoices.list'))
