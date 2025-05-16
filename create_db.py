"""
Script to create the database schema directly using SQL and generate sample data.
"""
import os
import sys
import sqlite3
from app import create_app

def create_database_schema():
    """Create the database schema directly using SQL"""
    print("Creating database schema...")
    
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
    
    # Create a new database and tables
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
        -- Create boards table
        CREATE TABLE boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(128) NOT NULL UNIQUE,
            code VARCHAR(20) NOT NULL UNIQUE,
            description TEXT,
            state VARCHAR(64),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            updated_at DATETIME
        );
        
        -- Create standards table
        CREATE TABLE standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            description TEXT,
            board_id INTEGER,
            academic_year VARCHAR(10) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (board_id) REFERENCES boards(id),
            UNIQUE (name, board_id)
        );
        
        -- Create sections table
        CREATE TABLE sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(10) NOT NULL,
            standard_id INTEGER NOT NULL,
            description VARCHAR(256),
            capacity INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (standard_id) REFERENCES standards(id),
            UNIQUE (name, standard_id)
        );
        
        -- Create users table
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(64) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(128),
            first_name VARCHAR(64) NOT NULL,
            last_name VARCHAR(64) NOT NULL,
            role VARCHAR(20) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            last_login DATETIME
        );
        
        -- Create admin_profiles table
        CREATE TABLE admin_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            department VARCHAR(64),
            phone VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Create teacher_profiles table
        CREATE TABLE teacher_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            employee_id VARCHAR(20) UNIQUE NOT NULL,
            date_of_birth DATE,
            date_of_joining DATE NOT NULL,
            primary_subject VARCHAR(64),
            secondary_subjects VARCHAR(128),
            qualification VARCHAR(128),
            experience_years INTEGER DEFAULT 0,
            phone VARCHAR(20),
            emergency_contact VARCHAR(20),
            address TEXT,
            specialization VARCHAR(128),
            bio TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Create parent_profiles table
        CREATE TABLE parent_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone VARCHAR(20),
            alternate_phone VARCHAR(20),
            occupation VARCHAR(64),
            annual_income INTEGER,
            address TEXT,
            relation_to_student VARCHAR(20),
            emergency_contact VARCHAR(20),
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Create student_profiles table
        CREATE TABLE student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            roll_number VARCHAR(20) UNIQUE NOT NULL,
            date_of_birth DATE NOT NULL,
            standard_id INTEGER NOT NULL,
            section_id INTEGER,
            admission_date DATE NOT NULL,
            parent_id INTEGER,
            blood_group VARCHAR(5),
            address TEXT,
            emergency_contact VARCHAR(20),
            medical_conditions TEXT,
            previous_school VARCHAR(128),
            academic_year VARCHAR(10) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (standard_id) REFERENCES standards(id),
            FOREIGN KEY (section_id) REFERENCES sections(id),
            FOREIGN KEY (parent_id) REFERENCES parent_profiles(id)
        );
        
        -- Create classes table
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            standard_id INTEGER NOT NULL,
            section_id INTEGER,
            subject VARCHAR(64) NOT NULL,
            teacher_id INTEGER NOT NULL,
            schedule VARCHAR(128),
            room VARCHAR(20),
            academic_year VARCHAR(10) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (standard_id) REFERENCES standards(id),
            FOREIGN KEY (section_id) REFERENCES sections(id),
            FOREIGN KEY (teacher_id) REFERENCES teacher_profiles(id)
        );
        
        -- Create sports table
        CREATE TABLE sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            category VARCHAR(64) NOT NULL,
            instructor_id INTEGER NOT NULL,
            schedule VARCHAR(128),
            location VARCHAR(128),
            description TEXT,
            FOREIGN KEY (instructor_id) REFERENCES teacher_profiles(id)
        );
        ''')
        
        conn.commit()
        conn.close()
        
        print("Database schema created successfully")
        return True
    except Exception as e:
        print(f"Error creating database schema: {e}")
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
    # Create the database schema first
    if create_database_schema():
        # If schema creation is successful, generate sample data
        generate_sample_data()
    else:
        print("Setup failed. Please check the error messages above.")
        sys.exit(1)
