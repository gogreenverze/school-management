"""
Forms for fee management.
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, FloatField, IntegerField, BooleanField,
    SelectField, HiddenField, DateField, SubmitField, FormField, FieldList
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError
from app.models.finance import (
    FeeCategory, FeeStructure, StudentFeeStructure, FeeSchedule, FeePayment,
    TransportationFee, StudentTransportation,
    FREQUENCY_MONTHLY, FREQUENCY_QUARTERLY, FREQUENCY_SEMI_ANNUALLY, FREQUENCY_ANNUALLY, FREQUENCY_ONE_TIME,
    FEE_TYPE_TUITION, FEE_TYPE_SPORTS, FEE_TYPE_TRANSPORTATION, FEE_TYPE_EXAM, FEE_TYPE_LIBRARY,
    FEE_TYPE_LABORATORY, FEE_TYPE_UNIFORM, FEE_TYPE_BOOKS, FEE_TYPE_MISCELLANEOUS,
    METHOD_CASH, METHOD_CHECK, METHOD_ONLINE, METHOD_BANK_TRANSFER, METHOD_UPI
)
from datetime import date

class FeeCategoryForm(FlaskForm):
    """Form for creating and editing fee categories"""
    name = StringField('Category Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=256)])
    is_recurring = BooleanField('Recurring Fee', default=False)
    frequency = SelectField('Frequency', choices=[
        (FREQUENCY_MONTHLY, 'Monthly'),
        (FREQUENCY_QUARTERLY, 'Quarterly'),
        (FREQUENCY_SEMI_ANNUALLY, 'Semi-Annually'),
        (FREQUENCY_ANNUALLY, 'Annually'),
        (FREQUENCY_ONE_TIME, 'One-time')
    ], validators=[Optional()])
    fee_type = SelectField('Fee Type', choices=[
        (FEE_TYPE_TUITION, 'Tuition Fee'),
        (FEE_TYPE_SPORTS, 'Sports Fee'),
        (FEE_TYPE_TRANSPORTATION, 'Transportation Fee'),
        (FEE_TYPE_EXAM, 'Examination Fee'),
        (FEE_TYPE_LIBRARY, 'Library Fee'),
        (FEE_TYPE_LABORATORY, 'Laboratory Fee'),
        (FEE_TYPE_UNIFORM, 'Uniform Fee'),
        (FEE_TYPE_BOOKS, 'Books Fee'),
        (FEE_TYPE_MISCELLANEOUS, 'Miscellaneous Fee')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

    def validate_name(self, name):
        category = FeeCategory.query.filter_by(name=name.data).first()
        if category is not None and getattr(self, 'id', None) != category.id:
            raise ValidationError('A fee category with this name already exists.')

class FeeStructureForm(FlaskForm):
    """Form for creating and editing fee structures"""
    category_id = SelectField('Fee Category', coerce=int, validators=[DataRequired()])
    standard_id = SelectField('Standard', coerce=int, validators=[Optional()])
    section_id = SelectField('Section', coerce=int, validators=[Optional()])
    name = StringField('Structure Name', validators=[DataRequired(), Length(max=64)])
    grade = StringField('Grade/Class', validators=[DataRequired(), Length(max=10)])
    amount = FloatField('Amount (₹)', validators=[DataRequired(), NumberRange(min=0)])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    frequency = SelectField('Frequency', choices=[
        (FREQUENCY_MONTHLY, 'Monthly'),
        (FREQUENCY_QUARTERLY, 'Quarterly'),
        (FREQUENCY_SEMI_ANNUALLY, 'Semi-Annually'),
        (FREQUENCY_ANNUALLY, 'Annually'),
        (FREQUENCY_ONE_TIME, 'One-time')
    ], validators=[DataRequired()])
    installments_allowed = BooleanField('Allow Installments', default=False)
    max_installments = IntegerField('Maximum Installments', validators=[Optional(), NumberRange(min=1)], default=1)
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    late_fee = FloatField('Late Fee (₹)', validators=[Optional(), NumberRange(min=0)], default=0.0)
    late_fee_frequency = SelectField('Late Fee Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('one_time', 'One-time')
    ], validators=[Optional()])
    discount_available = BooleanField('Discount Available', default=False)
    discount_percentage = FloatField('Default Discount (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=0.0)
    discount_conditions = TextAreaField('Discount Conditions', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

class StudentFeeStructureForm(FlaskForm):
    """Form for assigning fee structures to students"""
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    fee_structure_id = SelectField('Fee Structure', coerce=int, validators=[DataRequired()])
    custom_amount = FloatField('Custom Amount (₹)', validators=[Optional(), NumberRange(min=0)])
    discount_percentage = FloatField('Discount (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=0.0)
    discount_reason = StringField('Discount Reason', validators=[Optional(), Length(max=256)])
    installments = IntegerField('Installments', validators=[DataRequired(), NumberRange(min=1)], default=1)
    custom_due_date = DateField('Custom Due Date', format='%Y-%m-%d', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')

class FeePaymentForm(FlaskForm):
    """Form for recording fee payments"""
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    fee_structure_id = SelectField('Fee Structure', coerce=int, validators=[DataRequired()])
    fee_schedule_id = SelectField('Fee Schedule', coerce=int, validators=[Optional()])
    amount_paid = FloatField('Amount Paid (₹)', validators=[DataRequired(), NumberRange(min=0)])
    payment_date = DateField('Payment Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    payment_method = SelectField('Payment Method', choices=[
        (METHOD_CASH, 'Cash'),
        (METHOD_CHECK, 'Check'),
        (METHOD_ONLINE, 'Online Transfer'),
        (METHOD_BANK_TRANSFER, 'Bank Transfer'),
        (METHOD_UPI, 'UPI')
    ], validators=[DataRequired()])
    transaction_id = StringField('Transaction ID', validators=[Optional(), Length(max=64)])
    receipt_number = StringField('Receipt Number', validators=[DataRequired(), Length(max=20)])
    late_fee_paid = FloatField('Late Fee Paid (₹)', validators=[Optional(), NumberRange(min=0)], default=0.0)
    discount_applied = FloatField('Discount Applied (₹)', validators=[Optional(), NumberRange(min=0)], default=0.0)
    remarks = TextAreaField('Remarks', validators=[Optional(), Length(max=256)])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Save Payment')

class TransportationFeeForm(FlaskForm):
    """Form for creating and editing transportation fees"""
    name = StringField('Route/Zone Name', validators=[DataRequired(), Length(max=64)])
    route_description = TextAreaField('Route Description', validators=[Optional()])
    distance_km = FloatField('Distance (km)', validators=[Optional(), NumberRange(min=0)])
    amount = FloatField('Amount (₹)', validators=[DataRequired(), NumberRange(min=0)])
    frequency = SelectField('Frequency', choices=[
        (FREQUENCY_MONTHLY, 'Monthly'),
        (FREQUENCY_QUARTERLY, 'Quarterly'),
        (FREQUENCY_SEMI_ANNUALLY, 'Semi-Annually'),
        (FREQUENCY_ANNUALLY, 'Annually'),
        (FREQUENCY_ONE_TIME, 'One-time')
    ], validators=[DataRequired()])
    pickup_time = StringField('Pickup Time', validators=[Optional(), Length(max=20)])
    drop_time = StringField('Drop Time', validators=[Optional(), Length(max=20)])
    vehicle_type = StringField('Vehicle Type', validators=[Optional(), Length(max=50)])
    capacity = IntegerField('Capacity', validators=[Optional(), NumberRange(min=1)])
    late_fee = FloatField('Late Fee (₹)', validators=[Optional(), NumberRange(min=0)], default=0.0)
    late_fee_frequency = SelectField('Late Fee Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('one_time', 'One-time')
    ], validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

class StudentTransportationForm(FlaskForm):
    """Form for enrolling students in transportation"""
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    transportation_fee_id = SelectField('Transportation Route', coerce=int, validators=[DataRequired()])
    pickup_address = TextAreaField('Pickup Address', validators=[Optional()])
    drop_address = TextAreaField('Drop Address', validators=[Optional()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    custom_amount = FloatField('Custom Amount (₹)', validators=[Optional(), NumberRange(min=0)])
    discount_percentage = FloatField('Discount (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=0.0)
    discount_reason = StringField('Discount Reason', validators=[Optional(), Length(max=256)])
    is_active = BooleanField('Active', default=True)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')

class FeeReminderConfigForm(FlaskForm):
    """Form for configuring fee reminders"""
    # Upcoming payment reminders
    enable_upcoming_reminders = BooleanField('Enable Upcoming Payment Reminders', default=True)
    upcoming_days_before = IntegerField('Send Reminders Days Before Due Date', validators=[DataRequired(), NumberRange(min=1)], default=7)
    upcoming_email = BooleanField('Send Email Reminders', default=True)
    upcoming_whatsapp = BooleanField('Send WhatsApp Reminders', default=True)

    # Overdue payment reminders
    enable_overdue_reminders = BooleanField('Enable Overdue Payment Reminders', default=True)
    overdue_frequency = IntegerField('Overdue Reminder Frequency (Days)', validators=[DataRequired(), NumberRange(min=1)], default=7)
    overdue_email = BooleanField('Send Email Reminders', default=True)
    overdue_whatsapp = BooleanField('Send WhatsApp Reminders', default=True)
    max_overdue_reminders = IntegerField('Maximum Overdue Reminders', validators=[DataRequired(), NumberRange(min=1)], default=3)

    submit = SubmitField('Save Configuration')
