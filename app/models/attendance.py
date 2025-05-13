from datetime import datetime
from app import db

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, excused
    remarks = db.Column(db.String(256), nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recorder = db.relationship('User', backref='recorded_attendances')
    
    def __repr__(self):
        return f'<Attendance {self.id} - {self.date}>'

class SportsAttendance(db.Model):
    __tablename__ = 'sports_attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, excused
    remarks = db.Column(db.String(256), nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sport = db.relationship('Sport', backref='attendances')
    recorder = db.relationship('User', backref='recorded_sports_attendances')
    
    def __repr__(self):
        return f'<SportsAttendance {self.id} - {self.date}>'

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(10), nullable=True)
    subject = db.Column(db.String(64), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_profiles.id'), nullable=False)
    schedule = db.Column(db.String(128), nullable=True)  # e.g., "Mon,Wed,Fri 10:00-11:00"
    room = db.Column(db.String(20), nullable=True)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='class', lazy='dynamic')
    homeworks = db.relationship('Homework', backref='class', lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.name} - {self.grade}{self.section}>'

class Sport(db.Model):
    __tablename__ = 'sports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False)  # e.g., team sport, martial arts, etc.
    instructor_id = db.Column(db.Integer, db.ForeignKey('teacher_profiles.id'), nullable=False)
    schedule = db.Column(db.String(128), nullable=True)
    location = db.Column(db.String(128), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    instructor = db.relationship('TeacherProfile', backref='sports_instructed')
    
    def __repr__(self):
        return f'<Sport {self.name}>'
