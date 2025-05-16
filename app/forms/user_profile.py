from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField, DateField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, Email, EqualTo
from app.models.user import User, TeacherProfile, StudentProfile
from app.models.academic_structure import Standard, Section
from datetime import date

class TeacherProfileForm(FlaskForm):
    """Form for creating and editing teacher profiles"""
    # User information
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password')])

    # Teacher profile information
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    date_of_joining = DateField('Date of Joining', format='%Y-%m-%d', validators=[DataRequired()])
    primary_subject = StringField('Primary Subject', validators=[Length(max=64)])
    secondary_subjects = StringField('Secondary Subjects', validators=[Length(max=128)])
    qualification = StringField('Qualification', validators=[Length(max=128)])
    experience_years = IntegerField('Years of Experience', default=0)
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    emergency_contact = StringField('Emergency Contact', validators=[Length(max=20)])
    address = TextAreaField('Address')
    specialization = StringField('Specialization', validators=[Length(max=128)])
    bio = TextAreaField('Bio')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and getattr(self, 'user_id', None) != user.id:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and getattr(self, 'user_id', None) != user.id:
            raise ValidationError('Please use a different email address.')

    def validate_employee_id(self, employee_id):
        teacher = TeacherProfile.query.filter_by(employee_id=employee_id.data).first()
        if teacher is not None and getattr(self, 'id', None) != teacher.id:
            raise ValidationError('This Employee ID is already in use.')

class StudentProfileForm(FlaskForm):
    """Form for creating and editing student profiles"""
    # User information
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password')])

    # Student profile information
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    board_id = SelectField('Board', coerce=int, validators=[Optional()])
    standard_id = SelectField('Standard/Grade', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Section', coerce=int, validators=[Optional()])
    admission_date = DateField('Admission Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    parent_id = SelectField('Parent', coerce=int, validators=[Optional()])
    blood_group = StringField('Blood Group', validators=[Length(max=5)])
    address = TextAreaField('Address')
    emergency_contact = StringField('Emergency Contact', validators=[Length(max=20)])
    medical_conditions = TextAreaField('Medical Conditions')
    previous_school = StringField('Previous School', validators=[Length(max=128)])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and getattr(self, 'user_id', None) != user.id:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and getattr(self, 'user_id', None) != user.id:
            raise ValidationError('Please use a different email address.')

    def validate_roll_number(self, roll_number):
        student = StudentProfile.query.filter_by(roll_number=roll_number.data).first()
        if student is not None and getattr(self, 'id', None) != student.id:
            raise ValidationError('This Roll Number is already in use.')

class ClassAssignmentForm(FlaskForm):
    """Form for assigning teachers to classes"""
    name = StringField('Class Name', validators=[DataRequired(), Length(max=64)])
    standard_id = SelectField('Standard/Grade', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Section', coerce=int, validators=[Optional()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=64)])
    teacher_id = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    schedule = StringField('Schedule (e.g., Mon,Wed,Fri 10:00-11:00)', validators=[Length(max=128)])
    room = StringField('Room', validators=[Length(max=20)])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')
