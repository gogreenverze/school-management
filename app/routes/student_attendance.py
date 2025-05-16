from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_STUDENT
from app.models.attendance import Attendance, SportsAttendance, Class, Sport
from app.utils.decorators import student_required
from datetime import datetime, timedelta
import calendar
from collections import defaultdict

student_attendance_bp = Blueprint('student_attendance', __name__, url_prefix='/student/attendance')

@student_attendance_bp.route('/')
@login_required
@student_required
def list():
    student_profile = current_user.student_profile

    # Get attendance records
    attendances = Attendance.query.filter_by(student_id=student_profile.id).order_by(Attendance.date.desc()).all()

    # Add class_obj attribute to each attendance record
    for attendance in attendances:
        # Get the class object using the class_id
        class_obj = Class.query.get(attendance.class_id)
        attendance.class_obj = class_obj

    sports_attendances = SportsAttendance.query.filter_by(student_id=student_profile.id).order_by(SportsAttendance.date.desc()).all()

    # Calculate attendance statistics
    total_class_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status == 'present')
    absent_days = sum(1 for a in attendances if a.status == 'absent')
    late_days = sum(1 for a in attendances if a.status == 'late')
    excused_days = sum(1 for a in attendances if a.status == 'excused')

    attendance_rate = (present_days / total_class_days * 100) if total_class_days > 0 else 0

    # Calculate sports attendance statistics
    total_sports_days = len(sports_attendances)
    sports_present_days = sum(1 for a in sports_attendances if a.status == 'present')
    sports_absent_days = sum(1 for a in sports_attendances if a.status == 'absent')
    sports_late_days = sum(1 for a in sports_attendances if a.status == 'late')
    sports_excused_days = sum(1 for a in sports_attendances if a.status == 'excused')

    sports_attendance_rate = (sports_present_days / total_sports_days * 100) if total_sports_days > 0 else 0

    # Group attendance by month for chart
    attendance_by_month = defaultdict(lambda: {'present': 0, 'absent': 0, 'late': 0, 'excused': 0})

    for attendance in attendances:
        month_key = attendance.date.strftime('%Y-%m')
        attendance_by_month[month_key][attendance.status] += 1

    # Sort by month
    attendance_by_month = dict(sorted(attendance_by_month.items()))

    # Format for chart
    months = []
    present_counts = []
    absent_counts = []
    late_counts = []
    excused_counts = []

    for month, counts in attendance_by_month.items():
        year, month_num = month.split('-')
        month_name = calendar.month_name[int(month_num)]
        months.append(f"{month_name} {year}")
        present_counts.append(counts['present'])
        absent_counts.append(counts['absent'])
        late_counts.append(counts['late'])
        excused_counts.append(counts['excused'])

    return render_template('student/attendance/list.html',
                          title='My Attendance',
                          attendances=attendances,
                          sports_attendances=sports_attendances,
                          total_class_days=total_class_days,
                          present_days=present_days,
                          absent_days=absent_days,
                          late_days=late_days,
                          excused_days=excused_days,
                          attendance_rate=attendance_rate,
                          total_sports_days=total_sports_days,
                          sports_present_days=sports_present_days,
                          sports_absent_days=sports_absent_days,
                          sports_late_days=sports_late_days,
                          sports_excused_days=sports_excused_days,
                          sports_attendance_rate=sports_attendance_rate,
                          months=months,
                          present_counts=present_counts,
                          absent_counts=absent_counts,
                          late_counts=late_counts,
                          excused_counts=excused_counts)

@student_attendance_bp.route('/class/<int:class_id>')
@login_required
@student_required
def class_attendance(class_id):
    student_profile = current_user.student_profile
    class_obj = Class.query.get_or_404(class_id)

    # Check if student is in this class
    if class_obj.standard_id != student_profile.standard_id or (class_obj.section_id and class_obj.section_id != student_profile.section_id):
        flash('You are not enrolled in this class', 'danger')
        return redirect(url_for('student_attendance.list'))

    # Get attendance records for this class
    attendances = Attendance.query.filter_by(
        student_id=student_profile.id,
        class_id=class_id
    ).order_by(Attendance.date.desc()).all()

    # Calculate statistics
    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status == 'present')
    absent_days = sum(1 for a in attendances if a.status == 'absent')
    late_days = sum(1 for a in attendances if a.status == 'late')
    excused_days = sum(1 for a in attendances if a.status == 'excused')

    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

    return render_template('student/attendance/class.html',
                          title=f'Attendance - {class_obj.name}',
                          class_obj=class_obj,
                          attendances=attendances,
                          total_days=total_days,
                          present_days=present_days,
                          absent_days=absent_days,
                          late_days=late_days,
                          excused_days=excused_days,
                          attendance_rate=attendance_rate)

@student_attendance_bp.route('/sport/<int:sport_id>')
@login_required
@student_required
def sport_attendance(sport_id):
    student_profile = current_user.student_profile
    sport = Sport.query.get_or_404(sport_id)

    # Check if student is in this sport
    if student_profile not in sport.students:
        flash('You are not enrolled in this sport', 'danger')
        return redirect(url_for('student_attendance.list'))

    # Get attendance records for this sport
    attendances = SportsAttendance.query.filter_by(
        student_id=student_profile.id,
        sport_id=sport_id
    ).order_by(SportsAttendance.date.desc()).all()

    # Calculate statistics
    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status == 'present')
    absent_days = sum(1 for a in attendances if a.status == 'absent')
    late_days = sum(1 for a in attendances if a.status == 'late')
    excused_days = sum(1 for a in attendances if a.status == 'excused')

    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

    return render_template('student/attendance/sport.html',
                          title=f'Attendance - {sport.name}',
                          sport=sport,
                          attendances=attendances,
                          total_days=total_days,
                          present_days=present_days,
                          absent_days=absent_days,
                          late_days=late_days,
                          excused_days=excused_days,
                          attendance_rate=attendance_rate)
