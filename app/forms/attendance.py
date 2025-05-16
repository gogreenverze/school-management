from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField, DateField, HiddenField, FieldList, FormField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from datetime import date
from app.models.attendance import Class, Attendance, Sport
from app.models.user import StudentProfile

class AttendanceForm(FlaskForm):
    """Form for marking attendance for a single student"""
    student_id = HiddenField('Student ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ], validators=[DataRequired()])
    remarks = StringField('Remarks', validators=[Length(max=256)])
    submit = SubmitField('Save')


class StudentAttendanceEntry(FlaskForm):
    """Form for a single student's attendance in bulk form"""
    student_id = HiddenField('Student ID')
    student_name = HiddenField('Student Name')
    status = SelectField('Status', choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ], default='present')
    remarks = StringField('Remarks', validators=[Length(max=256)])


class BulkAttendanceForm(FlaskForm):
    """Form for marking attendance for multiple students at once"""
    class_id = HiddenField('Class ID', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    entries = FieldList(FormField(StudentAttendanceEntry), min_entries=0)
    submit = SubmitField('Save All')


class SportsAttendanceForm(FlaskForm):
    """Form for marking attendance for a sports class"""
    sport_id = HiddenField('Sport ID', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    entries = FieldList(FormField(StudentAttendanceEntry), min_entries=0)
    submit = SubmitField('Save All')


class AttendanceReportForm(FlaskForm):
    """Form for generating attendance reports"""
    report_type = SelectField('Report Type', choices=[
        ('student', 'Student Report'),
        ('class', 'Class Report'),
        ('standard', 'Standard Report'),
        ('sport', 'Sports Report')
    ], validators=[DataRequired()])
    student_id = SelectField('Student', coerce=int, validators=[Optional()])
    class_id = SelectField('Class', coerce=int, validators=[Optional()])
    sport_id = SelectField('Sport', coerce=int, validators=[Optional()])
    standard_id = SelectField('Standard', coerce=int, validators=[Optional()])
    section_id = SelectField('Section', coerce=int, validators=[Optional()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today().replace(day=1))
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today())
    submit = SubmitField('Generate Report')

    def __init__(self, *args, **kwargs):
        super(AttendanceReportForm, self).__init__(*args, **kwargs)
        # Populate the student choices
        self.student_id.choices = [(0, 'Select Student')] + [(s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})") 
                                                           for s in StudentProfile.query.filter_by(is_active=True).all()]
        # Populate the class choices
        self.class_id.choices = [(0, 'Select Class')] + [(c.id, f"{c.name} - {c.subject}") 
                                                      for c in Class.query.filter_by(is_active=True).all()]
        # Populate the sport choices
        self.sport_id.choices = [(0, 'Select Sport')] + [(s.id, s.name) 
                                                      for s in Sport.query.filter_by(is_active=True).all()]
        # Standard and section choices will be populated via AJAX
