from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User, StudentProfile, ParentProfile
from app.forms.auth import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.email import send_password_reset_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        print(f"Login attempt: Username={form.username.data}, Password={'*' * len(form.password.data)}")
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            print(f"No user found with username: {form.username.data}")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        if not user.check_password(form.password.data):
            print(f"Password check failed for user: {user.username}")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        print(f"Login successful for user: {user.username}, Role: {user.role}")
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.is_admin():
                next_page = url_for('admin.dashboard')
                print(f"Redirecting to admin dashboard: {next_page}")
            elif user.is_teacher():
                next_page = url_for('teacher.dashboard')
                print(f"Redirecting to teacher dashboard: {next_page}")
            elif user.is_parent():
                next_page = url_for('parent.dashboard')
                print(f"Redirecting to parent dashboard: {next_page}")
            elif user.is_student():
                next_page = url_for('student.dashboard')
                print(f"Redirecting to student dashboard: {next_page}")
            else:
                next_page = url_for('main.index')
                print(f"Redirecting to main index: {next_page}")

        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Create profile based on role
        if user.is_student():
            profile = StudentProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
        elif user.is_parent():
            profile = ParentProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    # Get the next parameter if it exists
    next_page = request.args.get('next')

    return render_template('auth/register.html', title='Register', form=form, next=next_page)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('auth/profile.html', title='User Profile')
