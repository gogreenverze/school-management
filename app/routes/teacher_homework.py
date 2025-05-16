from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_TEACHER, StudentProfile
from app.models.attendance import Class
from app.models.academic import Homework, HomeworkSubmission, Notification
from app.forms.academic import HomeworkForm, HomeworkGradingForm
from app.utils.decorators import teacher_required
from datetime import datetime
import os
import uuid

teacher_homework_bp = Blueprint('teacher_homework', __name__, url_prefix='/teacher/homeworks')

@teacher_homework_bp.route('/')
@login_required
@teacher_required
def list():
    homeworks = Homework.query.filter_by(created_by=current_user.id).order_by(Homework.created_at.desc()).all()
    return render_template('teacher/homeworks/list.html',
                          title='Homeworks',
                          homeworks=homeworks,
                          now=datetime.utcnow)

@teacher_homework_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create():
    form = HomeworkForm()

    # Filter classes to only those taught by this teacher
    teacher_profile = current_user.teacher_profile
    form.class_id.choices = [(c.id, f"{c.name} - {c.subject}")
                           for c in Class.query.filter_by(teacher_id=teacher_profile.id, is_active=True).all()]

    if form.validate_on_submit():
        homework = Homework(
            title=form.title.data,
            description=form.description.data,
            class_id=form.class_id.data,
            due_date=form.due_date.data,
            max_score=form.max_score.data,
            created_by=current_user.id
        )

        # Handle file upload if provided
        if form.attachment.data:
            filename = secure_filename(f"{uuid.uuid4()}_{form.attachment.data.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homeworks', filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            form.attachment.data.save(filepath)
            homework.attachment = filename

        db.session.add(homework)

        # Create notifications for students in this class
        class_obj = Class.query.get(form.class_id.data)
        students = StudentProfile.query.filter_by(
            standard_id=class_obj.standard_id,
            section_id=class_obj.section_id
        ).all()

        for student in students:
            notification = Notification(
                user_id=student.user_id,
                title=f"New Homework: {homework.title}",
                message=f"A new homework has been assigned for {class_obj.name} due on {homework.due_date.strftime('%d-%m-%Y')}.",
                category="homework",
                related_id=homework.id
            )
            db.session.add(notification)

        db.session.commit()
        flash('Homework has been created successfully!', 'success')
        return redirect(url_for('teacher_homework.list'))

    return render_template('teacher/homeworks/create.html',
                          title='Create Homework',
                          form=form,
                          now=datetime.utcnow)

@teacher_homework_bp.route('/<int:homework_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit(homework_id):
    homework = Homework.query.get_or_404(homework_id)

    # Ensure the teacher created this homework
    if homework.created_by != current_user.id:
        flash('You are not authorized to edit this homework', 'danger')
        return redirect(url_for('teacher_homework.list'))

    form = HomeworkForm(obj=homework)

    # Filter classes to only those taught by this teacher
    teacher_profile = current_user.teacher_profile
    form.class_id.choices = [(c.id, f"{c.name} - {c.subject}")
                           for c in Class.query.filter_by(teacher_id=teacher_profile.id, is_active=True).all()]

    if form.validate_on_submit():
        homework.title = form.title.data
        homework.description = form.description.data
        homework.class_id = form.class_id.data
        homework.due_date = form.due_date.data
        homework.max_score = form.max_score.data

        # Handle file upload if provided
        if form.attachment.data:
            # Remove old attachment if exists
            if homework.attachment:
                old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homeworks', homework.attachment)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            filename = secure_filename(f"{uuid.uuid4()}_{form.attachment.data.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homeworks', filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            form.attachment.data.save(filepath)
            homework.attachment = filename

        db.session.commit()
        flash('Homework has been updated successfully!', 'success')
        return redirect(url_for('teacher_homework.list'))

    return render_template('teacher/homeworks/edit.html',
                          title='Edit Homework',
                          form=form,
                          homework=homework,
                          now=datetime.utcnow)

@teacher_homework_bp.route('/<int:homework_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete(homework_id):
    homework = Homework.query.get_or_404(homework_id)

    # Ensure the teacher created this homework
    if homework.created_by != current_user.id:
        flash('You are not authorized to delete this homework', 'danger')
        return redirect(url_for('teacher_homework.list'))

    # Remove attachment if exists
    if homework.attachment:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homeworks', homework.attachment)
        if os.path.exists(filepath):
            os.remove(filepath)

    # Delete related submissions
    HomeworkSubmission.query.filter_by(homework_id=homework.id).delete()

    # Delete related notifications
    Notification.query.filter_by(category="homework", related_id=homework.id).delete()

    db.session.delete(homework)
    db.session.commit()

    flash('Homework has been deleted successfully!', 'success')
    return redirect(url_for('teacher_homework.list'))

@teacher_homework_bp.route('/<int:homework_id>/submissions')
@login_required
@teacher_required
def submissions(homework_id):
    homework = Homework.query.get_or_404(homework_id)

    # Ensure the teacher created this homework
    if homework.created_by != current_user.id:
        flash('You are not authorized to view submissions for this homework', 'danger')
        return redirect(url_for('teacher_homework.list'))

    # Get all submissions for this homework
    submissions = HomeworkSubmission.query.filter_by(homework_id=homework.id).all()

    # Get all students who should submit this homework
    class_obj = getattr(homework, 'class')
    students = StudentProfile.query.filter_by(
        standard_id=class_obj.standard_id,
        section_id=class_obj.section_id
    ).all()

    # Create a dictionary of student_id -> submission
    submission_dict = {sub.student_id: sub for sub in submissions}

    return render_template('teacher/homeworks/submissions.html',
                          title=f'Submissions - {homework.title}',
                          homework=homework,
                          students=students,
                          submissions=submission_dict,
                          now=datetime.utcnow)

@teacher_homework_bp.route('/<int:homework_id>/submissions/<int:submission_id>/grade', methods=['GET', 'POST'])
@login_required
@teacher_required
def grade_submission(homework_id, submission_id):
    homework = Homework.query.get_or_404(homework_id)
    submission = HomeworkSubmission.query.get_or_404(submission_id)

    # Ensure the teacher created this homework
    if homework.created_by != current_user.id:
        flash('You are not authorized to grade submissions for this homework', 'danger')
        return redirect(url_for('teacher_homework.list'))

    # Ensure the submission is for this homework
    if submission.homework_id != homework.id:
        flash('Invalid submission', 'danger')
        return redirect(url_for('teacher_homework.submissions', homework_id=homework.id))

    form = HomeworkGradingForm(obj=submission)

    if form.validate_on_submit():
        submission.score = form.score.data
        submission.feedback = form.feedback.data
        submission.status = form.status.data
        submission.graded_by = current_user.id
        submission.graded_at = datetime.utcnow()

        db.session.commit()

        # Create notification for the student
        notification = Notification(
            user_id=submission.student.user_id,
            title=f"Homework Graded: {homework.title}",
            message=f"Your submission for '{homework.title}' has been graded. Score: {submission.score}/{homework.max_score}",
            category="homework",
            related_id=homework.id
        )
        db.session.add(notification)
        db.session.commit()

        flash('Submission has been graded successfully!', 'success')
        return redirect(url_for('teacher_homework.submissions', homework_id=homework.id))

    return render_template('teacher/homeworks/grade.html',
                          title=f'Grade Submission - {homework.title}',
                          form=form,
                          homework=homework,
                          submission=submission,
                          student=submission.student,
                          now=datetime.utcnow)
