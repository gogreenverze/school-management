from datetime import datetime, timedelta, date
import uuid
from app import db

# Fee Category Types
FEE_TYPE_TUITION = 'tuition'
FEE_TYPE_SPORTS = 'sports'
FEE_TYPE_TRANSPORTATION = 'transportation'
FEE_TYPE_EXAM = 'exam'
FEE_TYPE_LIBRARY = 'library'
FEE_TYPE_LABORATORY = 'laboratory'
FEE_TYPE_UNIFORM = 'uniform'
FEE_TYPE_BOOKS = 'books'
FEE_TYPE_MISCELLANEOUS = 'miscellaneous'

# Fee Frequencies
FREQUENCY_MONTHLY = 'monthly'
FREQUENCY_QUARTERLY = 'quarterly'
FREQUENCY_SEMI_ANNUALLY = 'semi_annually'
FREQUENCY_ANNUALLY = 'annually'
FREQUENCY_ONE_TIME = 'one_time'

# Payment Status
STATUS_PENDING = 'pending'
STATUS_COMPLETED = 'completed'
STATUS_PARTIAL = 'partial'
STATUS_OVERDUE = 'overdue'
STATUS_FAILED = 'failed'
STATUS_REFUNDED = 'refunded'

# Invoice Status
INVOICE_STATUS_DRAFT = 'draft'
INVOICE_STATUS_SENT = 'sent'
INVOICE_STATUS_PAID = 'paid'
INVOICE_STATUS_PARTIALLY_PAID = 'partially_paid'
INVOICE_STATUS_OVERDUE = 'overdue'
INVOICE_STATUS_CANCELLED = 'cancelled'

# Invoice Types
INVOICE_TYPE_TUITION = 'tuition'
INVOICE_TYPE_SPORTS = 'sports'
INVOICE_TYPE_TRANSPORTATION = 'transportation'
INVOICE_TYPE_COMBINED = 'combined'

# Payment Methods
METHOD_CASH = 'cash'
METHOD_CHECK = 'check'
METHOD_ONLINE = 'online'
METHOD_BANK_TRANSFER = 'bank_transfer'
METHOD_UPI = 'upi'

class FeeCategory(db.Model):
    __tablename__ = 'fee_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    frequency = db.Column(db.String(20), nullable=True)  # monthly, quarterly, annually, one-time
    fee_type = db.Column(db.String(20), nullable=False, default=FEE_TYPE_TUITION)  # tuition, sports, transportation, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fee_structures = db.relationship('FeeStructure', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<FeeCategory {self.name}>'

class FeeStructure(db.Model):
    __tablename__ = 'fee_structures'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('fee_categories.id'), nullable=False)
    standard_id = db.Column(db.Integer, db.ForeignKey('standards.id'), nullable=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True)
    name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    frequency = db.Column(db.String(20), nullable=False, default=FREQUENCY_ANNUALLY)
    installments_allowed = db.Column(db.Boolean, default=False)
    max_installments = db.Column(db.Integer, default=1)
    due_date = db.Column(db.Date, nullable=True)
    late_fee = db.Column(db.Float, default=0.0)
    late_fee_frequency = db.Column(db.String(20), nullable=True)  # daily, weekly, monthly
    discount_available = db.Column(db.Boolean, default=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_conditions = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    standard = db.relationship('Standard', backref='fee_structures')
    section = db.relationship('Section', backref='fee_structures')

    def __repr__(self):
        return f'<FeeStructure {self.id} - {self.name} - {self.grade} - {self.academic_year}>'

    def calculate_late_fee(self, payment_date):
        """Calculate late fee based on days overdue"""
        if not self.due_date or not self.late_fee or payment_date <= self.due_date:
            return 0.0

        days_late = (payment_date - self.due_date).days

        if self.late_fee_frequency == 'daily':
            return self.late_fee * days_late
        elif self.late_fee_frequency == 'weekly':
            weeks_late = days_late // 7 + (1 if days_late % 7 > 0 else 0)
            return self.late_fee * weeks_late
        elif self.late_fee_frequency == 'monthly':
            months_late = days_late // 30 + (1 if days_late % 30 > 0 else 0)
            return self.late_fee * months_late
        else:
            return self.late_fee  # One-time late fee

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structures.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, check, online
    transaction_id = db.Column(db.String(64), nullable=True)
    receipt_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending, completed, failed, refunded
    late_fee_paid = db.Column(db.Float, default=0.0)
    discount_applied = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.String(256), nullable=True)
    collected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fee_structure = db.relationship('FeeStructure', backref='payments')
    collector = db.relationship('User', backref='collected_payments')

    def __repr__(self):
        return f'<FeePayment {self.receipt_number}>'

    @property
    def total_amount(self):
        """Get the total amount including late fees"""
        return self.amount_paid + self.late_fee_paid

class FeeReminder(db.Model):
    __tablename__ = 'fee_reminders'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structures.id'), nullable=True)
    fee_schedule_id = db.Column(db.Integer, db.ForeignKey('fee_schedules.id'), nullable=True)
    reminder_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=True)
    sent = db.Column(db.Boolean, default=False)
    sent_date = db.Column(db.DateTime, nullable=True)
    notification_type = db.Column(db.String(20), default='email')  # email, whatsapp, sms
    reminder_type = db.Column(db.String(20), default='upcoming')  # upcoming, due, overdue
    response_received = db.Column(db.Boolean, default=False)
    response_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    fee_structure = db.relationship('FeeStructure', backref='reminders')
    fee_schedule = db.relationship('FeeSchedule', backref='reminders')

    def __repr__(self):
        return f'<FeeReminder {self.id} - {self.reminder_date} - {self.notification_type}>'

class SportFee(db.Model):
    __tablename__ = 'sport_fees'

    id = db.Column(db.Integer, primary_key=True)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)  # e.g., "Basic", "Advanced", "Competition"
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # monthly, quarterly, annually, one-time
    duration = db.Column(db.Integer, nullable=True)  # Number of months/sessions
    description = db.Column(db.Text, nullable=True)
    late_fee = db.Column(db.Float, default=0.0)
    late_fee_frequency = db.Column(db.String(20), nullable=True)  # daily, weekly, monthly
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SportFee {self.name} - {self.sport_id}>'

    def calculate_late_fee(self, payment_date, due_date):
        """Calculate late fee based on days overdue"""
        if not due_date or not self.late_fee or payment_date <= due_date:
            return 0.0

        days_late = (payment_date - due_date).days

        if self.late_fee_frequency == 'daily':
            return self.late_fee * days_late
        elif self.late_fee_frequency == 'weekly':
            weeks_late = days_late // 7 + (1 if days_late % 7 > 0 else 0)
            return self.late_fee * weeks_late
        elif self.late_fee_frequency == 'monthly':
            months_late = days_late // 30 + (1 if days_late % 30 > 0 else 0)
            return self.late_fee * months_late
        else:
            return self.late_fee  # One-time late fee

class StudentFeeStructure(db.Model):
    """Student-specific fee structure that can override the standard fee structure"""
    __tablename__ = 'student_fee_structures'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structures.id'), nullable=False)
    custom_amount = db.Column(db.Float, nullable=True)  # If null, use the base fee structure amount
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_reason = db.Column(db.String(256), nullable=True)
    installments = db.Column(db.Integer, default=1)
    custom_due_date = db.Column(db.Date, nullable=True)  # If null, use the base fee structure due date
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('StudentProfile', foreign_keys=[student_id], backref='student_fee_assignments')
    base_structure = db.relationship('FeeStructure', foreign_keys=[fee_structure_id], backref='student_fee_structures')

    def __repr__(self):
        return f'<StudentFeeStructure {self.id} - Student: {self.student_id}>'

    @property
    def effective_amount(self):
        """Get the effective amount after applying any custom amount or discount"""
        base_amount = self.custom_amount if self.custom_amount is not None else self.base_structure.amount
        if self.discount_percentage > 0:
            return base_amount * (1 - (self.discount_percentage / 100))
        return base_amount

    @property
    def effective_due_date(self):
        """Get the effective due date, either custom or from base structure"""
        return self.custom_due_date if self.custom_due_date else self.base_structure.due_date

class FeeSchedule(db.Model):
    """Schedule for recurring fee payments"""
    __tablename__ = 'fee_schedules'

    id = db.Column(db.Integer, primary_key=True)
    student_fee_structure_id = db.Column(db.Integer, db.ForeignKey('student_fee_structures.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    payment_id = db.Column(db.Integer, db.ForeignKey('fee_payments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_fee_structure = db.relationship('StudentFeeStructure', foreign_keys=[student_fee_structure_id], backref='fee_schedules')
    payment = db.relationship('FeePayment', foreign_keys=[payment_id], backref='fee_schedule', uselist=False)

    def __repr__(self):
        return f'<FeeSchedule {self.id} - Installment: {self.installment_number} - Due: {self.due_date}>'

    @property
    def is_overdue(self):
        """Check if this fee schedule is overdue"""
        return self.status == STATUS_PENDING and self.due_date < date.today()

    @property
    def days_overdue(self):
        """Get the number of days this fee is overdue"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

class SportFeeSchedule(db.Model):
    """Schedule for sport fee payments"""
    __tablename__ = 'sport_fee_schedules'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    sport_fee_id = db.Column(db.Integer, db.ForeignKey('sport_fees.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    payment_id = db.Column(db.Integer, db.ForeignKey('sport_fee_payments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('StudentProfile', foreign_keys=[student_id], backref='sport_fee_schedules')
    sport = db.relationship('Sport', foreign_keys=[sport_id], backref='sport_fee_schedules')
    sport_fee = db.relationship('SportFee', foreign_keys=[sport_fee_id], backref='sport_schedules')

    def __repr__(self):
        return f'<SportFeeSchedule {self.id} - Sport: {self.sport_id} - Due: {self.due_date}>'

    @property
    def is_overdue(self):
        """Check if this fee schedule is overdue"""
        return self.status == STATUS_PENDING and self.due_date < date.today()

    @property
    def days_overdue(self):
        """Get the number of days this fee is overdue"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

class SportFeePayment(db.Model):
    __tablename__ = 'sport_fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    sport_fee_id = db.Column(db.Integer, db.ForeignKey('sport_fees.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, check, online
    transaction_id = db.Column(db.String(64), nullable=True)
    receipt_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending, completed, failed, refunded
    late_fee_paid = db.Column(db.Float, default=0.0)
    discount_applied = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.String(256), nullable=True)
    collected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    academic_year = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sport = db.relationship('Sport', foreign_keys=[sport_id], backref='sport_payments')
    sport_fee = db.relationship('SportFee', foreign_keys=[sport_fee_id], backref='sport_fee_payments')
    student = db.relationship('StudentProfile', foreign_keys=[student_id], backref='student_sport_payments')
    collector = db.relationship('User', foreign_keys=[collected_by], backref='collected_sport_payments')

    def __repr__(self):
        return f'<SportFeePayment {self.receipt_number}>'

    @property
    def total_amount(self):
        """Get the total amount including late fees"""
        return self.amount_paid + self.late_fee_paid

class TransportationFee(db.Model):
    """Transportation/Van fee structure"""
    __tablename__ = 'transportation_fees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # e.g., "Zone A", "Zone B", etc.
    route_description = db.Column(db.Text, nullable=True)
    distance_km = db.Column(db.Float, nullable=True)  # Distance in kilometers
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False, default=FREQUENCY_MONTHLY)
    pickup_time = db.Column(db.String(20), nullable=True)  # Format: "HH:MM AM/PM"
    drop_time = db.Column(db.String(20), nullable=True)  # Format: "HH:MM AM/PM"
    vehicle_type = db.Column(db.String(50), nullable=True)  # e.g., "School Bus", "Van", etc.
    capacity = db.Column(db.Integer, nullable=True)
    late_fee = db.Column(db.Float, default=0.0)
    late_fee_frequency = db.Column(db.String(20), nullable=True)  # daily, weekly, monthly
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TransportationFee {self.name} - ₹{self.amount}>'

    def calculate_late_fee(self, payment_date, due_date):
        """Calculate late fee based on days overdue"""
        if not due_date or not self.late_fee or payment_date <= due_date:
            return 0.0

        days_late = (payment_date - due_date).days

        if self.late_fee_frequency == 'daily':
            return self.late_fee * days_late
        elif self.late_fee_frequency == 'weekly':
            weeks_late = days_late // 7 + (1 if days_late % 7 > 0 else 0)
            return self.late_fee * weeks_late
        elif self.late_fee_frequency == 'monthly':
            months_late = days_late // 30 + (1 if days_late % 30 > 0 else 0)
            return self.late_fee * months_late
        else:
            return self.late_fee  # One-time late fee

class StudentTransportation(db.Model):
    """Student transportation enrollment"""
    __tablename__ = 'student_transportation'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    transportation_fee_id = db.Column(db.Integer, db.ForeignKey('transportation_fees.id'), nullable=False)
    pickup_address = db.Column(db.Text, nullable=True)
    drop_address = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)  # If null, ongoing
    custom_amount = db.Column(db.Float, nullable=True)  # If null, use the base fee amount
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_reason = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('StudentProfile', foreign_keys=[student_id], backref='student_transportation')
    transportation_fee = db.relationship('TransportationFee', foreign_keys=[transportation_fee_id], backref='student_enrollments')

    def __repr__(self):
        return f'<StudentTransportation {self.id} - Student: {self.student_id}>'

    @property
    def effective_amount(self):
        """Get the effective amount after applying any custom amount or discount"""
        base_amount = self.custom_amount if self.custom_amount is not None else self.transportation_fee.amount
        if self.discount_percentage > 0:
            return base_amount * (1 - (self.discount_percentage / 100))
        return base_amount

class TransportationFeeSchedule(db.Model):
    """Schedule for transportation fee payments"""
    __tablename__ = 'transportation_fee_schedules'

    id = db.Column(db.Integer, primary_key=True)
    student_transportation_id = db.Column(db.Integer, db.ForeignKey('student_transportation.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    payment_id = db.Column(db.Integer, db.ForeignKey('transportation_fee_payments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_transportation = db.relationship('StudentTransportation', foreign_keys=[student_transportation_id], backref='transportation_schedules')
    payment = db.relationship('TransportationFeePayment', foreign_keys=[payment_id], backref='transportation_schedule', uselist=False)

    def __repr__(self):
        return f'<TransportationFeeSchedule {self.id} - Installment: {self.installment_number} - Due: {self.due_date}>'

    @property
    def is_overdue(self):
        """Check if this fee schedule is overdue"""
        return self.status == STATUS_PENDING and self.due_date < date.today()

    @property
    def days_overdue(self):
        """Get the number of days this fee is overdue"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

class TransportationFeePayment(db.Model):
    """Transportation fee payment records"""
    __tablename__ = 'transportation_fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    transportation_fee_id = db.Column(db.Integer, db.ForeignKey('transportation_fees.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, check, online
    transaction_id = db.Column(db.String(64), nullable=True)
    receipt_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # pending, completed, failed, refunded
    late_fee_paid = db.Column(db.Float, default=0.0)
    discount_applied = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.String(256), nullable=True)
    collected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    academic_year = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('StudentProfile', foreign_keys=[student_id], backref='transportation_payments')
    transportation_fee = db.relationship('TransportationFee', foreign_keys=[transportation_fee_id], backref='transportation_payments')
    collector = db.relationship('User', foreign_keys=[collected_by], backref='collected_transportation_payments')

    def __repr__(self):
        return f'<TransportationFeePayment {self.receipt_number}>'

    @property
    def total_amount(self):
        """Get the total amount including late fees"""
        return self.amount_paid + self.late_fee_paid

class Invoice(db.Model):
    """Invoice model for all types of fees"""
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    invoice_type = db.Column(db.String(20), nullable=False)  # tuition, sports, transportation, combined
    invoice_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=INVOICE_STATUS_DRAFT)
    subtotal = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    late_fee = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    terms = db.Column(db.Text, nullable=True)
    pdf_path = db.Column(db.String(256), nullable=True)  # Path to stored PDF file
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('StudentProfile', backref='invoices')
    creator = db.relationship('User', backref='created_invoices')

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

    @property
    def is_paid(self):
        """Check if invoice is fully paid"""
        return self.status == INVOICE_STATUS_PAID

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.status in [INVOICE_STATUS_SENT, INVOICE_STATUS_PARTIALLY_PAID] and self.due_date < date.today()

    @property
    def days_overdue(self):
        """Get the number of days this invoice is overdue"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    @staticmethod
    def generate_invoice_number():
        """Generate a unique invoice number"""
        prefix = "INV"
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = str(uuid.uuid4().int)[:6]
        return f"{prefix}-{date_part}-{random_part}"

class InvoiceItem(db.Model):
    """Individual line items for invoices"""
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)
    fee_type = db.Column(db.String(20), nullable=False)  # tuition, sports, transportation, etc.
    fee_schedule_id = db.Column(db.Integer, nullable=True)  # Can be from different schedule tables
    fee_schedule_type = db.Column(db.String(20), nullable=True)  # fee_schedules, sport_fee_schedules, transportation_fee_schedules
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=True)  # For sports fees
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    invoice = db.relationship('Invoice', backref='items')
    sport = db.relationship('Sport', backref='invoice_items')

    def __repr__(self):
        return f'<InvoiceItem {self.id} - {self.description}>'

class InvoicePayment(db.Model):
    """Payments made against invoices"""
    __tablename__ = 'invoice_payments'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    payment_id = db.Column(db.Integer, nullable=False)  # ID from the respective payment table
    payment_type = db.Column(db.String(20), nullable=False)  # fee_payments, sport_fee_payments, transportation_fee_payments
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    invoice = db.relationship('Invoice', backref='payments')

    def __repr__(self):
        return f'<InvoicePayment {self.id} - Invoice: {self.invoice_id} - Amount: {self.amount}>'