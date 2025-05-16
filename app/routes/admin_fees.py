"""
Admin routes for fee management.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, StudentProfile
from app.models.academic_structure import Standard, Section
from app.models.finance import (
    FeeCategory, FeeStructure, StudentFeeStructure, FeeSchedule, FeePayment, FeeReminder,
    TransportationFee, StudentTransportation, TransportationFeeSchedule, TransportationFeePayment,
    STATUS_PENDING, STATUS_COMPLETED, STATUS_OVERDUE
)
from app.forms.fees import (
    FeeCategoryForm, FeeStructureForm, StudentFeeStructureForm, FeePaymentForm,
    TransportationFeeForm, StudentTransportationForm, FeeReminderConfigForm
)
from app.utils.decorators import admin_required
from app.utils.fee_utils import (
    generate_fee_schedules, generate_transportation_fee_schedules,
    send_fee_reminders, send_overdue_reminders
)
from app.models.academic import Notification
from datetime import datetime, date
import uuid

admin_fees_bp = Blueprint('admin_fees', __name__, url_prefix='/admin_dashboard/fees')

@admin_fees_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Fee management dashboard"""
    # Get counts for dashboard
    total_fee_structures = FeeStructure.query.filter_by(is_active=True).count()
    total_student_fees = StudentFeeStructure.query.filter_by(is_active=True).count()
    total_transportation_fees = TransportationFee.query.filter_by(is_active=True).count()

    # Get payment statistics
    # Use a simpler query to avoid columns that might not exist in the database yet
    total_payments = db.session.query(FeePayment.id).count()
    total_amount_collected = db.session.query(db.func.sum(FeePayment.amount_paid)).scalar() or 0

    # Get pending payments
    pending_payments = FeeSchedule.query.filter_by(status=STATUS_PENDING).count()
    overdue_payments = FeeSchedule.query.filter(
        FeeSchedule.status == STATUS_PENDING,
        FeeSchedule.due_date < date.today()
    ).count()

    # Get recent payments - use a simpler query to avoid columns that might not exist
    recent_payments = db.session.query(FeePayment).order_by(FeePayment.payment_date.desc()).limit(5).all()

    return render_template('admin/fees/dashboard.html',
                          title='Fee Management Dashboard',
                          total_fee_structures=total_fee_structures,
                          total_student_fees=total_student_fees,
                          total_transportation_fees=total_transportation_fees,
                          total_payments=total_payments,
                          total_amount_collected=total_amount_collected,
                          pending_payments=pending_payments,
                          overdue_payments=overdue_payments,
                          recent_payments=recent_payments)

# Fee Category Routes
@admin_fees_bp.route('/categories')
@login_required
@admin_required
def category_list():
    """List fee categories"""
    categories = FeeCategory.query.order_by(FeeCategory.name).all()
    return render_template('admin/fees/categories/list.html',
                          title='Fee Categories',
                          categories=categories)

@admin_fees_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def category_create():
    """Create a new fee category"""
    form = FeeCategoryForm()

    if form.validate_on_submit():
        category = FeeCategory(
            name=form.name.data,
            description=form.description.data,
            is_recurring=form.is_recurring.data,
            frequency=form.frequency.data if form.is_recurring.data else None,
            fee_type=form.fee_type.data,
            is_active=form.is_active.data
        )
        db.session.add(category)
        db.session.commit()

        flash('Fee category created successfully!', 'success')
        return redirect(url_for('admin_fees.category_list'))

    return render_template('admin/fees/categories/create.html',
                          title='Create Fee Category',
                          form=form)

@admin_fees_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def category_edit(id):
    """Edit a fee category"""
    category = FeeCategory.query.get_or_404(id)
    form = FeeCategoryForm(obj=category)
    form.id = id

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.is_recurring = form.is_recurring.data
        category.frequency = form.frequency.data if form.is_recurring.data else None
        category.fee_type = form.fee_type.data
        category.is_active = form.is_active.data

        db.session.commit()

        flash('Fee category updated successfully!', 'success')
        return redirect(url_for('admin_fees.category_list'))

    return render_template('admin/fees/categories/edit.html',
                          title='Edit Fee Category',
                          form=form,
                          category=category)

@admin_fees_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def category_delete(id):
    """Delete a fee category"""
    category = FeeCategory.query.get_or_404(id)

    # Check if category is used in any fee structures
    if category.fee_structures.count() > 0:
        flash('Cannot delete category that is used in fee structures. Deactivate it instead.', 'danger')
        return redirect(url_for('admin_fees.category_list'))

    db.session.delete(category)
    db.session.commit()

    flash('Fee category deleted successfully!', 'success')
    return redirect(url_for('admin_fees.category_list'))

# Fee Structure Routes
@admin_fees_bp.route('/structures')
@login_required
@admin_required
def structure_list():
    """List fee structures"""
    structures = FeeStructure.query.order_by(FeeStructure.name).all()
    return render_template('admin/fees/structures/list.html',
                          title='Fee Structures',
                          structures=structures)

@admin_fees_bp.route('/structures/create', methods=['GET', 'POST'])
@login_required
@admin_required
def structure_create():
    """Create a new fee structure"""
    form = FeeStructureForm()

    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in FeeCategory.query.filter_by(is_active=True).order_by(FeeCategory.name).all()]

    # Populate standard and section choices
    form.standard_id.choices = [(0, 'All Standards')] + [(s.id, s.name) for s in Standard.query.filter_by(is_active=True).order_by(Standard.name).all()]
    form.section_id.choices = [(0, 'All Sections')] + [(s.id, s.name) for s in Section.query.filter_by(is_active=True).order_by(Section.name).all()]

    if form.validate_on_submit():
        structure = FeeStructure(
            category_id=form.category_id.data,
            standard_id=form.standard_id.data if form.standard_id.data > 0 else None,
            section_id=form.section_id.data if form.section_id.data > 0 else None,
            name=form.name.data,
            grade=form.grade.data,
            amount=form.amount.data,
            academic_year=form.academic_year.data,
            frequency=form.frequency.data,
            installments_allowed=form.installments_allowed.data,
            max_installments=form.max_installments.data if form.installments_allowed.data else 1,
            due_date=form.due_date.data,
            late_fee=form.late_fee.data,
            late_fee_frequency=form.late_fee_frequency.data,
            discount_available=form.discount_available.data,
            discount_percentage=form.discount_percentage.data if form.discount_available.data else 0.0,
            discount_conditions=form.discount_conditions.data,
            is_active=form.is_active.data
        )
        db.session.add(structure)
        db.session.commit()

        flash('Fee structure created successfully!', 'success')
        return redirect(url_for('admin_fees.structure_list'))

    return render_template('admin/fees/structures/create.html',
                          title='Create Fee Structure',
                          form=form)

@admin_fees_bp.route('/structures/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def structure_edit(id):
    """Edit a fee structure"""
    structure = FeeStructure.query.get_or_404(id)
    form = FeeStructureForm(obj=structure)

    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in FeeCategory.query.filter_by(is_active=True).order_by(FeeCategory.name).all()]

    # Populate standard and section choices
    form.standard_id.choices = [(0, 'All Standards')] + [(s.id, s.name) for s in Standard.query.filter_by(is_active=True).order_by(Standard.name).all()]
    form.section_id.choices = [(0, 'All Sections')] + [(s.id, s.name) for s in Section.query.filter_by(is_active=True).order_by(Section.name).all()]

    if structure.standard_id is None:
        form.standard_id.data = 0
    if structure.section_id is None:
        form.section_id.data = 0

    if form.validate_on_submit():
        structure.category_id = form.category_id.data
        structure.standard_id = form.standard_id.data if form.standard_id.data > 0 else None
        structure.section_id = form.section_id.data if form.section_id.data > 0 else None
        structure.name = form.name.data
        structure.grade = form.grade.data
        structure.amount = form.amount.data
        structure.academic_year = form.academic_year.data
        structure.frequency = form.frequency.data
        structure.installments_allowed = form.installments_allowed.data
        structure.max_installments = form.max_installments.data if form.installments_allowed.data else 1
        structure.due_date = form.due_date.data
        structure.late_fee = form.late_fee.data
        structure.late_fee_frequency = form.late_fee_frequency.data
        structure.discount_available = form.discount_available.data
        structure.discount_percentage = form.discount_percentage.data if form.discount_available.data else 0.0
        structure.discount_conditions = form.discount_conditions.data
        structure.is_active = form.is_active.data

        db.session.commit()

        flash('Fee structure updated successfully!', 'success')
        return redirect(url_for('admin_fees.structure_list'))

    return render_template('admin/fees/structures/edit.html',
                          title='Edit Fee Structure',
                          form=form,
                          structure=structure)

@admin_fees_bp.route('/structures/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def structure_delete(id):
    """Delete a fee structure"""
    structure = FeeStructure.query.get_or_404(id)

    # Check if structure is used in any student fee structures
    if structure.student_fee_structures.count() > 0:
        flash('Cannot delete structure that is assigned to students. Deactivate it instead.', 'danger')
        return redirect(url_for('admin_fees.structure_list'))

    db.session.delete(structure)
    db.session.commit()

    flash('Fee structure deleted successfully!', 'success')
    return redirect(url_for('admin_fees.structure_list'))

# Student Fee Assignment Routes
@admin_fees_bp.route('/student-fees')
@login_required
@admin_required
def student_fee_list():
    """List student fee assignments"""
    student_fees = StudentFeeStructure.query.order_by(StudentFeeStructure.created_at.desc()).all()
    return render_template('admin/fees/student_fees/list.html',
                          title='Student Fee Assignments',
                          student_fees=student_fees)

@admin_fees_bp.route('/student-fees/create', methods=['GET', 'POST'])
@login_required
@admin_required
def student_fee_create():
    """Create a new student fee assignment"""
    form = StudentFeeStructureForm()

    # Populate student choices
    form.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
                              for s in StudentProfile.query.join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()]

    # Populate fee structure choices
    form.fee_structure_id.choices = [(s.id, f"{s.name} - {s.grade} - ₹{s.amount}")
                                    for s in FeeStructure.query.filter_by(is_active=True).order_by(FeeStructure.name).all()]

    if form.validate_on_submit():
        # Check if student already has this fee structure
        existing = StudentFeeStructure.query.filter_by(
            student_id=form.student_id.data,
            fee_structure_id=form.fee_structure_id.data,
            is_active=True
        ).first()

        if existing:
            flash('This student already has this fee structure assigned.', 'danger')
            return redirect(url_for('admin_fees.student_fee_create'))

        student_fee = StudentFeeStructure(
            student_id=form.student_id.data,
            fee_structure_id=form.fee_structure_id.data,
            custom_amount=form.custom_amount.data,
            discount_percentage=form.discount_percentage.data,
            discount_reason=form.discount_reason.data,
            installments=form.installments.data,
            custom_due_date=form.custom_due_date.data,
            is_active=form.is_active.data,
            notes=form.notes.data
        )
        db.session.add(student_fee)
        db.session.commit()

        # Generate fee schedules
        generate_fee_schedules(student_fee)

        flash('Student fee assignment created successfully!', 'success')
        return redirect(url_for('admin_fees.student_fee_list'))

    return render_template('admin/fees/student_fees/create.html',
                          title='Create Student Fee Assignment',
                          form=form)

@admin_fees_bp.route('/student-fees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def student_fee_edit(id):
    """Edit a student fee assignment"""
    student_fee = StudentFeeStructure.query.get_or_404(id)
    form = StudentFeeStructureForm(obj=student_fee)

    # Populate student choices
    form.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
                              for s in StudentProfile.query.join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()]

    # Populate fee structure choices
    form.fee_structure_id.choices = [(s.id, f"{s.name} - {s.grade} - ₹{s.amount}")
                                    for s in FeeStructure.query.filter_by(is_active=True).order_by(FeeStructure.name).all()]

    if form.validate_on_submit():
        # Check if student already has this fee structure (if changed)
        if student_fee.fee_structure_id != form.fee_structure_id.data:
            existing = StudentFeeStructure.query.filter_by(
                student_id=form.student_id.data,
                fee_structure_id=form.fee_structure_id.data,
                is_active=True
            ).first()

            if existing and existing.id != id:
                flash('This student already has this fee structure assigned.', 'danger')
                return redirect(url_for('admin_fees.student_fee_edit', id=id))

        student_fee.student_id = form.student_id.data
        student_fee.fee_structure_id = form.fee_structure_id.data
        student_fee.custom_amount = form.custom_amount.data
        student_fee.discount_percentage = form.discount_percentage.data
        student_fee.discount_reason = form.discount_reason.data
        student_fee.installments = form.installments.data
        student_fee.custom_due_date = form.custom_due_date.data
        student_fee.is_active = form.is_active.data
        student_fee.notes = form.notes.data

        db.session.commit()

        # Regenerate fee schedules if needed
        if form.installments.data != student_fee.installments or form.custom_amount.data != student_fee.custom_amount:
            generate_fee_schedules(student_fee)

        flash('Student fee assignment updated successfully!', 'success')
        return redirect(url_for('admin_fees.student_fee_list'))

    return render_template('admin/fees/student_fees/edit.html',
                          title='Edit Student Fee Assignment',
                          form=form,
                          student_fee=student_fee)

@admin_fees_bp.route('/student-fees/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def student_fee_delete(id):
    """Delete a student fee assignment"""
    student_fee = StudentFeeStructure.query.get_or_404(id)

    # Check if there are any payments for this fee structure
    schedules_with_payments = FeeSchedule.query.filter_by(
        student_fee_structure_id=id,
        status=STATUS_COMPLETED
    ).count()

    if schedules_with_payments > 0:
        flash('Cannot delete fee assignment with completed payments. Deactivate it instead.', 'danger')
        return redirect(url_for('admin_fees.student_fee_list'))

    # Delete all pending schedules
    FeeSchedule.query.filter_by(student_fee_structure_id=id).delete()

    # Delete the student fee structure
    db.session.delete(student_fee)
    db.session.commit()

    flash('Student fee assignment deleted successfully!', 'success')
    return redirect(url_for('admin_fees.student_fee_list'))

@admin_fees_bp.route('/student-fees/<int:id>/schedules')
@login_required
@admin_required
def student_fee_schedules(id):
    """View fee schedules for a student fee assignment"""
    student_fee = StudentFeeStructure.query.get_or_404(id)
    schedules = FeeSchedule.query.filter_by(student_fee_structure_id=id).order_by(FeeSchedule.due_date).all()

    return render_template('admin/fees/student_fees/schedules.html',
                          title='Fee Schedules',
                          student_fee=student_fee,
                          schedules=schedules)

@admin_fees_bp.route('/student-fees/<int:id>/regenerate-schedules', methods=['POST'])
@login_required
@admin_required
def student_fee_regenerate_schedules(id):
    """Regenerate fee schedules for a student fee assignment"""
    student_fee = StudentFeeStructure.query.get_or_404(id)

    # Delete existing pending schedules and generate new ones
    generate_fee_schedules(student_fee)

    flash('Fee schedules regenerated successfully!', 'success')
    return redirect(url_for('admin_fees.student_fee_schedules', id=id))

# Fee Payment Routes
@admin_fees_bp.route('/payments')
@login_required
@admin_required
def payment_list():
    """List fee payments"""
    payments = FeePayment.query.order_by(FeePayment.payment_date.desc()).all()
    return render_template('admin/fees/payments/list.html',
                          title='Fee Payments',
                          payments=payments)

@admin_fees_bp.route('/payments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def payment_create():
    """Create a new fee payment"""
    form = FeePaymentForm()

    # Populate student choices
    form.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
                              for s in StudentProfile.query.join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()]

    # Populate fee structure choices (will be filtered by student via AJAX)
    form.fee_structure_id.choices = [(0, 'Select Student First')]

    # Populate fee schedule choices (will be filtered by fee structure via AJAX)
    form.fee_schedule_id.choices = [(0, 'Select Fee Structure First')]

    if form.validate_on_submit():
        # Generate receipt number
        receipt_number = f"FEE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        payment = FeePayment(
            student_id=form.student_id.data,
            fee_structure_id=form.fee_structure_id.data,
            amount_paid=form.amount_paid.data,
            payment_date=form.payment_date.data,
            payment_method=form.payment_method.data,
            transaction_id=form.transaction_id.data,
            receipt_number=receipt_number,
            status=STATUS_COMPLETED,
            late_fee_paid=form.late_fee_paid.data,
            discount_applied=form.discount_applied.data,
            remarks=form.remarks.data,
            collected_by=current_user.id,
            academic_year=form.academic_year.data
        )
        db.session.add(payment)

        # Update fee schedule if provided
        if form.fee_schedule_id.data and form.fee_schedule_id.data > 0:
            schedule = FeeSchedule.query.get(form.fee_schedule_id.data)
            if schedule:
                schedule.status = STATUS_COMPLETED
                schedule.payment_id = payment.id

        db.session.commit()

        # Create notification for student and parent
        student = StudentProfile.query.get(form.student_id.data)
        notification = Notification(
            user_id=student.user_id,
            title="Fee Payment Confirmation",
            message=f"Your fee payment of ₹{form.amount_paid.data} has been received. Receipt: {receipt_number}",
            category="fee",
            related_id=payment.id
        )
        db.session.add(notification)

        if student.parent_id and student.parent_profile:
            parent_notification = Notification(
                user_id=student.parent_profile.user_id,
                title="Fee Payment Confirmation",
                message=f"Fee payment of ₹{form.amount_paid.data} for {student.user.first_name} has been received. Receipt: {receipt_number}",
                category="fee",
                related_id=payment.id
            )
            db.session.add(parent_notification)

        db.session.commit()

        flash('Fee payment recorded successfully!', 'success')
        return redirect(url_for('admin_fees.payment_list'))

    return render_template('admin/fees/payments/create.html',
                          title='Record Fee Payment',
                          form=form)

@admin_fees_bp.route('/payments/<int:id>/view')
@login_required
@admin_required
def payment_view(id):
    """View a fee payment"""
    payment = FeePayment.query.get_or_404(id)
    return render_template('admin/fees/payments/view.html',
                          title='View Payment',
                          payment=payment)

@admin_fees_bp.route('/payments/<int:id>/receipt')
@login_required
@admin_required
def payment_receipt(id):
    """Generate a receipt for a fee payment"""
    payment = FeePayment.query.get_or_404(id)
    return render_template('admin/fees/payments/receipt.html',
                          title='Payment Receipt',
                          payment=payment)

# Transportation Fee Routes
@admin_fees_bp.route('/transportation')
@login_required
@admin_required
def transportation_list():
    """List transportation fees"""
    transportation_fees = TransportationFee.query.order_by(TransportationFee.name).all()
    return render_template('admin/fees/transportation/list.html',
                          title='Transportation Fees',
                          transportation_fees=transportation_fees)

@admin_fees_bp.route('/transportation/create', methods=['GET', 'POST'])
@login_required
@admin_required
def transportation_create():
    """Create a new transportation fee"""
    form = TransportationFeeForm()

    if form.validate_on_submit():
        transportation_fee = TransportationFee(
            name=form.name.data,
            route_description=form.route_description.data,
            distance_km=form.distance_km.data,
            amount=form.amount.data,
            frequency=form.frequency.data,
            pickup_time=form.pickup_time.data,
            drop_time=form.drop_time.data,
            vehicle_type=form.vehicle_type.data,
            capacity=form.capacity.data,
            late_fee=form.late_fee.data,
            late_fee_frequency=form.late_fee_frequency.data,
            is_active=form.is_active.data
        )
        db.session.add(transportation_fee)
        db.session.commit()

        flash('Transportation fee created successfully!', 'success')
        return redirect(url_for('admin_fees.transportation_list'))

    return render_template('admin/fees/transportation/create.html',
                          title='Create Transportation Fee',
                          form=form)

@admin_fees_bp.route('/transportation/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def transportation_edit(id):
    """Edit a transportation fee"""
    transportation_fee = TransportationFee.query.get_or_404(id)
    form = TransportationFeeForm(obj=transportation_fee)

    if form.validate_on_submit():
        transportation_fee.name = form.name.data
        transportation_fee.route_description = form.route_description.data
        transportation_fee.distance_km = form.distance_km.data
        transportation_fee.amount = form.amount.data
        transportation_fee.frequency = form.frequency.data
        transportation_fee.pickup_time = form.pickup_time.data
        transportation_fee.drop_time = form.drop_time.data
        transportation_fee.vehicle_type = form.vehicle_type.data
        transportation_fee.capacity = form.capacity.data
        transportation_fee.late_fee = form.late_fee.data
        transportation_fee.late_fee_frequency = form.late_fee_frequency.data
        transportation_fee.is_active = form.is_active.data

        db.session.commit()

        flash('Transportation fee updated successfully!', 'success')
        return redirect(url_for('admin_fees.transportation_list'))

    return render_template('admin/fees/transportation/edit.html',
                          title='Edit Transportation Fee',
                          form=form,
                          transportation_fee=transportation_fee)

@admin_fees_bp.route('/transportation/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def transportation_delete(id):
    """Delete a transportation fee"""
    transportation_fee = TransportationFee.query.get_or_404(id)

    # Check if fee is used by any students
    if transportation_fee.students.count() > 0:
        flash('Cannot delete transportation fee that is assigned to students. Deactivate it instead.', 'danger')
        return redirect(url_for('admin_fees.transportation_list'))

    db.session.delete(transportation_fee)
    db.session.commit()

    flash('Transportation fee deleted successfully!', 'success')
    return redirect(url_for('admin_fees.transportation_list'))

@admin_fees_bp.route('/student-transportation')
@login_required
@admin_required
def student_transportation_list():
    """List student transportation enrollments"""
    enrollments = StudentTransportation.query.order_by(StudentTransportation.created_at.desc()).all()
    return render_template('admin/fees/transportation/student_list.html',
                          title='Student Transportation Enrollments',
                          enrollments=enrollments)

@admin_fees_bp.route('/student-transportation/create', methods=['GET', 'POST'])
@login_required
@admin_required
def student_transportation_create():
    """Create a new student transportation enrollment"""
    form = StudentTransportationForm()

    # Populate student choices
    form.student_id.choices = [(s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
                              for s in StudentProfile.query.join(User).filter(StudentProfile.is_active==True).order_by(User.first_name).all()]

    # Populate transportation fee choices
    form.transportation_fee_id.choices = [(t.id, f"{t.name} - ₹{t.amount} ({t.frequency})")
                                         for t in TransportationFee.query.filter_by(is_active=True).order_by(TransportationFee.name).all()]

    if form.validate_on_submit():
        # Check if student already has active transportation
        existing = StudentTransportation.query.filter_by(
            student_id=form.student_id.data,
            is_active=True
        ).first()

        if existing:
            flash('This student already has active transportation enrollment. Please deactivate it first.', 'danger')
            return redirect(url_for('admin_fees.student_transportation_create'))

        enrollment = StudentTransportation(
            student_id=form.student_id.data,
            transportation_fee_id=form.transportation_fee_id.data,
            pickup_address=form.pickup_address.data,
            drop_address=form.drop_address.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            custom_amount=form.custom_amount.data,
            discount_percentage=form.discount_percentage.data,
            discount_reason=form.discount_reason.data,
            is_active=form.is_active.data,
            notes=form.notes.data
        )
        db.session.add(enrollment)
        db.session.commit()

        # Generate fee schedules
        generate_transportation_fee_schedules(enrollment)

        flash('Student transportation enrollment created successfully!', 'success')
        return redirect(url_for('admin_fees.student_transportation_list'))

    return render_template('admin/fees/transportation/student_create.html',
                          title='Create Transportation Enrollment',
                          form=form)

# AJAX Endpoints
@admin_fees_bp.route('/api/student/<int:student_id>/fee-structures')
@login_required
@admin_required
def api_student_fee_structures(student_id):
    """Get fee structures for a student"""
    # Get student's standard
    student = StudentProfile.query.get_or_404(student_id)

    # Get fee structures for this student's standard or all standards
    structures = FeeStructure.query.filter(
        (FeeStructure.standard_id == student.standard_id) |
        (FeeStructure.standard_id == None),
        FeeStructure.is_active == True
    ).all()

    # Format for select field
    result = [{'id': s.id, 'text': f"{s.name} - {s.grade} - ₹{s.amount}"} for s in structures]

    return jsonify(result)

@admin_fees_bp.route('/api/student/<int:student_id>/fee-structure/<int:structure_id>/schedules')
@login_required
@admin_required
def api_student_fee_schedules(student_id, structure_id):
    """Get fee schedules for a student and fee structure"""
    # Get student fee structure
    student_fee = StudentFeeStructure.query.filter_by(
        student_id=student_id,
        fee_structure_id=structure_id,
        is_active=True
    ).first()

    if not student_fee:
        return jsonify([])

    # Get pending schedules
    schedules = FeeSchedule.query.filter_by(
        student_fee_structure_id=student_fee.id,
        status=STATUS_PENDING
    ).order_by(FeeSchedule.due_date).all()

    # Format for select field
    result = [{'id': s.id, 'text': f"Installment {s.installment_number} - ₹{s.amount} - Due: {s.due_date.strftime('%d-%m-%Y')}"} for s in schedules]

    return jsonify(result)

@admin_fees_bp.route('/api/fee-schedule/<int:schedule_id>')
@login_required
@admin_required
def api_fee_schedule(schedule_id):
    """Get details of a fee schedule"""
    schedule = FeeSchedule.query.get_or_404(schedule_id)
    student_fee = schedule.student_fee_structure
    fee_structure = student_fee.base_structure

    # Calculate late fee if overdue
    late_fee = 0
    if schedule.is_overdue:
        late_fee = fee_structure.calculate_late_fee(date.today())

    result = {
        'amount': schedule.amount,
        'due_date': schedule.due_date.strftime('%Y-%m-%d'),
        'is_overdue': schedule.is_overdue,
        'days_overdue': schedule.days_overdue,
        'late_fee': late_fee
    }

    return jsonify(result)

# Reminder Configuration and Manual Sending
@admin_fees_bp.route('/reminders/config', methods=['GET', 'POST'])
@login_required
@admin_required
def reminder_config():
    """Configure fee reminders"""
    form = FeeReminderConfigForm()

    if form.validate_on_submit():
        # Store configuration in database or config file
        # For now, we'll just flash a message
        flash('Reminder configuration updated successfully!', 'success')
        return redirect(url_for('admin_fees.dashboard'))

    return render_template('admin/fees/reminders/config.html',
                          title='Configure Fee Reminders',
                          form=form)

@admin_fees_bp.route('/reminders/send-upcoming', methods=['POST'])
@login_required
@admin_required
def send_upcoming_reminders():
    """Manually send reminders for upcoming payments"""
    days_before = int(request.form.get('days_before', 7))
    notification_types = request.form.getlist('notification_types')

    if not notification_types:
        notification_types = ['email', 'whatsapp']

    count = send_fee_reminders(days_before, notification_types)

    flash(f'Sent {count} reminders for upcoming payments!', 'success')
    return redirect(url_for('admin_fees.dashboard'))

@admin_fees_bp.route('/reminders/send-overdue', methods=['POST'])
@login_required
@admin_required
def send_overdue_reminders_route():
    """Manually send reminders for overdue payments"""
    notification_types = request.form.getlist('notification_types')

    if not notification_types:
        notification_types = ['email', 'whatsapp']

    # Import the function from utils to avoid name conflict
    from app.utils.fee_utils import send_overdue_reminders as send_overdue_reminders_util
    count = send_overdue_reminders_util(notification_types)

    flash(f'Sent {count} reminders for overdue payments!', 'success')
    return redirect(url_for('admin_fees.dashboard'))

@admin_fees_bp.route('/reminders/history')
@login_required
@admin_required
def reminder_history():
    """View reminder history"""
    reminders = FeeReminder.query.order_by(FeeReminder.reminder_date.desc()).all()
    return render_template('admin/fees/reminders/history.html',
                          title='Reminder History',
                          reminders=reminders)
