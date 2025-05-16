from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from app.models.academic_structure import Board, Standard, Section
from app.models.academic import Homework, HomeworkSubmission
from app.models.attendance import Class

class BoardForm(FlaskForm):
    """Form for creating and editing education boards"""
    name = StringField('Board Name', validators=[DataRequired(), Length(max=128)])
    code = StringField('Board Code', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description')
    state = StringField('State', validators=[Length(max=64)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_name(self, name):
        board = Board.query.filter_by(name=name.data).first()
        if board is not None and getattr(self, 'id', None) != board.id:
            raise ValidationError('A board with this name already exists.')

    def validate_code(self, code):
        board = Board.query.filter_by(code=code.data).first()
        if board is not None and getattr(self, 'id', None) != board.id:
            raise ValidationError('A board with this code already exists.')

class StandardForm(FlaskForm):
    """Form for creating and editing standards/grades"""
    name = StringField('Standard/Grade Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description')
    board_id = SelectField('Education Board', coerce=int, validators=[Optional()])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(StandardForm, self).__init__(*args, **kwargs)
        # Populate the board choices
        from app.models.academic_structure import Board
        self.board_id.choices = [(0, 'Select Board')] + [(b.id, b.name) for b in Board.query.filter_by(is_active=True).order_by(Board.name).all()]

    def validate_name(self, name):
        # Check if a standard with the same name exists for the same board
        board_id = self.board_id.data if self.board_id.data and self.board_id.data != 0 else None
        standard = Standard.query.filter_by(name=name.data, board_id=board_id).first()
        if standard is not None and getattr(self, 'id', None) != standard.id:
            raise ValidationError('A standard with this name already exists for this board.')

class SectionForm(FlaskForm):
    """Form for creating and editing sections"""
    name = StringField('Section Name', validators=[DataRequired(), Length(max=10)])
    standard_id = SelectField('Standard/Grade', coerce=int, validators=[DataRequired()])
    description = StringField('Description', validators=[Length(max=256)])
    capacity = IntegerField('Capacity', default=30)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_name(self, name):
        section = Section.query.filter_by(name=name.data, standard_id=self.standard_id.data).first()
        if section is not None and getattr(self, 'id', None) != section.id:
            raise ValidationError('A section with this name already exists for this standard.')


class HomeworkForm(FlaskForm):
    """Form for creating and editing homework assignments"""
    title = StringField('Homework Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description/Instructions', validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    max_score = IntegerField('Maximum Score', default=100)
    attachment = FileField('Attachment (PDF, DOC, DOCX, PPT, PPTX)',
                          validators=[Optional(),
                                     FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx'],
                                                'Only PDF, DOC, DOCX, PPT, PPTX files are allowed!')])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(HomeworkForm, self).__init__(*args, **kwargs)
        # Populate the class choices
        self.class_id.choices = [(c.id, f"{c.name} - {c.subject}") for c in Class.query.filter_by(is_active=True).all()]


class HomeworkSubmissionForm(FlaskForm):
    """Form for students to submit homework"""
    content = TextAreaField('Your Answer', validators=[Optional()])
    attachment = FileField('Attachment (PDF, DOC, DOCX, PPT, PPTX, JPG, PNG)',
                          validators=[Optional(),
                                     FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'],
                                                'Only PDF, DOC, DOCX, PPT, PPTX, JPG, PNG files are allowed!')])
    submit = SubmitField('Submit Homework')


class HomeworkGradingForm(FlaskForm):
    """Form for teachers to grade homework submissions"""
    score = IntegerField('Score', validators=[DataRequired()])
    feedback = TextAreaField('Feedback', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('graded', 'Graded'),
        ('resubmit', 'Request Resubmission'),
        ('late', 'Marked as Late')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Grade')
