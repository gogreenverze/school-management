"""
Script to reset the database and create it from scratch.
"""
import os
import sys
from app import create_app, db

def reset_database():
    """Reset the database and create it from scratch"""
    print("Resetting database...")

    # Get the database file path
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    # Remove the database file if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database file: {db_path}")
        except Exception as e:
            print(f"Error removing database file: {e}")
            return False

    # Create a new database with all tables
    with app.app_context():
        # Make sure all models are imported
        from app.models.user import User, AdminProfile, TeacherProfile, ParentProfile, StudentProfile
        from app.models.academic_structure import Board, Standard, Section
        from app.models.attendance import Class, Sport, Attendance, SportsAttendance
        from app.models.academic import Homework, HomeworkSubmission, Notification, ContentBlock
        from app.models.finance import FeeCategory, FeeStructure, FeePayment, FeeReminder

        # Create all tables
        db.create_all()
        print("Created new database with all tables")

    return True

def generate_sample_data():
    """Generate sample data for the application"""
    print("Generating sample data...")
    try:
        # Import and run the data generation script
        from app.utils.generate_data import generate_data
        generate_data()
        print("Sample data generation completed successfully!")
        return True
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return False

if __name__ == "__main__":
    # Reset the database first
    if reset_database():
        # If database reset is successful, generate sample data
        generate_sample_data()
    else:
        print("Setup failed. Please check the error messages above.")
        sys.exit(1)
