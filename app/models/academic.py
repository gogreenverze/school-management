from datetime import datetime
from app import db

class Homework(db.Model):
    __tablename__ = 'homeworks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    assigned_date = db.Column(db.Date, default=datetime.utcnow().date)
    due_date = db.Column(db.Date, nullable=False)
    max_score = db.Column(db.Integer, default=100)
    attachment = db.Column(db.String(256), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', backref='assigned_homeworks')
    submissions = db.relationship('HomeworkSubmission', backref='homework', lazy='dynamic')
    
    def __repr__(self):
        return f'<Homework {self.title}>'

class HomeworkSubmission(db.Model):
    __tablename__ = 'homework_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(20), default='submitted')  # submitted, graded, late, resubmitted
    score = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    grader = db.relationship('User', backref='graded_submissions')
    
    def __repr__(self):
        return f'<HomeworkSubmission {self.id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)  # attendance, fee, homework, announcement
    related_id = db.Column(db.Integer, nullable=True)  # ID of related entity (homework, fee, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'

class ContentBlock(db.Model):
    __tablename__ = 'content_blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    title = db.Column(db.String(128), nullable=True)
    content = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(64), nullable=False)  # home, about, contact, etc.
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='content_blocks')
    
    def __repr__(self):
        return f'<ContentBlock {self.name}>'
