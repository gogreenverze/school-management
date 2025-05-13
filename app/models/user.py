from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# Role definitions
ROLE_ADMIN = 'admin'
ROLE_TEACHER = 'teacher'
ROLE_PARENT = 'parent'
ROLE_STUDENT = 'student'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    profile_image = db.Column(db.String(120), nullable=True)
    
    # Relationships
    admin_profile = db.relationship('AdminProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('TeacherProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    parent_profile = db.relationship('ParentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, first_name, last_name, role, password=None):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        return self.role == ROLE_ADMIN
    
    def is_teacher(self):
        return self.role == ROLE_TEACHER
    
    def is_parent(self):
        return self.role == ROLE_PARENT
    
    def is_student(self):
        return self.role == ROLE_STUDENT
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AdminProfile(db.Model):
    __tablename__ = 'admin_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    department = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<AdminProfile {self.id}>'

class TeacherProfile(db.Model):
    __tablename__ = 'teacher_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    subject = db.Column(db.String(64), nullable=True)
    qualification = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', lazy='dynamic')
    
    def __repr__(self):
        return f'<TeacherProfile {self.id}>'

class ParentProfile(db.Model):
    __tablename__ = 'parent_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(256), nullable=True)
    occupation = db.Column(db.String(64), nullable=True)
    
    # Relationships
    students = db.relationship('StudentProfile', backref='parent_profile', lazy='dynamic')
    
    def __repr__(self):
        return f'<ParentProfile {self.id}>'

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(10), nullable=True)
    admission_date = db.Column(db.Date, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_profiles.id'))
    
    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy='dynamic')
    sports_attendances = db.relationship('SportsAttendance', backref='student', lazy='dynamic')
    fee_payments = db.relationship('FeePayment', backref='student', lazy='dynamic')
    homework_submissions = db.relationship('HomeworkSubmission', backref='student', lazy='dynamic')
    
    def __repr__(self):
        return f'<StudentProfile {self.roll_number}>'
