"""
Forms for invoice management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FloatField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from datetime import date

class InvoiceForm(FlaskForm):
    """Form for creating and editing invoices"""
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    invoice_type = SelectField('Invoice Type', choices=[
        ('tuition', 'Tuition Fee'),
        ('sports', 'Sports Fee'),
        ('transportation', 'Transportation Fee'),
        ('combined', 'Combined')
    ], validators=[DataRequired()])
    invoice_date = DateField('Invoice Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    subtotal = FloatField('Subtotal', validators=[DataRequired(), NumberRange(min=0)])
    discount = FloatField('Discount', validators=[Optional(), NumberRange(min=0)], default=0.0)
    tax = FloatField('Tax', validators=[Optional(), NumberRange(min=0)], default=0.0)
    late_fee = FloatField('Late Fee', validators=[Optional(), NumberRange(min=0)], default=0.0)
    total_amount = FloatField('Total Amount', validators=[DataRequired(), NumberRange(min=0)])
    amount_paid = FloatField('Amount Paid', validators=[Optional(), NumberRange(min=0)], default=0.0)
    balance = FloatField('Balance', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    terms = TextAreaField('Terms and Conditions', validators=[Optional(), Length(max=1000)])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Save Invoice')

class InvoiceItemForm(FlaskForm):
    """Form for adding items to an invoice"""
    invoice_id = HiddenField('Invoice ID')
    description = StringField('Description', validators=[DataRequired(), Length(max=256)])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    discount = FloatField('Discount', validators=[Optional(), NumberRange(min=0)], default=0.0)
    total = FloatField('Total', validators=[DataRequired(), NumberRange(min=0)])
    fee_type = SelectField('Fee Type', choices=[
        ('tuition', 'Tuition Fee'),
        ('sports', 'Sports Fee'),
        ('transportation', 'Transportation Fee'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    sport_id = SelectField('Sport', coerce=int, validators=[Optional()])
    fee_schedule_id = HiddenField('Fee Schedule ID')
    fee_schedule_type = HiddenField('Fee Schedule Type')
    submit = SubmitField('Add Item')

class InvoiceFilterForm(FlaskForm):
    """Form for filtering invoices"""
    student_id = SelectField('Student', coerce=int, validators=[Optional()])
    invoice_type = SelectField('Invoice Type', choices=[
        ('', 'All Types'),
        ('tuition', 'Tuition Fee'),
        ('sports', 'Sports Fee'),
        ('transportation', 'Transportation Fee'),
        ('combined', 'Combined')
    ], validators=[Optional()])
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], validators=[Optional()])
    date_from = DateField('From Date', format='%Y-%m-%d', validators=[Optional()])
    date_to = DateField('To Date', format='%Y-%m-%d', validators=[Optional()])
    academic_year = StringField('Academic Year', validators=[Optional(), Length(max=10)])
    submit = SubmitField('Filter')

class InvoiceStatusForm(FlaskForm):
    """Form for updating invoice status"""
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Status')

class InvoicePaymentForm(FlaskForm):
    """Form for recording payments against an invoice"""
    invoice_id = HiddenField('Invoice ID')
    payment_id = SelectField('Payment', coerce=int, validators=[DataRequired()])
    payment_type = SelectField('Payment Type', choices=[
        ('fee_payments', 'Tuition Fee Payment'),
        ('sport_fee_payments', 'Sports Fee Payment'),
        ('transportation_fee_payments', 'Transportation Fee Payment')
    ], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Record Payment')

class GenerateInvoicesForm(FlaskForm):
    """Form for batch generating invoices"""
    invoice_type = SelectField('Invoice Type', choices=[
        ('tuition', 'Tuition Fee'),
        ('sports', 'Sports Fee'),
        ('transportation', 'Transportation Fee'),
        ('combined', 'Combined')
    ], validators=[DataRequired()])
    standard_id = SelectField('Standard', coerce=int, validators=[Optional()])
    section_id = SelectField('Section', coerce=int, validators=[Optional()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=10)])
    include_late_fees = SelectField('Include Late Fees', choices=[
        ('no', 'No'),
        ('yes', 'Yes')
    ], default='no', validators=[DataRequired()])
    submit = SubmitField('Generate Invoices')
