#!/usr/bin/env python
"""
Setup script for the School Management System.
This script helps with initial setup of the application.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def create_env_file():
    """Create a .env file with necessary environment variables."""
    if os.path.exists('.env'):
        print("A .env file already exists. Skipping creation.")
        return
    
    print("Creating .env file...")
    secret_key = secrets.token_hex(16)
    
    env_content = f"""SECRET_KEY={secret_key}
DATABASE_URL=sqlite:///instance/school.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Created .env file. Please update it with your email settings.")

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    if os.path.exists('venv'):
        print("Virtual environment already exists. Skipping creation.")
        return
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    print("Virtual environment created.")

def install_dependencies():
    """Install dependencies from requirements.txt."""
    print("Installing dependencies...")
    
    # Determine the pip path based on the operating system
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Unix/Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'])
    print("Dependencies installed.")

def create_instance_directory():
    """Create the instance directory if it doesn't exist."""
    instance_dir = Path('instance')
    if not instance_dir.exists():
        print("Creating instance directory...")
        instance_dir.mkdir()
        print("Instance directory created.")
    else:
        print("Instance directory already exists. Skipping creation.")

def initialize_database():
    """Initialize the database."""
    print("Initializing database...")
    
    # Determine the python path based on the operating system
    if os.name == 'nt':  # Windows
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:  # Unix/Linux/Mac
        python_path = os.path.join('venv', 'bin', 'python')
    
    subprocess.run([python_path, 'create_db.py'])
    print("Database initialized.")

def main():
    """Main function to run all setup steps."""
    print("Setting up School Management System...")
    
    create_virtual_environment()
    create_env_file()
    create_instance_directory()
    install_dependencies()
    initialize_database()
    
    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    if os.name == 'nt':  # Windows
        print("1. Activate the virtual environment: venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("1. Activate the virtual environment: source venv/bin/activate")
    print("2. Run the application: python run.py")
    print("3. Access the application at: http://127.0.0.1:5007")
    print("\nDefault login credentials:")
    print("Admin - Username: admin, Password: admin123")
    print("Teacher - Username: teacher1, Password: teacher123")
    print("Student - Username: student1, Password: student123")

if __name__ == "__main__":
    main()
