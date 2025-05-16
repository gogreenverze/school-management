from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_STUDENT
from app.models.attendance import Class
from app.models.academic import Homework, HomeworkSubmission, Notification
from app.forms.academic import HomeworkSubmissionForm
from app.utils.decorators import student_required
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

student_homework_bp = Blueprint('student_homework', __name__, url_prefix='/student/homeworks')

@student_homework_bp.route('/')
@login_required
@student_required
def list():
    student_profile = current_user.student_profile

    # Get classes for this student's grade and section
    classes = Class.query.filter_by(
        standard_id=student_profile.standard_id,
        section_id=student_profile.section_id
    ).all()

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

    # Separate homeworks into categories
    pending_homeworks = []
    submitted_homeworks = []
    graded_homeworks = []
    past_due_homeworks = []

    for homework in homeworks:
        if homework.id in submissions:
            submission = submissions[homework.id]
            if submission.status == 'graded':
                graded_homeworks.append(homework)
            else:
                submitted_homeworks.append(homework)
        elif homework.due_date < datetime.utcnow().date():
            past_due_homeworks.append(homework)
        else:
            pending_homeworks.append(homework)

    return render_template('student/homeworks/list.html',
                          title='My Homeworks',
                          pending_homeworks=pending_homeworks,
                          submitted_homeworks=submitted_homeworks,
                          graded_homeworks=graded_homeworks,
                          past_due_homeworks=past_due_homeworks,
                          submissions=submissions,
                          now=datetime.utcnow)

@student_homework_bp.route('/<int:homework_id>')
@login_required
@student_required
def view(homework_id):
    student_profile = current_user.student_profile
    homework = Homework.query.get_or_404(homework_id)

    # Check if this homework is for a class the student is in
    class_obj = getattr(homework, 'class')
    if class_obj.standard_id != student_profile.standard_id or (class_obj.section_id and class_obj.section_id != student_profile.section_id):
        flash('You do not have access to this homework', 'danger')
        return redirect(url_for('student_homework.list'))

    # Get submission if exists
    submission = HomeworkSubmission.query.filter_by(homework_id=homework.id, student_id=student_profile.id).first()

    return render_template('student/homeworks/view.html',
                          title=f'Homework - {homework.title}',
                          homework=homework,
                          submission=submission,
                          now=datetime.utcnow)

@student_homework_bp.route('/<int:homework_id>/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit(homework_id):
    student_profile = current_user.student_profile
    homework = Homework.query.get_or_404(homework_id)

    # Check if this homework is for a class the student is in
    class_obj = getattr(homework, 'class')
    if class_obj.standard_id != student_profile.standard_id or (class_obj.section_id and class_obj.section_id != student_profile.section_id):
        flash('You do not have access to this homework', 'danger')
        return redirect(url_for('student_homework.list'))

    # Check if already submitted
    existing_submission = HomeworkSubmission.query.filter_by(homework_id=homework.id, student_id=student_profile.id).first()

    # Check if past due date
    is_late = homework.due_date < datetime.utcnow().date()

    form = HomeworkSubmissionForm()

    if form.validate_on_submit():
        if existing_submission:
            # Update existing submission
            existing_submission.content = form.content.data
            existing_submission.submission_date = datetime.utcnow()
            existing_submission.status = 'resubmitted' if existing_submission.status == 'graded' else 'submitted'

            # Handle file upload if provided
            if form.attachment.data:
                # Remove old attachment if exists
                if existing_submission.attachment:
                    old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'submissions', existing_submission.attachment)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)

                filename = secure_filename(f"{uuid.uuid4()}_{form.attachment.data.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'submissions', filename)

                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                form.attachment.data.save(filepath)
                existing_submission.attachment = filename

            db.session.commit()
            flash('Your homework has been updated successfully!', 'success')
        else:
            # Create new submission
            submission = HomeworkSubmission(
                homework_id=homework.id,
                student_id=student_profile.id,
                content=form.content.data,
                status='late' if is_late else 'submitted'
            )

            # Handle file upload if provided
            if form.attachment.data:
                filename = secure_filename(f"{uuid.uuid4()}_{form.attachment.data.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'submissions', filename)

                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                form.attachment.data.save(filepath)
                submission.attachment = filename

            db.session.add(submission)

            # Create notification for teacher
            notification = Notification(
                user_id=homework.teacher.id,
                title=f"Homework Submitted: {homework.title}",
                message=f"{student_profile.user.first_name} {student_profile.user.last_name} has submitted their homework for '{homework.title}'.",
                category="homework",
                related_id=homework.id
            )
            db.session.add(notification)

            db.session.commit()
            flash('Your homework has been submitted successfully!', 'success')

        return redirect(url_for('student_homework.view', homework_id=homework.id))

    # If GET request and existing submission, populate form
    if request.method == 'GET' and existing_submission:
        form.content.data = existing_submission.content

    return render_template('student/homeworks/submit.html',
                          title=f'Submit Homework - {homework.title}',
                          homework=homework,
                          form=form,
                          existing_submission=existing_submission,
                          is_late=is_late,
                          now=datetime.utcnow)
