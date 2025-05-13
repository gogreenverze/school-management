from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_PARENT
from app.models.finance import FeePayment
from app.models.academic import Homework, HomeworkSubmission, Notification
from app.utils.decorators import parent_required

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')

@parent_bp.route('/dashboard')
@login_required
@parent_required
def dashboard():
    # Get parent's children
    parent_profile = current_user.parent_profile
    children = parent_profile.students.all()
    
    # Get recent notifications
    recent_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get pending fee payments
    pending_fees = []
    for child in children:
        child_fees = FeePayment.query.filter_by(student_id=child.id, status='pending').all()
        pending_fees.extend(child_fees)
    
    return render_template('parent/dashboard.html', 
                          title='Parent Dashboard',
                          children=children,
                          recent_notifications=recent_notifications,
                          pending_fees=pending_fees)

@parent_bp.route('/children')
@login_required
@parent_required
def children_list():
    parent_profile = current_user.parent_profile
    children = parent_profile.students.all()
    return render_template('parent/children/list.html', title='My Children', children=children)

@parent_bp.route('/children/<int:student_id>/attendance')
@login_required
@parent_required
def child_attendance(student_id):
    # Verify this is the parent's child
    parent_profile = current_user.parent_profile
    student = parent_profile.students.filter_by(id=student_id).first_or_404()
    
    # Get attendance records
    attendances = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
    sports_attendances = SportsAttendance.query.filter_by(student_id=student_id).order_by(SportsAttendance.date.desc()).all()
    
    return render_template('parent/children/attendance.html', 
                          title=f'Attendance - {student.user.get_full_name()}',
                          student=student,
                          attendances=attendances,
                          sports_attendances=sports_attendances)

@parent_bp.route('/children/<int:student_id>/homework')
@login_required
@parent_required
def child_homework(student_id):
    # Verify this is the parent's child
    parent_profile = current_user.parent_profile
    student = parent_profile.students.filter_by(id=student_id).first_or_404()
    
    # Get homework submissions
    submissions = HomeworkSubmission.query.filter_by(student_id=student_id).order_by(HomeworkSubmission.submission_date.desc()).all()
    
    return render_template('parent/children/homework.html', 
                          title=f'Homework - {student.user.get_full_name()}',
                          student=student,
                          submissions=submissions)

@parent_bp.route('/fees')
@login_required
@parent_required
def fee_list():
    parent_profile = current_user.parent_profile
    children = parent_profile.students.all()
    
    # Get fee payments for all children
    fee_payments = []
    for child in children:
        child_fees = FeePayment.query.filter_by(student_id=child.id).order_by(FeePayment.payment_date.desc()).all()
        fee_payments.extend(child_fees)
    
    return render_template('parent/fees/list.html', title='Fee Payments', fee_payments=fee_payments)

@parent_bp.route('/notifications')
@login_required
@parent_required
def notification_list():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('parent/notifications/list.html', title='Notifications', notifications=notifications)
