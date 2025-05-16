from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_TEACHER, StudentProfile
from app.models.attendance import Class, Attendance, Sport, SportsAttendance
from app.models.academic import Homework, HomeworkSubmission, Notification
from app.utils.decorators import teacher_required
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    # Get teacher's profile
    teacher_profile = current_user.teacher_profile

    # Get page parameter for classes pagination (default to page 1)
    page = request.args.get('page', 1, type=int)

    # Get teacher's classes with pagination (10 per page)
    classes_pagination = Class.query.filter_by(teacher_id=teacher_profile.id).paginate(page=page, per_page=10, error_out=False)

    # Get sports
    sports = Sport.query.filter_by(instructor_id=teacher_profile.id).all()

    # Get homeworks
    homeworks = Homework.query.filter_by(created_by=current_user.id).order_by(Homework.created_at.desc()).limit(10).all()

    # Get notifications
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()

    return render_template('teacher/dashboard.html',
                          title='Teacher Dashboard',
                          teacher_profile=teacher_profile,
                          classes_pagination=classes_pagination,
                          sports=sports,
                          homeworks=homeworks,
                          notifications=notifications,
                          now=datetime.utcnow)

@teacher_bp.route('/classes')
@login_required
@teacher_required
def class_list():
    teacher_profile = current_user.teacher_profile
    classes = Class.query.filter_by(teacher_id=teacher_profile.id).all()
    return render_template('teacher/classes/list.html', title='My Classes', classes=classes)

@teacher_bp.route('/classes/<int:class_id>/attendance')
@login_required
@teacher_required
def class_attendance(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Ensure the teacher is assigned to this class
    if class_obj.teacher_id != current_user.teacher_profile.id:
        flash('You are not authorized to view this class', 'danger')
        return redirect(url_for('teacher.class_list'))

    # Get students in this class (based on grade and section)
    students = StudentProfile.query.filter_by(grade=class_obj.grade, section=class_obj.section).all()

    return render_template('teacher/classes/attendance.html',
                          title=f'Attendance - {class_obj.name}',
                          class_obj=class_obj,
                          students=students)

@teacher_bp.route('/homeworks')
@login_required
@teacher_required
def homework_list():
    homeworks = Homework.query.filter_by(created_by=current_user.id).order_by(Homework.created_at.desc()).all()
    return render_template('teacher/homeworks/list.html', title='Homeworks', homeworks=homeworks, now=datetime.utcnow)

@teacher_bp.route('/sports')
@login_required
@teacher_required
def sport_list():
    teacher_profile = current_user.teacher_profile
    sports = Sport.query.filter_by(instructor_id=teacher_profile.id).all()
    return render_template('teacher/sports/list.html', title='My Sports Classes', sports=sports)
