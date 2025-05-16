from datetime import datetime
from app import db

class Board(db.Model):
    """
    Model for education boards (e.g., Tamil Nadu State Board, CBSE, etc.)
    """
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    standards = db.relationship('Standard', backref='board', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Board {self.name}>'

class Standard(db.Model):
    """
    Model for school standards/grades (e.g., Grade 1, Grade 2, etc.)
    """
    __tablename__ = 'standards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=True)
    academic_year = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sections = db.relationship('Section', backref='standard', lazy='dynamic', cascade='all, delete-orphan')

    # Define a unique constraint for standard name within a board
    __table_args__ = (db.UniqueConstraint('name', 'board_id', name='_standard_board_uc'),)

    def __repr__(self):
        return f'<Standard {self.name}>'

class Section(db.Model):
    """
    Model for sections within a standard (e.g., Section A, Section B, etc.)
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    standard_id = db.Column(db.Integer, db.ForeignKey('standards.id'), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    capacity = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define a unique constraint for section name within a standard
    __table_args__ = (db.UniqueConstraint('name', 'standard_id', name='_section_standard_uc'),)

    def __repr__(self):
        return f'<Section {self.name} - {self.standard.name if self.standard else "No Standard"}>'
