from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_TEACHER, StudentProfile
from app.models.attendance import Class, Attendance, Sport, SportsAttendance
from app.models.academic import Notification
from app.forms.attendance import AttendanceForm, BulkAttendanceForm, SportsAttendanceForm, AttendanceReportForm, StudentAttendanceEntry
from app.utils.decorators import teacher_required
from datetime import datetime, date, timedelta
import calendar

teacher_attendance_bp = Blueprint('teacher_attendance', __name__, url_prefix='/teacher/attendance')

@teacher_attendance_bp.route('/classes')
@login_required
@teacher_required
def class_list():
    teacher_profile = current_user.teacher_profile
    classes = Class.query.filter_by(teacher_id=teacher_profile.id).all()
    return render_template('teacher/attendance/class_list.html',
                          title='Classes for Attendance',
                          classes=classes)

@teacher_attendance_bp.route('/classes/<int:class_id>')
@login_required
@teacher_required
def class_attendance_history(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Ensure the teacher is assigned to this class
    if class_obj.teacher_id != current_user.teacher_profile.id:
        flash('You are not authorized to view this class', 'danger')
        return redirect(url_for('teacher_attendance.class_list'))

    # Get attendance records for this class
    attendances = Attendance.query.filter_by(class_id=class_id).order_by(Attendance.date.desc()).all()

    # Group by date
    attendance_by_date = {}
    for attendance in attendances:
        date_str = attendance.date.strftime('%Y-%m-%d')
        if date_str not in attendance_by_date:
            attendance_by_date[date_str] = []
        attendance_by_date[date_str].append(attendance)

    return render_template('teacher/attendance/class_history.html',
                          title=f'Attendance History - {class_obj.name}',
                          class_obj=class_obj,
                          attendance_by_date=attendance_by_date)

@teacher_attendance_bp.route('/classes/<int:class_id>/mark', methods=['GET', 'POST'])
@login_required
@teacher_required
def mark_class_attendance(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Ensure the teacher is assigned to this class
    if class_obj.teacher_id != current_user.teacher_profile.id:
        flash('You are not authorized to mark attendance for this class', 'danger')
        return redirect(url_for('teacher_attendance.class_list'))

    # Get students in this class
    students = StudentProfile.query.filter_by(
        standard_id=class_obj.standard_id,
        section_id=class_obj.section_id
    ).all()

    if not students:
        flash('No students found in this class', 'warning')
        return redirect(url_for('teacher_attendance.class_list'))

    form = BulkAttendanceForm()
    form.class_id.data = class_id

    # Check if attendance already exists for today
    today = date.today()
    existing_attendance = Attendance.query.filter_by(
        class_id=class_id,
        date=today
    ).first()

    if request.method == 'GET':
        # Clear existing entries
        while len(form.entries) > 0:
            form.entries.pop_entry()

        # Initialize form with student entries
        for student in students:
            # Create a dictionary of data for this student
            student_data = {
                'student_id': student.id,
                'student_name': f"{student.user.first_name} {student.user.last_name} ({student.roll_number})",
                'status': 'present',
                'remarks': ''
            }

            # If attendance exists, pre-populate status
            if existing_attendance:
                student_attendance = Attendance.query.filter_by(
                    class_id=class_id,
                    student_id=student.id,
                    date=today
                ).first()

                if student_attendance:
                    student_data['status'] = student_attendance.status
                    student_data['remarks'] = student_attendance.remarks

            # Append entry to the form
            form.entries.append_entry(student_data)

    if form.validate_on_submit():
        attendance_date = form.date.data

        # Check if attendance already exists for the selected date
        existing_attendance = Attendance.query.filter_by(
            class_id=class_id,
            date=attendance_date
        ).first()

        if existing_attendance and attendance_date == today:
            # Delete existing attendance for today
            Attendance.query.filter_by(
                class_id=class_id,
                date=attendance_date
            ).delete()
        elif existing_attendance:
            flash(f'Attendance for {attendance_date.strftime("%d-%m-%Y")} already exists', 'warning')
            return redirect(url_for('teacher_attendance.class_attendance_history', class_id=class_id))

        # Create new attendance records
        for entry in form.entries:
            attendance = Attendance(
                student_id=entry.student_id.data,
                class_id=class_id,
                date=attendance_date,
                status=entry.status.data,
                remarks=entry.remarks.data,
                recorded_by=current_user.id
            )
            db.session.add(attendance)

            # Create notification for absent students
            if entry.status.data == 'absent':
                student = StudentProfile.query.get(entry.student_id.data)
                notification = Notification(
                    user_id=student.user_id,
                    title=f"Absent: {class_obj.name}",
                    message=f"You were marked absent for {class_obj.name} on {attendance_date.strftime('%d-%m-%Y')}.",
                    category="attendance",
                    related_id=class_id
                )
                db.session.add(notification)

                # Notify parent if exists
                if student.parent_id and student.parent_profile:
                    parent_notification = Notification(
                        user_id=student.parent_profile.user_id,
                        title=f"Child Absent: {class_obj.name}",
                        message=f"Your child {student.user.first_name} was marked absent for {class_obj.name} on {attendance_date.strftime('%d-%m-%Y')}.",
                        category="attendance",
                        related_id=class_id
                    )
                    db.session.add(parent_notification)

        db.session.commit()
        flash('Attendance has been marked successfully!', 'success')
        return redirect(url_for('teacher_attendance.class_attendance_history', class_id=class_id))

    return render_template('teacher/attendance/mark_class.html',
                          title=f'Mark Attendance - {class_obj.name}',
                          form=form,
                          class_obj=class_obj,
                          students=students,
                          today=today)

@teacher_attendance_bp.route('/sports')
@login_required
@teacher_required
def sports_list():
    teacher_profile = current_user.teacher_profile
    sports = Sport.query.filter_by(instructor_id=teacher_profile.id).all()
    return render_template('teacher/attendance/sports_list.html',
                          title='Sports for Attendance',
                          sports=sports)

@teacher_attendance_bp.route('/sports/<int:sport_id>')
@login_required
@teacher_required
def sport_attendance_history(sport_id):
    sport = Sport.query.get_or_404(sport_id)

    # Ensure the teacher is assigned to this sport
    if sport.instructor_id != current_user.teacher_profile.id:
        flash('You are not authorized to view this sport', 'danger')
        return redirect(url_for('teacher_attendance.sports_list'))

    # Get attendance records for this sport
    attendances = SportsAttendance.query.filter_by(sport_id=sport_id).order_by(SportsAttendance.date.desc()).all()

    # Group by date
    attendance_by_date = {}
    for attendance in attendances:
        date_str = attendance.date.strftime('%Y-%m-%d')
        if date_str not in attendance_by_date:
            attendance_by_date[date_str] = []
        attendance_by_date[date_str].append(attendance)

    return render_template('teacher/attendance/sport_history.html',
                          title=f'Attendance History - {sport.name}',
                          sport=sport,
                          attendance_by_date=attendance_by_date)

@teacher_attendance_bp.route('/sports/<int:sport_id>/mark', methods=['GET', 'POST'])
@login_required
@teacher_required
def mark_sport_attendance(sport_id):
    sport = Sport.query.get_or_404(sport_id)

    # Ensure the teacher is assigned to this sport
    if sport.instructor_id != current_user.teacher_profile.id:
        flash('You are not authorized to mark attendance for this sport', 'danger')
        return redirect(url_for('teacher_attendance.sports_list'))

    # Get students in this sport
    students = sport.students

    if not students:
        flash('No students found in this sport', 'warning')
        return redirect(url_for('teacher_attendance.sports_list'))

    form = SportsAttendanceForm()
    form.sport_id.data = sport_id

    # Check if attendance already exists for today
    today = date.today()
    existing_attendance = SportsAttendance.query.filter_by(
        sport_id=sport_id,
        date=today
    ).first()

    if request.method == 'GET':
        # Clear existing entries
        while len(form.entries) > 0:
            form.entries.pop_entry()

        # Initialize form with student entries
        for student in students:
            # Create a dictionary of data for this student
            student_data = {
                'student_id': student.id,
                'student_name': f"{student.user.first_name} {student.user.last_name} ({student.roll_number})",
                'status': 'present',
                'remarks': ''
            }

            # If attendance exists, pre-populate status
            if existing_attendance:
                student_attendance = SportsAttendance.query.filter_by(
                    sport_id=sport_id,
                    student_id=student.id,
                    date=today
                ).first()

                if student_attendance:
                    student_data['status'] = student_attendance.status
                    student_data['remarks'] = student_attendance.remarks

            # Append entry to the form
            form.entries.append_entry(student_data)

    if form.validate_on_submit():
        attendance_date = form.date.data

        # Check if attendance already exists for the selected date
        existing_attendance = SportsAttendance.query.filter_by(
            sport_id=sport_id,
            date=attendance_date
        ).first()

        if existing_attendance and attendance_date == today:
            # Delete existing attendance for today
            SportsAttendance.query.filter_by(
                sport_id=sport_id,
                date=attendance_date
            ).delete()
        elif existing_attendance:
            flash(f'Attendance for {attendance_date.strftime("%d-%m-%Y")} already exists', 'warning')
            return redirect(url_for('teacher_attendance.sport_attendance_history', sport_id=sport_id))

        # Create new attendance records
        for entry in form.entries:
            attendance = SportsAttendance(
                student_id=entry.student_id.data,
                sport_id=sport_id,
                date=attendance_date,
                status=entry.status.data,
                remarks=entry.remarks.data,
                recorded_by=current_user.id
            )
            db.session.add(attendance)

        db.session.commit()
        flash('Sports attendance has been marked successfully!', 'success')
        return redirect(url_for('teacher_attendance.sport_attendance_history', sport_id=sport_id))

    return render_template('teacher/attendance/mark_sport.html',
                          title=f'Mark Attendance - {sport.name}',
                          form=form,
                          sport=sport,
                          students=students,
                          today=today)
