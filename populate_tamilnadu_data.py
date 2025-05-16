"""
Script to populate the database with Tamil Nadu specific data.
This includes Tamil names, schools, and all education boards in India.
"""
import os
import random
import sqlite3
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash

# Database path
DB_PATH = 'instance/school.db'

# Tamil Nadu standard names
tn_standards = [
    {'name': 'LKG', 'description': 'Lower Kindergarten'},
    {'name': 'UKG', 'description': 'Upper Kindergarten'},
    {'name': 'Standard 1', 'description': 'First Standard'},
    {'name': 'Standard 2', 'description': 'Second Standard'},
    {'name': 'Standard 3', 'description': 'Third Standard'},
    {'name': 'Standard 4', 'description': 'Fourth Standard'},
    {'name': 'Standard 5', 'description': 'Fifth Standard'},
    {'name': 'Standard 6', 'description': 'Sixth Standard'},
    {'name': 'Standard 7', 'description': 'Seventh Standard'},
    {'name': 'Standard 8', 'description': 'Eighth Standard'},
    {'name': 'Standard 9', 'description': 'Ninth Standard'},
    {'name': 'Standard 10', 'description': 'Tenth Standard (SSLC)'},
    {'name': 'Standard 11', 'description': 'Eleventh Standard (Higher Secondary First Year)'},
    {'name': 'Standard 12', 'description': 'Twelfth Standard (Higher Secondary Second Year)'}
]

# Section names
section_names = ['A', 'B', 'C', 'D', 'E', 'F']

# Tamil Nadu school names
tn_school_prefixes = [
    'Sri', 'Shri', 'St.', 'Holy', 'Sacred', 'Maharishi', 'Guru', 'Saraswathi',
    'Vivekananda', 'Chinmaya', 'Bharathiar', 'Thiruvalluvar', 'Kambar',
    'Avvaiyar', 'Bharathidasan', 'Vallalar', 'Subramaniya', 'Ramakrishna'
]

tn_school_types = [
    'Matriculation Higher Secondary School',
    'Higher Secondary School',
    'Model School',
    'International School',
    'Public School',
    'Residential School',
    'CBSE School',
    'Academy',
    'Vidyalaya',
    'Convent',
    'Girls Higher Secondary School',
    'Boys Higher Secondary School',
    'Central School'
]

# Tamil Nadu specific data
tn_districts = [
    'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli',
    'Tiruppur', 'Erode', 'Vellore', 'Thoothukkudi', 'Dindigul', 'Thanjavur',
    'Ranipet', 'Sivakasi', 'Karur', 'Udhagamandalam', 'Hosur', 'Nagercoil',
    'Kanchipuram', 'Kumarapalayam', 'Karaikkudi', 'Neyveli', 'Cuddalore',
    'Kumbakonam', 'Tiruvannamalai', 'Pollachi', 'Rajapalayam', 'Gudiyatham',
    'Pudukkottai', 'Vaniyambadi', 'Ambur', 'Nagapattinam'
]

# Common Tamil surnames
tamil_surnames = [
    'Murugan', 'Rajan', 'Kumar', 'Krishnan', 'Sundaram', 'Pillai', 'Nadar',
    'Gounder', 'Naidu', 'Chettiar', 'Thevar', 'Iyer', 'Iyengar', 'Sharma',
    'Pandian', 'Subramanian', 'Venkatesh', 'Natarajan', 'Annamalai', 'Palaniswamy',
    'Shanmugam', 'Kannan', 'Chandran', 'Selvaraj', 'Venkatesan', 'Ramachandran',
    'Durairaj', 'Saravanan', 'Balasubramanian', 'Ganesan', 'Muthusamy', 'Arumugam'
]

# Common Tamil first names
tamil_male_first_names = [
    'Arun', 'Bala', 'Chandru', 'Dinesh', 'Ezhil', 'Ganesh', 'Hari', 'Inba',
    'Jagan', 'Karthik', 'Lokesh', 'Madhan', 'Naveen', 'Prabhu', 'Rajesh',
    'Senthil', 'Tamil', 'Udhay', 'Vijay', 'Yuvan', 'Anand', 'Bharath',
    'Deepak', 'Gopal', 'Harish', 'Karthikeyan', 'Manoj', 'Nandha', 'Prasad',
    'Ramesh', 'Sathish', 'Surya', 'Vignesh', 'Ashwin', 'Balaji', 'Charan'
]

tamil_female_first_names = [
    'Anitha', 'Bhavani', 'Chitra', 'Divya', 'Eswari', 'Geetha', 'Hema',
    'Indhu', 'Janani', 'Kala', 'Lakshmi', 'Meena', 'Nithya', 'Priya',
    'Radha', 'Saranya', 'Tamilselvi', 'Uma', 'Vani', 'Yamuna', 'Abinaya',
    'Brindha', 'Deepika', 'Gayathri', 'Hari Priya', 'Kalpana', 'Malathi',
    'Nirmala', 'Pavithra', 'Ramya', 'Sangeetha', 'Thenmozhi', 'Vanitha'
]

# All education boards in India
indian_boards = [
    {
        'name': 'Tamil Nadu State Board of School Examination',
        'code': 'TNSBSE',
        'description': 'The official board of education for the state of Tamil Nadu',
        'state': 'Tamil Nadu'
    },
    {
        'name': 'Central Board of Secondary Education',
        'code': 'CBSE',
        'description': 'National level board of education in India for public and private schools',
        'state': 'All India'
    },
    {
        'name': 'Indian Certificate of Secondary Education',
        'code': 'ICSE',
        'description': 'Private board of secondary education in India',
        'state': 'All India'
    },
    {
        'name': 'International Baccalaureate',
        'code': 'IB',
        'description': 'International education foundation with programs for students aged 3 to 19',
        'state': 'International'
    },
    {
        'name': 'National Institute of Open Schooling',
        'code': 'NIOS',
        'description': 'Board for distance education at school level in India',
        'state': 'All India'
    },
    {
        'name': 'Andhra Pradesh Board of Secondary Education',
        'code': 'APBSE',
        'description': 'State board of education for Andhra Pradesh',
        'state': 'Andhra Pradesh'
    },
    {
        'name': 'Assam Board of Secondary Education',
        'code': 'SEBA',
        'description': 'State board of education for Assam',
        'state': 'Assam'
    },
    {
        'name': 'Bihar School Examination Board',
        'code': 'BSEB',
        'description': 'State board of education for Bihar',
        'state': 'Bihar'
    },
    {
        'name': 'Chhattisgarh Board of Secondary Education',
        'code': 'CGBSE',
        'description': 'State board of education for Chhattisgarh',
        'state': 'Chhattisgarh'
    },
    {
        'name': 'Goa Board of Secondary & Higher Secondary Education',
        'code': 'GBSHSE',
        'description': 'State board of education for Goa',
        'state': 'Goa'
    },
    {
        'name': 'Gujarat Secondary and Higher Secondary Education Board',
        'code': 'GSEB',
        'description': 'State board of education for Gujarat',
        'state': 'Gujarat'
    },
    {
        'name': 'Haryana Board of School Education',
        'code': 'HBSE',
        'description': 'State board of education for Haryana',
        'state': 'Haryana'
    },
    {
        'name': 'Himachal Pradesh Board of School Education',
        'code': 'HPBOSE',
        'description': 'State board of education for Himachal Pradesh',
        'state': 'Himachal Pradesh'
    },
    {
        'name': 'Jammu and Kashmir State Board of School Education',
        'code': 'JKBOSE',
        'description': 'State board of education for Jammu and Kashmir',
        'state': 'Jammu and Kashmir'
    },
    {
        'name': 'Jharkhand Academic Council',
        'code': 'JAC',
        'description': 'State board of education for Jharkhand',
        'state': 'Jharkhand'
    },
    {
        'name': 'Karnataka Secondary Education Examination Board',
        'code': 'KSEEB',
        'description': 'State board of education for Karnataka',
        'state': 'Karnataka'
    },
    {
        'name': 'Kerala Board of Public Examinations',
        'code': 'KBPE',
        'description': 'State board of education for Kerala',
        'state': 'Kerala'
    },
    {
        'name': 'Maharashtra State Board of Secondary and Higher Secondary Education',
        'code': 'MSBSHSE',
        'description': 'State board of education for Maharashtra',
        'state': 'Maharashtra'
    },
    {
        'name': 'Manipur Board of Secondary Education',
        'code': 'BOSEM',
        'description': 'State board of education for Manipur',
        'state': 'Manipur'
    },
    {
        'name': 'Meghalaya Board of School Education',
        'code': 'MBOSE',
        'description': 'State board of education for Meghalaya',
        'state': 'Meghalaya'
    },
    {
        'name': 'Mizoram Board of School Education',
        'code': 'MBSE',
        'description': 'State board of education for Mizoram',
        'state': 'Mizoram'
    },
    {
        'name': 'Nagaland Board of School Education',
        'code': 'NBSE',
        'description': 'State board of education for Nagaland',
        'state': 'Nagaland'
    },
    {
        'name': 'Odisha Board of Secondary Education',
        'code': 'BSE',
        'description': 'State board of education for Odisha',
        'state': 'Odisha'
    },
    {
        'name': 'Punjab School Education Board',
        'code': 'PSEB',
        'description': 'State board of education for Punjab',
        'state': 'Punjab'
    },
    {
        'name': 'Rajasthan Board of Secondary Education',
        'code': 'RBSE',
        'description': 'State board of education for Rajasthan',
        'state': 'Rajasthan'
    },
    {
        'name': 'Sikkim State Human Resource Development Department',
        'code': 'HRDD',
        'description': 'State board of education for Sikkim',
        'state': 'Sikkim'
    },
    {
        'name': 'Telangana Board of Secondary Education',
        'code': 'TBSE',
        'description': 'State board of education for Telangana',
        'state': 'Telangana'
    },
    {
        'name': 'Tripura Board of Secondary Education',
        'code': 'TBSE',
        'description': 'State board of education for Tripura',
        'state': 'Tripura'
    },
    {
        'name': 'Uttar Pradesh Board of High School and Intermediate Education',
        'code': 'UPMSP',
        'description': 'State board of education for Uttar Pradesh',
        'state': 'Uttar Pradesh'
    },
    {
        'name': 'Uttarakhand Board of School Education',
        'code': 'UBSE',
        'description': 'State board of education for Uttarakhand',
        'state': 'Uttarakhand'
    },
    {
        'name': 'West Bengal Board of Secondary Education',
        'code': 'WBBSE',
        'description': 'State board of education for West Bengal',
        'state': 'West Bengal'
    }
]

def generate_random_date(start_year, end_year):
    """Generate a random date between start_year and end_year"""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

def create_connection():
    """Create a connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def populate_boards(conn):
    """Populate the boards table with all Indian education boards"""
    print("Populating boards table...")
    cursor = conn.cursor()

    # Check if boards already exist
    cursor.execute("SELECT COUNT(*) FROM boards")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Boards table already has {count} records. Skipping.")
        return

    # Insert boards
    for board in indian_boards:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO boards (name, code, description, state, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (board['name'], board['code'], board['description'], board['state'], 1, now, now))

    conn.commit()
    print(f"Added {len(indian_boards)} boards to the database.")

def populate_standards(conn):
    """Populate the standards table with Tamil Nadu standards"""
    print("Populating standards table...")
    cursor = conn.cursor()

    # Check if standards already exist
    cursor.execute("SELECT COUNT(*) FROM standards")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Standards table already has {count} records. Skipping.")
        return

    # Get all board IDs
    cursor.execute("SELECT id FROM boards")
    board_ids = [row[0] for row in cursor.fetchall()]

    # Insert standards for each board
    standard_count = 0
    for board_id in board_ids:
        for std in tn_standards:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO standards (name, description, board_id, academic_year, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (std['name'], std['description'], board_id, '2023-2024', 1, now, now))
            standard_count += 1

    conn.commit()
    print(f"Added {standard_count} standards to the database.")

def populate_sections(conn):
    """Populate the sections table"""
    print("Populating sections table...")
    cursor = conn.cursor()

    # Check if sections already exist
    cursor.execute("SELECT COUNT(*) FROM sections")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Sections table already has {count} records. Skipping.")
        return

    # Get all standard IDs
    cursor.execute("SELECT id FROM standards")
    standard_ids = [row[0] for row in cursor.fetchall()]

    # Insert sections for each standard
    section_count = 0
    for standard_id in standard_ids:
        num_sections = random.randint(2, 6)  # Random number of sections between 2 and 6
        for i in range(num_sections):
            if i < len(section_names):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    INSERT INTO sections (name, standard_id, description, capacity, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (section_names[i], standard_id, f"Section {section_names[i]}", random.randint(30, 45), 1, now, now))
                section_count += 1

    conn.commit()
    print(f"Added {section_count} sections to the database.")

def populate_admin_user(conn):
    """Create an admin user if one doesn't exist"""
    print("Creating admin user...")
    cursor = conn.cursor()

    # Check if admin user already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Admin user already exists. Skipping.")
        return

    # Create admin user
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    password_hash = generate_password_hash('admin123')

    cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@school.com', password_hash, 'Admin', 'User', 'admin', 1, now))

    admin_id = cursor.lastrowid

    # Create admin profile
    cursor.execute('''
        INSERT INTO admin_profiles (user_id, department, phone)
        VALUES (?, ?, ?)
    ''', (admin_id, 'Administration', '+91 9876543210'))

    conn.commit()
    print("Admin user created successfully.")
    print("Username: admin")
    print("Password: admin123")

def populate_teachers(conn, num_teachers=100):
    """Populate the teachers table with Tamil teachers"""
    print(f"Populating teachers table with {num_teachers} teachers...")
    cursor = conn.cursor()

    # Check if teachers already exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Teachers table already has {count} records. Skipping.")
        return

    # Teacher qualifications
    teacher_qualifications = [
        'B.Ed., M.A. Tamil',
        'B.Ed., M.Sc. Mathematics',
        'B.Ed., M.Sc. Physics',
        'B.Ed., M.Sc. Chemistry',
        'B.Ed., M.Sc. Biology',
        'B.Ed., M.A. English',
        'B.Ed., M.A. History',
        'B.Ed., M.A. Geography',
        'B.Ed., M.Com.',
        'B.Ed., M.C.A.',
        'B.P.Ed., M.P.Ed.',
        'B.Ed., M.A. Economics',
        'B.Ed., M.A. Political Science',
        'B.Ed., M.Sc. Computer Science',
        'B.Ed., M.A. Hindi',
        'B.Ed., M.A. Sanskrit',
        'B.Ed., M.A. French',
        'B.F.A., M.F.A.',
        'B.Mus., M.Mus.',
        'D.T.Ed., B.Ed.'
    ]

    # Subjects
    primary_subjects = ['Tamil', 'English', 'Mathematics', 'Environmental Science', 'General Knowledge']
    middle_subjects = ['Tamil', 'English', 'Mathematics', 'Science', 'Social Science', 'Hindi/Sanskrit/French']

    # Create teachers
    for i in range(num_teachers):
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first_name = random.choice(tamil_male_first_names)
            prefix = 'Mr.'
        else:
            first_name = random.choice(tamil_female_first_names)
            prefix = random.choice(['Ms.', 'Mrs.'])

        last_name = random.choice(tamil_surnames)
        username = f"teacher{i+1}"
        email = f"{username}@school.com"

        # Create user
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        password_hash = generate_password_hash('teacher123')

        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, first_name, last_name, 'teacher', 1, now))

        teacher_id = cursor.lastrowid

        # Create teacher profile
        qualification = random.choice(teacher_qualifications)
        primary_subject = qualification.split('.')[-1].strip()

        cursor.execute('''
            INSERT INTO teacher_profiles (user_id, employee_id, date_of_birth, date_of_joining,
                primary_subject, secondary_subjects, qualification, experience_years,
                phone, emergency_contact, address, specialization, bio, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            teacher_id,
            f"TCH{100+i:03d}",
            generate_random_date(1970, 1995).strftime('%Y-%m-%d'),
            generate_random_date(2000, 2022).strftime('%Y-%m-%d'),
            primary_subject,
            ', '.join(random.sample(primary_subjects + middle_subjects, 2)),
            qualification,
            random.randint(1, 25),
            f"+91 {random.randint(6000000000, 9999999999)}",
            f"+91 {random.randint(6000000000, 9999999999)}",
            f"{random.randint(1, 100)}, {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road', 'Nehru Street'])}, {random.choice(tn_districts)}",
            random.choice(['Primary', 'Middle School', 'High School', 'Higher Secondary']),
            f"{prefix} {first_name} {last_name} is an experienced educator with expertise in {primary_subject}.",
            1
        ))

    conn.commit()
    print(f"Added {num_teachers} teachers to the database.")
    print("Default teacher login: username: teacher1, password: teacher123")

def populate_students(conn, num_students=200):
    """Populate the students table with Tamil students"""
    print(f"Populating students table with {num_students} students...")
    cursor = conn.cursor()

    # Check if students already exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Students table already has {count} records. Skipping.")
        return

    # Get all sections
    cursor.execute("SELECT id, standard_id FROM sections")
    sections = cursor.fetchall()

    # Blood groups
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    # Create students
    for i in range(num_students):
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first_name = random.choice(tamil_male_first_names)
        else:
            first_name = random.choice(tamil_female_first_names)

        last_name = random.choice(tamil_surnames)
        username = f"student{i+1}"
        email = f"{username}@school.com"

        # Create user
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        password_hash = generate_password_hash('student123')

        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, first_name, last_name, 'student', 1, now))

        student_id = cursor.lastrowid

        # Assign to a random section
        section_id, standard_id = random.choice(sections)

        # Create student profile
        cursor.execute('''
            INSERT INTO student_profiles (user_id, roll_number, date_of_birth, standard_id, section_id,
                admission_date, blood_group, address, emergency_contact, medical_conditions,
                previous_school, academic_year, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id,
            f"STU{1000+i:04d}",
            generate_random_date(2005, 2015).strftime('%Y-%m-%d'),
            standard_id,
            section_id,
            generate_random_date(2018, 2023).strftime('%Y-%m-%d'),
            random.choice(blood_groups),
            f"{random.randint(1, 100)}, {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road', 'Nehru Street'])}, {random.choice(tn_districts)}",
            f"+91 {random.randint(6000000000, 9999999999)}",
            random.choice([None, 'Asthma', 'Allergies', 'Diabetes', 'None']),
            f"{random.choice(tn_school_prefixes)} {random.choice(tn_school_types)}, {random.choice(tn_districts)}",
            '2023-2024',
            1
        ))

    conn.commit()
    print(f"Added {num_students} students to the database.")
    print("Default student login: username: student1, password: student123")

def main():
    """Main function to populate the database"""
    # Create a connection to the database
    conn = create_connection()
    if conn is None:
        return

    try:
        # Populate the database tables
        populate_boards(conn)
        populate_standards(conn)
        populate_sections(conn)
        populate_admin_user(conn)
        populate_teachers(conn, 100)  # Generate 100 teachers
        populate_students(conn, 200)  # Generate 200 students

        print("Database populated successfully!")
    except sqlite3.Error as e:
        print(f"Error populating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
