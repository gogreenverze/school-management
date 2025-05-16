"""
Forms for application settings.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional, URL

class WhatsAppConfigForm(FlaskForm):
    """Form for WhatsApp API configuration"""
    api_key = StringField('WhatsApp API Key (Access Token)', validators=[DataRequired(), Length(max=256)],
                         description="Your WhatsApp Business API access token from Meta Developer Dashboard")
    
    phone_number_id = StringField('Phone Number ID', validators=[DataRequired(), Length(max=128)],
                                 description="Your WhatsApp Business Phone Number ID from Meta Developer Dashboard")
    
    api_version = StringField('API Version', validators=[DataRequired(), Length(max=20)],
                             default='v17.0',
                             description="WhatsApp API version (default: v17.0)")
    
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=128)],
                               description="Your school or business name that will appear in WhatsApp messages")
    
    is_enabled = BooleanField('Enable WhatsApp Integration', default=True,
                             description="Turn WhatsApp integration on or off")
    
    test_phone = StringField('Test Phone Number', validators=[Optional(), Length(max=20)],
                            description="Phone number to send test message (with country code, e.g., 919876543210)")
    
    submit = SubmitField('Save Configuration')
    test_button = SubmitField('Test Configuration')
