from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_STUDENT
from app.models.attendance import Attendance, SportsAttendance, Class
from app.models.academic import Homework, HomeworkSubmission, Notification
from app.models.finance import (
    FeeSchedule, StudentFeeStructure, SportFeeSchedule, TransportationFeeSchedule,
    STATUS_PENDING, STATUS_OVERDUE
)
from app.utils.decorators import student_required
from datetime import datetime, date

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get student profile
    student_profile = current_user.student_profile

    # Get recent notifications
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()

    # Get classes for this student
    classes = Class.query.filter_by(standard_id=student_profile.standard_id, section_id=student_profile.section_id).all()

    # Get sports the student is enrolled in
    sports = student_profile.sports.all()

    # Get attendance statistics
    attendances = Attendance.query.filter_by(student_id=student_profile.id).all()
    total_classes = len(attendances)
    present_count = sum(1 for a in attendances if a.status == 'present')
    absent_count = sum(1 for a in attendances if a.status == 'absent')
    late_count = sum(1 for a in attendances if a.status == 'late')
    excused_count = sum(1 for a in attendances if a.status == 'excused')

    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

    # Get pending homeworks
    pending_homeworks = []
    all_homeworks = []
    for class_obj in classes:
        homeworks = Homework.query.filter_by(class_id=class_obj.id).all()
        all_homeworks.extend(homeworks)
        for homework in homeworks:
            submission = HomeworkSubmission.query.filter_by(homework_id=homework.id, student_id=student_profile.id).first()
            if not submission and homework.due_date >= datetime.utcnow().date():
                pending_homeworks.append(homework)

    total_homeworks = len(all_homeworks)

    # Get fee schedules for this student
    # 1. Regular fee schedules
    student_fee_structures = StudentFeeStructure.query.filter_by(student_id=student_profile.id, is_active=True).all()
    fee_schedules = []
    for sfs in student_fee_structures:
        schedules = FeeSchedule.query.filter_by(
            student_fee_structure_id=sfs.id,
            status=STATUS_PENDING
        ).order_by(FeeSchedule.due_date).all()
        fee_schedules.extend(schedules)

    # 2. Sport fee schedules
    sport_fee_schedules = SportFeeSchedule.query.filter_by(
        student_id=student_profile.id,
        status=STATUS_PENDING
    ).order_by(SportFeeSchedule.due_date).all()

    # 3. Transportation fee schedules
    transportation_fee_schedules = []
    student_transportation = student_profile.student_transportation
    if student_transportation:
        for st in student_transportation:
            if st.is_active:
                schedules = TransportationFeeSchedule.query.filter_by(
                    student_transportation_id=st.id,
                    status=STATUS_PENDING
                ).order_by(TransportationFeeSchedule.due_date).all()
                transportation_fee_schedules.extend(schedules)

    # Combine all fee schedules and sort by due date
    all_fee_schedules = []
    today = date.today()

    # Add regular fee schedules
    for schedule in fee_schedules:
        fee_type = schedule.student_fee_structure.base_structure.category.name
        all_fee_schedules.append({
            'id': schedule.id,
            'type': 'regular',
            'name': schedule.student_fee_structure.base_structure.name,
            'fee_type': fee_type,
            'amount': schedule.amount,
            'due_date': schedule.due_date,
            'is_overdue': schedule.is_overdue,
            'days_overdue': schedule.days_overdue if schedule.is_overdue else 0
        })

    # Add sport fee schedules
    for schedule in sport_fee_schedules:
        all_fee_schedules.append({
            'id': schedule.id,
            'type': 'sport',
            'name': schedule.sport.name,
            'fee_type': 'Sports',
            'amount': schedule.amount,
            'due_date': schedule.due_date,
            'is_overdue': schedule.is_overdue,
            'days_overdue': schedule.days_overdue if schedule.is_overdue else 0
        })

    # Add transportation fee schedules
    for schedule in transportation_fee_schedules:
        all_fee_schedules.append({
            'id': schedule.id,
            'type': 'transportation',
            'name': schedule.student_transportation.transportation_fee.name,
            'fee_type': 'Transportation',
            'amount': schedule.amount,
            'due_date': schedule.due_date,
            'is_overdue': schedule.is_overdue,
            'days_overdue': schedule.days_overdue if schedule.is_overdue else 0
        })

    # Sort by due date
    all_fee_schedules.sort(key=lambda x: x['due_date'])

    # Separate upcoming and overdue fees
    upcoming_fees = [fee for fee in all_fee_schedules if not fee['is_overdue']]
    overdue_fees = [fee for fee in all_fee_schedules if fee['is_overdue']]

    # Count total fees
    total_fees = len(all_fee_schedules)
    overdue_count = len(overdue_fees)

    return render_template('student/dashboard.html',
                          title='Student Dashboard',
                          student_profile=student_profile,
                          notifications=notifications,
                          classes=classes,
                          sports=sports,
                          total_classes=total_classes,
                          present_count=present_count,
                          absent_count=absent_count,
                          late_count=late_count,
                          excused_count=excused_count,
                          attendance_percentage=attendance_percentage,
                          pending_homeworks=pending_homeworks,
                          total_homeworks=total_homeworks,
                          upcoming_fees=upcoming_fees,
                          overdue_fees=overdue_fees,
                          total_fees=total_fees,
                          overdue_count=overdue_count,
                          now=datetime.utcnow())

@student_bp.route('/attendance')
@login_required
@student_required
def attendance_list():
    # Redirect to the student_attendance blueprint
    return redirect(url_for('student_attendance.list'))

@student_bp.route('/homeworks')
@login_required
@student_required
def homework_list():
    student_profile = current_user.student_profile

    # Get classes for this student's standard and section
    classes = Class.query.filter_by(standard_id=student_profile.standard_id, section_id=student_profile.section_id).all()

    # Get homeworks for these classes
    homeworks = []
    for class_obj in classes:
        class_homeworks = Homework.query.filter_by(class_id=class_obj.id).all()
        homeworks.extend(class_homeworks)

    # Get submissions for these homeworks
    submissions = {}
    for homework in homeworks:
        submission = HomeworkSubmission.query.filter_by(homework_id=homework.id, student_id=student_profile.id).first()
        if submission:
            submissions[homework.id] = submission

    return render_template('student/homeworks/list.html',
                          title='My Homeworks',
                          homeworks=homeworks,
                          submissions=submissions,
                          now=datetime.utcnow())

@student_bp.route('/notifications')
@login_required
@student_required
def notification_list():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('student/notifications/list.html', title='Notifications', notifications=notifications)

@student_bp.route('/fees')
@login_required
@student_required
def fees():
    # Get student profile
    student_profile = current_user.student_profile

    # Get fee schedules for this student
    # 1. Regular fee schedules
    student_fee_structures = StudentFeeStructure.query.filter_by(student_id=student_profile.id, is_active=True).all()
    fee_schedules = []
    for sfs in student_fee_structures:
        schedules = FeeSchedule.query.filter_by(
            student_fee_structure_id=sfs.id,
            status=STATUS_PENDING
        ).order_by(FeeSchedule.due_date).all()
        fee_schedules.extend(schedules)

    # 2. Sport fee schedules
    sport_fee_schedules = SportFeeSchedule.query.filter_by(
        student_id=student_profile.id,
        status=STATUS_PENDING
    ).order_by(SportFeeSchedule.due_date).all()

    # 3. Transportation fee schedules
    transportation_fee_schedules = []
    student_transportation = student_profile.student_transportation
    if student_transportation:
        for st in student_transportation:
            if st.is_active:
                schedules = TransportationFeeSchedule.query.filter_by(
                    student_transportation_id=st.id,
                    status=STATUS_PENDING
                ).order_by(TransportationFeeSchedule.due_date).all()
                transportation_fee_schedules.extend(schedules)

    # Combine all fee schedules and sort by due date
    all_fee_schedules = []
    today = date.today()

    # Add regular fee schedules
    for schedule in fee_schedules:
        fee_type = schedule.student_fee_structure.base_structure.category.name
        all_fee_schedules.append({
            'id': schedule.id,
            'type': 'regular',
            'name': schedule.student_fee_structure.base_structure.name,
            'fee_type': fee_type,
            'amount': schedule.amount,
            'due_date': schedule.due_date,
            'is_overdue': schedule.is_overdue,
            'days_overdue': schedule.days_overdue if schedule.is_overdue else 0
        })

    # Add sport fee schedules
    for schedule in sport_fee_schedules:
        all_fee_schedules.append({
            'id': schedule.id,
            'type': 'sport',
            'name': schedule.sport.name,
            'fee_type': 'Sports',
            'amount': schedule.amount,
            'due_date': schedule.due_date,
            'is_overdue': schedule.is_overdue,
            'days_overdue': schedule.days_overdue if schedule.is_overdue else 0
        })

    # Add transportation fee schedules
    for schedule in transportation_fee_schedules:
        all_fee_schedules.append({
            'id': schedule.id,
            'type': 'transportation',
            'name': schedule.student_transportation.transportation_fee.name,
            'fee_type': 'Transportation',
            'amount': schedule.amount,
            'due_date': schedule.due_date,
            'is_overdue': schedule.is_overdue,
            'days_overdue': schedule.days_overdue if schedule.is_overdue else 0
        })

    # Sort by due date
    all_fee_schedules.sort(key=lambda x: x['due_date'])

    # Separate upcoming and overdue fees
    upcoming_fees = [fee for fee in all_fee_schedules if not fee['is_overdue']]
    overdue_fees = [fee for fee in all_fee_schedules if fee['is_overdue']]

    return render_template('student/fees/list.html',
                          title='My Fees',
                          student_profile=student_profile,
                          upcoming_fees=upcoming_fees,
                          overdue_fees=overdue_fees,
                          all_fees=all_fee_schedules,
                          now=datetime.utcnow())
