from datetime import datetime
from app import db
from app.models.academic_structure import Standard, Section

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
    standard_id = db.Column(db.Integer, db.ForeignKey('standards.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True)
    subject = db.Column(db.String(64), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_profiles.id'), nullable=False)
    schedule = db.Column(db.String(128), nullable=True)  # e.g., "Mon,Wed,Fri 10:00-11:00"
    room = db.Column(db.String(20), nullable=True)
    academic_year = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    standard = db.relationship('Standard', backref='classes')
    section = db.relationship('Section', backref='classes')
    attendances = db.relationship('Attendance', backref='class', lazy='dynamic')
    homeworks = db.relationship('Homework', backref='class', lazy='dynamic')

    # For backward compatibility
    @property
    def grade(self):
        if self.standard:
            return self.standard.name
        return ""

    def __repr__(self):
        section_name = self.section.name if self.section else ""
        return f'<Class {self.name} - {self.standard.name if self.standard else ""}{section_name}>'

# Association table for students and sports
sport_students = db.Table('sport_students',
    db.Column('sport_id', db.Integer, db.ForeignKey('sports.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student_profiles.id'), primary_key=True)
)

class Sport(db.Model):
    __tablename__ = 'sports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False)  # e.g., team sport, martial arts, etc.
    instructor_id = db.Column(db.Integer, db.ForeignKey('teacher_profiles.id'), nullable=False)
    schedule = db.Column(db.String(128), nullable=True)
    location = db.Column(db.String(128), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(256), nullable=True)  # URL to sport image
    icon = db.Column(db.String(64), nullable=True)  # Font Awesome icon class
    capacity = db.Column(db.Integer, default=30)  # Maximum number of students
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor = db.relationship('TeacherProfile', backref='sports_instructed')
    students = db.relationship('StudentProfile', secondary=sport_students,
                              backref=db.backref('sports', lazy='dynamic'))
    fees = db.relationship('SportFee', backref='sport', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sport {self.name}>'
