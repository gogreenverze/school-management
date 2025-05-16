from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.academic import ContentBlock

class ContentBlockForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    title = StringField('Title', validators=[Length(max=128)])
    content = TextAreaField('Content', validators=[DataRequired()])
    location = SelectField('Location', choices=[
        ('home', 'Home Page'),
        ('about', 'About Page'),
        ('contact', 'Contact Page'),
        ('footer', 'Footer'),
        ('sidebar', 'Sidebar')
    ], validators=[DataRequired()])
    order = IntegerField('Display Order', default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_name(self, name):
        content_block = ContentBlock.query.filter_by(name=name.data).first()
        if content_block is not None and self.id.data and content_block.id != int(self.id.data):
            raise ValidationError('A content block with this name already exists.')
