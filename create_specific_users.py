"""
Script to create specific teacher and student users with detailed profiles.
"""
import sqlite3
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Database path
DB_PATH = 'instance/school.db'

def create_connection():
    """Create a connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_teacher_user(conn):
    """Create a specific teacher user with detailed profile"""
    print("Creating specific teacher user...")
    cursor = conn.cursor()
    
    # Check if teacher already exists
    cursor.execute("SELECT id FROM users WHERE username = 'rajkumar'")
    existing_user = cursor.fetchone()
    
    if existing_user:
        print("Teacher 'rajkumar' already exists. Skipping.")
        return
    
    # Create user
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    password_hash = generate_password_hash('teacher123')
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('rajkumar', 'rajkumar@school.com', password_hash, 'Raj', 'Kumar', 'teacher', 1, now))
    
    teacher_user_id = cursor.lastrowid
    
    # Create teacher profile
    cursor.execute('''
        INSERT INTO teacher_profiles (user_id, employee_id, date_of_birth, date_of_joining, 
            primary_subject, secondary_subjects, qualification, experience_years, 
            phone, emergency_contact, address, specialization, bio, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        teacher_user_id, 
        'TCH001',
        '1985-06-15',
        '2010-07-01',
        'Mathematics',
        'Physics, Computer Science',
        'B.Ed., M.Sc. Mathematics',
        12,
        '+91 9876543210',
        '+91 9876543211',
        '123, Gandhi Road, Chennai, Tamil Nadu',
        'Higher Secondary',
        'Mr. Raj Kumar is an experienced mathematics teacher with expertise in teaching higher secondary students.',
        1
    ))
    
    conn.commit()
    print("Teacher user created successfully!")
    print("Username: rajkumar")
    print("Password: teacher123")

def create_student_user(conn):
    """Create a specific student user with detailed profile"""
    print("Creating specific student user...")
    cursor = conn.cursor()
    
    # Check if student already exists
    cursor.execute("SELECT id FROM users WHERE username = 'priya'")
    existing_user = cursor.fetchone()
    
    if existing_user:
        print("Student 'priya' already exists. Skipping.")
        return
    
    # Get a parent ID
    cursor.execute("SELECT id FROM parent_profiles LIMIT 1")
    parent_id = cursor.fetchone()[0]
    
    # Get a standard and section
    cursor.execute("""
        SELECT s.id, sec.id 
        FROM standards s 
        JOIN sections sec ON s.id = sec.standard_id 
        WHERE s.name = 'Standard 10' 
        LIMIT 1
    """)
    standard_section = cursor.fetchone()
    
    if not standard_section:
        print("Could not find Standard 10. Using first available standard and section.")
        cursor.execute("SELECT s.id, sec.id FROM standards s JOIN sections sec ON s.id = sec.standard_id LIMIT 1")
        standard_section = cursor.fetchone()
    
    standard_id, section_id = standard_section
    
    # Create user
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    password_hash = generate_password_hash('student123')
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('priya', 'priya@school.com', password_hash, 'Priya', 'Lakshmi', 'student', 1, now))
    
    student_user_id = cursor.lastrowid
    
    # Create student profile
    cursor.execute('''
        INSERT INTO student_profiles (user_id, roll_number, date_of_birth, standard_id, section_id,
            admission_date, parent_id, blood_group, address, emergency_contact, medical_conditions,
            previous_school, academic_year, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_user_id,
        'STU001',
        '2008-09-12',
        standard_id,
        section_id,
        '2020-06-01',
        parent_id,
        'O+',
        '456, Nehru Street, Chennai, Tamil Nadu',
        '+91 9876543212',
        'None',
        'St. Mary\'s Higher Secondary School, Chennai',
        '2023-2024',
        1
    ))
    
    # Enroll in some sports
    # Get Karate and Badminton IDs
    cursor.execute("SELECT id FROM sports WHERE name = 'Karate'")
    karate_id = cursor.fetchone()
    
    cursor.execute("SELECT id FROM sports WHERE name = 'Badminton'")
    badminton_id = cursor.fetchone()
    
    # Get student profile ID
    cursor.execute("SELECT id FROM student_profiles WHERE user_id = ?", (student_user_id,))
    student_profile_id = cursor.fetchone()[0]
    
    # Enroll in Karate if it exists
    if karate_id:
        try:
            cursor.execute('''
                INSERT INTO sport_students (sport_id, student_id)
                VALUES (?, ?)
            ''', (karate_id[0], student_profile_id))
        except sqlite3.IntegrityError:
            print(f"Student already enrolled in Karate")
    
    # Enroll in Badminton if it exists
    if badminton_id:
        try:
            cursor.execute('''
                INSERT INTO sport_students (sport_id, student_id)
                VALUES (?, ?)
            ''', (badminton_id[0], student_profile_id))
        except sqlite3.IntegrityError:
            print(f"Student already enrolled in Badminton")
    
    conn.commit()
    print("Student user created successfully!")
    print("Username: priya")
    print("Password: student123")

def main():
    """Main function to create specific users"""
    # Create a connection to the database
    conn = create_connection()
    if conn is None:
        return
    
    try:
        create_teacher_user(conn)
        create_student_user(conn)
        
        print("Specific users created successfully!")
    except sqlite3.Error as e:
        print(f"Error creating users: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
