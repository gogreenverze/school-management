from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, FloatField, BooleanField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, NumberRange
from app.models.attendance import Sport
from app.models.finance import SportFee
from app.models.user import TeacherProfile

class SportForm(FlaskForm):
    """Form for creating and editing sports"""
    name = StringField('Sport Name', validators=[DataRequired(), Length(max=64)])
    category = SelectField('Category', choices=[
        ('team_sport', 'Team Sport'),
        ('individual_sport', 'Individual Sport'),
        ('martial_arts', 'Martial Arts'),
        ('swimming', 'Swimming'),
        ('athletics', 'Athletics'),
        ('yoga', 'Yoga'),
        ('dance', 'Dance'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    instructor_id = SelectField('Instructor', coerce=int, validators=[DataRequired()])
    schedule = StringField('Schedule', validators=[Length(max=128)], 
                          description="e.g., Mon,Wed,Fri 4:00-5:00 PM")
    location = StringField('Location', validators=[Length(max=128)])
    description = TextAreaField('Description')
    image = StringField('Image URL', validators=[Length(max=256)], 
                       description="URL to an image representing this sport")
    icon = StringField('Icon Class', validators=[Length(max=64)], 
                      description="Font Awesome icon class (e.g., fas fa-futbol)")
    capacity = IntegerField('Maximum Capacity', default=30, 
                           validators=[NumberRange(min=1, max=200)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(SportForm, self).__init__(*args, **kwargs)
        # Populate the instructor choices
        self.instructor_id.choices = [(t.id, f"{t.user.first_name} {t.user.last_name}") 
                                    for t in TeacherProfile.query.filter_by(is_active=True).all()]

    def validate_name(self, name):
        sport = Sport.query.filter_by(name=name.data).first()
        if sport is not None and getattr(self, 'id', None) != sport.id:
            raise ValidationError('A sport with this name already exists.')

class SportFeeForm(FlaskForm):
    """Form for creating and editing sport fees"""
    sport_id = HiddenField('Sport ID', validators=[DataRequired()])
    name = StringField('Fee Name', validators=[DataRequired(), Length(max=64)],
                      description="e.g., Basic, Advanced, Competition")
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)],
                       description="Fee amount in INR")
    frequency = SelectField('Frequency', choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annually', 'Semi-Annually'),
        ('annually', 'Annually'),
        ('one_time', 'One-time')
    ], validators=[DataRequired()])
    duration = IntegerField('Duration', validators=[Optional(), NumberRange(min=1)],
                           description="Number of months/sessions (leave blank for ongoing)")
    description = TextAreaField('Description', validators=[Optional()],
                               description="Additional details about this fee structure")
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_name(self, name):
        fee = SportFee.query.filter_by(sport_id=self.sport_id.data, name=name.data).first()
        if fee is not None and getattr(self, 'id', None) != fee.id:
            raise ValidationError('A fee with this name already exists for this sport.')

class SportStudentForm(FlaskForm):
    """Form for enrolling students in a sport"""
    sport_id = HiddenField('Sport ID', validators=[DataRequired()])
    student_ids = SelectField('Students', coerce=int, validators=[DataRequired()],
                             render_kw={"multiple": True})
    submit = SubmitField('Enroll Students')
