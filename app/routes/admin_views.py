from flask import redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_login import current_user
from app.models.user import User, AdminProfile, TeacherProfile, ParentProfile, StudentProfile
from app.models.attendance import Attendance, SportsAttendance, Class, Sport
from app.models.finance import FeeCategory, FeeStructure, FeePayment, FeeReminder
from app.models.academic import Homework, HomeworkSubmission, Notification, ContentBlock

class SecureModelView(ModelView):
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
    can_view_details = True
    can_export = True

class ContentBlockModelView(SecureModelView):
    column_list = ['name', 'title', 'location', 'order', 'is_active', 'updated_at']
    column_searchable_list = ['name', 'title', 'content']
    column_filters = ['location', 'is_active']
    form_excluded_columns = ['created_by', 'created_at', 'updated_at', 'creator']
    can_view_details = True
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_by = current_user.id

class AttendanceModelView(SecureModelView):
    column_list = ['student', 'class', 'date', 'status', 'recorded_by', 'created_at']
    column_searchable_list = ['date', 'status']
    column_filters = ['date', 'status', 'class_id', 'student_id']
    can_view_details = True
    can_export = True

class SportsAttendanceModelView(SecureModelView):
    column_list = ['student', 'sport', 'date', 'status', 'recorded_by', 'created_at']
    column_searchable_list = ['date', 'status']
    column_filters = ['date', 'status', 'sport_id', 'student_id']
    can_view_details = True
    can_export = True

class FeePaymentModelView(SecureModelView):
    column_list = ['student', 'fee_structure', 'amount_paid', 'payment_date', 'payment_method', 'status']
    column_searchable_list = ['receipt_number', 'transaction_id']
    column_filters = ['payment_date', 'status', 'payment_method']
    can_view_details = True
    can_export = True

class HomeworkModelView(SecureModelView):
    column_list = ['title', 'class', 'assigned_date', 'due_date', 'created_by']
    column_searchable_list = ['title', 'description']
    column_filters = ['assigned_date', 'due_date', 'class_id']
    can_view_details = True

def init_admin_views(admin, db):
    # Override default index view
    admin.index_view = SecureAdminIndexView()
    
    # Add model views
    admin.add_view(UserModelView(User, db.session, category='Users'))
    admin.add_view(SecureModelView(AdminProfile, db.session, category='Users'))
    admin.add_view(SecureModelView(TeacherProfile, db.session, category='Users'))
    admin.add_view(SecureModelView(ParentProfile, db.session, category='Users'))
    admin.add_view(SecureModelView(StudentProfile, db.session, category='Users'))
    
    admin.add_view(SecureModelView(Class, db.session, category='Academic'))
    admin.add_view(AttendanceModelView(Attendance, db.session, category='Academic'))
    admin.add_view(HomeworkModelView(Homework, db.session, category='Academic'))
    admin.add_view(SecureModelView(HomeworkSubmission, db.session, category='Academic'))
    
    admin.add_view(SecureModelView(Sport, db.session, category='Sports'))
    admin.add_view(SportsAttendanceModelView(SportsAttendance, db.session, category='Sports'))
    
    admin.add_view(SecureModelView(FeeCategory, db.session, category='Finance'))
    admin.add_view(SecureModelView(FeeStructure, db.session, category='Finance'))
    admin.add_view(FeePaymentModelView(FeePayment, db.session, category='Finance'))
    admin.add_view(SecureModelView(FeeReminder, db.session, category='Finance'))
    
    admin.add_view(SecureModelView(Notification, db.session, category='Communication'))
    admin.add_view(ContentBlockModelView(ContentBlock, db.session, category='Content'))
