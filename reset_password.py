"""
Script to reset passwords for users in the School Management System.
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Create a minimal Flask app without loading all blueprints
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/arkprabha/Desktop/School/instance/school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a minimal User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

def reset_password(username, new_password):
    """Reset password for a specific user"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"Password for user '{username}' has been reset successfully!")
            return True
        else:
            print(f"User '{username}' not found.")
            return False

def reset_all_passwords(new_password):
    """Reset passwords for all users"""
    with app.app_context():
        users = User.query.all()

        for user in users:
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        print(f"Passwords for all {len(users)} users have been reset to '{new_password}'!")
        return True

if __name__ == "__main__":
    # Reset password for admin
    reset_password('admin', 'admin123')

    # Reset password for a specific teacher
    reset_password('eswari.kannan.teacher308356', 'teacher123')

    # Reset password for a specific student
    reset_password('bharath.ramachandran111923', 'student123')

    # Uncomment to reset all passwords
    # reset_all_passwords('password123')
