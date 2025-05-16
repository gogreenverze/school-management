"""
Settings models for the application.
This module contains models for storing application settings.
"""
from datetime import datetime
from app import db

class WhatsAppConfig(db.Model):
    """
    Model for storing WhatsApp API configuration settings.
    This is used for the WhatsApp integration to send notifications.
    """
    __tablename__ = 'whatsapp_config'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(256), nullable=True)
    phone_number_id = db.Column(db.String(128), nullable=True)
    api_version = db.Column(db.String(20), default='v17.0')
    business_name = db.Column(db.String(128), nullable=True)
    is_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store the last test message status
    last_test_status = db.Column(db.Boolean, nullable=True)
    last_test_message = db.Column(db.Text, nullable=True)
    last_test_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<WhatsAppConfig {self.id} - {self.business_name}>'
    
    @classmethod
    def get_active_config(cls):
        """Get the active WhatsApp configuration"""
        return cls.query.filter_by(is_enabled=True).first()
