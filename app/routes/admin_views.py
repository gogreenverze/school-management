from flask import redirect, url_for, flash, request, Markup
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_login import current_user
from app.models.user import User, AdminProfile, TeacherProfile, ParentProfile, StudentProfile
from app.models.attendance import Attendance, SportsAttendance, Class, Sport
from app.models.finance import FeeCategory, FeeStructure, FeePayment, FeeReminder
from app.models.academic import Homework, HomeworkSubmission, Notification, ContentBlock
from app.models.academic_structure import Board, Standard, Section

class SecureModelView(ModelView):
    page_size = 2  # Set default page size to 2 records per page for desktop
    can_view_details = True  # Enable details view
    can_export = True  # Enable export

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('You need to be an administrator to access this page.', 'danger')
        return redirect(url_for('auth.login'))

class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need to be an administrator to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return super(SecureAdminIndexView, self).index()

class UserModelView(SecureModelView):
    column_list = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'last_login']
    column_searchable_list = ['username', 'email', 'first_name', 'last_name']
    column_filters = ['role', 'is_active']
    form_excluded_columns = ['password_hash', 'created_at', 'last_login', 'admin_profile',
                            'teacher_profile', 'parent_profile', 'student_profile', 'notifications']

class ContentBlockModelView(SecureModelView):
    column_list = ['name', 'title', 'location', 'order', 'is_active', 'updated_at']
    column_searchable_list = ['name', 'title', 'content']
    column_filters = ['location', 'is_active']
    form_excluded_columns = ['created_by', 'created_at', 'updated_at', 'creator']

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id

class AttendanceModelView(SecureModelView):
    column_list = ['student', 'class', 'date', 'status', 'recorded_by', 'created_at']
    column_searchable_list = ['date', 'status']
    column_filters = ['date', 'status', 'class_id', 'student_id']

class SportsAttendanceModelView(SecureModelView):
    column_list = ['student', 'sport', 'date', 'status', 'recorded_by', 'created_at']
    column_searchable_list = ['date', 'status']
    column_filters = ['date', 'status', 'sport_id', 'student_id']

class FeePaymentModelView(SecureModelView):
    column_list = ['student', 'fee_structure', 'amount_paid', 'payment_date', 'payment_method', 'status']
    column_searchable_list = ['receipt_number', 'transaction_id']
    column_filters = ['payment_date', 'status', 'payment_method']

class BoardModelView(SecureModelView):
    column_list = ['name', 'code', 'state', 'is_active']
    column_searchable_list = ['name', 'code', 'state']
    column_filters = ['state', 'is_active']
    column_labels = {
        'name': 'Board Name',
        'code': 'Board Code',
        'state': 'State',
        'is_active': 'Active'
    }
    column_formatters = {
        'name': lambda v, c, m, p: Markup(f'<i class="fa fa-university"></i> {m.name}'),
        'is_active': lambda v, c, m, p: Markup(f'<span class="badge badge-{"success" if m.is_active else "danger"}">{m.is_active}</span>')
    }

class StandardModelView(SecureModelView):
    column_list = ['name', 'board', 'academic_year', 'is_active']
    column_searchable_list = ['name', 'academic_year']
    column_filters = ['board_id', 'academic_year', 'is_active']
    column_labels = {
        'name': 'Standard Name',
        'board': 'Education Board',
        'academic_year': 'Academic Year',
        'is_active': 'Active'
    }
    column_formatters = {
        'name': lambda v, c, m, p: Markup(f'<i class="fa fa-graduation-cap"></i> {m.name}'),
        'is_active': lambda v, c, m, p: Markup(f'<span class="badge badge-{"success" if m.is_active else "danger"}">{m.is_active}</span>')
    }

class SectionModelView(SecureModelView):
    column_list = ['name', 'standard', 'capacity', 'is_active']
    column_searchable_list = ['name']
    column_filters = ['standard_id', 'is_active']
    column_labels = {
        'name': 'Section Name',
        'standard': 'Standard',
        'capacity': 'Capacity',
        'is_active': 'Active'
    }
    column_formatters = {
        'name': lambda v, c, m, p: Markup(f'<i class="fa fa-users"></i> {m.name}'),
        'capacity': lambda v, c, m, p: Markup(f'<i class="fa fa-user"></i> {m.capacity}'),
        'is_active': lambda v, c, m, p: Markup(f'<span class="badge badge-{"success" if m.is_active else "danger"}">{m.is_active}</span>')
    }

class HomeworkModelView(SecureModelView):
    column_list = ['title', 'class', 'assigned_date', 'due_date', 'created_by']
    column_searchable_list = ['title', 'description']
    column_filters = ['assigned_date', 'due_date', 'class_id']
    column_labels = {
        'title': 'Homework Title',
        'class': 'Class',
        'assigned_date': 'Assigned Date',
        'due_date': 'Due Date',
        'created_by': 'Created By'
    }
    column_formatters = {
        'title': lambda v, c, m, p: Markup(f'<i class="fa fa-book"></i> {m.title}'),
        'assigned_date': lambda v, c, m, p: Markup(f'<i class="fa fa-calendar-check-o"></i> {m.assigned_date.strftime("%d-%m-%Y")}'),
        'due_date': lambda v, c, m, p: Markup(f'<i class="fa fa-calendar-times-o"></i> {m.due_date.strftime("%d-%m-%Y")}')
    }

def init_admin_views(admin, db):
    # Add model views
    admin.add_view(UserModelView(User, db.session, category='Users'))
    admin.add_view(SecureModelView(AdminProfile, db.session, category='Users'))
    admin.add_view(SecureModelView(TeacherProfile, db.session, category='Users'))
    admin.add_view(SecureModelView(ParentProfile, db.session, category='Users'))
    admin.add_view(SecureModelView(StudentProfile, db.session, category='Users'))

    # Academic Structure
    admin.add_view(BoardModelView(Board, db.session, category='Academic Structure'))
    admin.add_view(StandardModelView(Standard, db.session, category='Academic Structure'))
    admin.add_view(SectionModelView(Section, db.session, category='Academic Structure'))

    # Academic
    admin.add_view(SecureModelView(Class, db.session, category='Academic'))
    admin.add_view(AttendanceModelView(Attendance, db.session, category='Academic'))
    admin.add_view(HomeworkModelView(Homework, db.session, category='Academic'))
    admin.add_view(SecureModelView(HomeworkSubmission, db.session, category='Academic'))

    admin.add_view(SecureModelView(Sport, db.session, category='Sports'))
    # Temporarily comment out sports attendance to avoid backref conflicts
    # admin.add_view(SportsAttendanceModelView(SportsAttendance, db.session, category='Sports'))

    # Temporarily comment out fee models to avoid backref conflicts
    # admin.add_view(SecureModelView(FeeCategory, db.session, category='Finance'))
    # admin.add_view(SecureModelView(FeeStructure, db.session, category='Finance'))
    # admin.add_view(FeePaymentModelView(FeePayment, db.session, category='Finance'))
    # admin.add_view(SecureModelView(FeeReminder, db.session, category='Finance'))

    admin.add_view(SecureModelView(Notification, db.session, category='Communication'))
    admin.add_view(ContentBlockModelView(ContentBlock, db.session, category='Content'))
