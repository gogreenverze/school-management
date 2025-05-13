from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_STUDENT
from app.models.attendance import Attendance, SportsAttendance
from app.models.academic import Homework, HomeworkSubmission, Notification
from app.utils.decorators import student_required

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get student profile
    student_profile = current_user.student_profile
    
    # Get recent notifications
    recent_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get recent attendance
    recent_attendances = Attendance.query.filter_by(student_id=student_profile.id).order_by(Attendance.date.desc()).limit(5).all()
    
    # Get pending homeworks
    pending_homeworks = []
    classes = Class.query.filter_by(grade=student_profile.grade, section=student_profile.section).all()
    for class_obj in classes:
        homeworks = Homework.query.filter_by(class_id=class_obj.id).all()
        for homework in homeworks:
            submission = HomeworkSubmission.query.filter_by(homework_id=homework.id, student_id=student_profile.id).first()
            if not submission and homework.due_date >= datetime.utcnow().date():
                pending_homeworks.append(homework)
    
    return render_template('student/dashboard.html', 
                          title='Student Dashboard',
                          student=student_profile,
                          recent_notifications=recent_notifications,
                          recent_attendances=recent_attendances,
                          pending_homeworks=pending_homeworks)

@student_bp.route('/attendance')
@login_required
@student_required
def attendance_list():
    student_profile = current_user.student_profile
    attendances = Attendance.query.filter_by(student_id=student_profile.id).order_by(Attendance.date.desc()).all()
    sports_attendances = SportsAttendance.query.filter_by(student_id=student_profile.id).order_by(SportsAttendance.date.desc()).all()
    
    return render_template('student/attendance/list.html', 
                          title='My Attendance',
                          attendances=attendances,
                          sports_attendances=sports_attendances)

@student_bp.route('/homeworks')
@login_required
@student_required
def homework_list():
    student_profile = current_user.student_profile
    
    # Get classes for this student's grade and section
    classes = Class.query.filter_by(grade=student_profile.grade, section=student_profile.section).all()
    
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
                          submissions=submissions)

@student_bp.route('/notifications')
@login_required
@student_required
def notification_list():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('student/notifications/list.html', title='Notifications', notifications=notifications)
