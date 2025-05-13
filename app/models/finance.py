from datetime import datetime
from app import db

class FeeCategory(db.Model):
    __tablename__ = 'fee_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    frequency = db.Column(db.String(20), nullable=True)  # monthly, quarterly, annually, one-time
    
    # Relationships
    fee_structures = db.relationship('FeeStructure', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<FeeCategory {self.name}>'

class FeeStructure(db.Model):
    __tablename__ = 'fee_structures'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('fee_categories.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    late_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FeeStructure {self.id} - {self.grade} - {self.academic_year}>'

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
    remarks = db.Column(db.String(256), nullable=True)
    collected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    fee_structure = db.relationship('FeeStructure', backref='payments')
    collector = db.relationship('User', backref='collected_payments')
    
    def __repr__(self):
        return f'<FeePayment {self.receipt_number}>'

class FeeReminder(db.Model):
    __tablename__ = 'fee_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structures.id'), nullable=False)
    reminder_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=True)
    sent = db.Column(db.Boolean, default=False)
    sent_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    fee_structure = db.relationship('FeeStructure', backref='reminders')
    
    def __repr__(self):
        return f'<FeeReminder {self.id} - {self.reminder_date}>'
