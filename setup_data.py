"""
Script to set up the database and generate sample data for the School Management System.
"""
import os
import sys
import subprocess
from app import create_app

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    try:
        # Create a Flask app context
        app = create_app()
        with app.app_context():
            # Run Flask-Migrate commands
            subprocess.run(["flask", "db", "migrate", "-m", "Add Board model and update Standard model"], check=True)
            subprocess.run(["flask", "db", "upgrade"], check=True)
        print("Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return False

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
    # Run migrations first
    if run_migrations():
        # If migrations are successful, generate sample data
        generate_sample_data()
    else:
        print("Setup failed. Please check the error messages above.")
        sys.exit(1)
