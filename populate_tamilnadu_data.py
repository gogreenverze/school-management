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

# Tamil Nadu specific education boards
indian_boards = [
    {
        'name': 'Tamil Nadu State Board of School Examination',
        'code': 'TNSBSE',
        'description': 'The official board of education for the state of Tamil Nadu',
        'state': 'Tamil Nadu'
    },
    {
        'name': 'Samacheer Kalvi',
        'code': 'SAMACHEER',
        'description': 'Uniform System of Education in Tamil Nadu',
        'state': 'Tamil Nadu'
    },
    {
        'name': 'Tamil Nadu Matriculation Board',
        'code': 'TNMATRIC',
        'description': 'Matriculation schools in Tamil Nadu',
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
    }
]

# Sports data with focus on Karate and Kabaddi
sports_data = [
    {
        'name': 'Karate',
        'category': 'Martial Arts',
        'description': 'Traditional Japanese martial art focusing on striking techniques',
        'fee': 1500,
        'schedule': 'Mon,Wed,Fri 4:00 PM - 5:30 PM',
        'location': 'School Martial Arts Hall',
        'instructor': 'Sensei',
        'levels': ['White Belt', 'Yellow Belt', 'Orange Belt', 'Green Belt', 'Blue Belt', 'Brown Belt', 'Black Belt'],
        'age_groups': ['5-8 years', '9-12 years', '13-16 years', '17+ years']
    },
    {
        'name': 'Kabaddi',
        'category': 'Team Sport',
        'description': 'Traditional Indian contact team sport',
        'fee': 1000,
        'schedule': 'Tue,Thu,Sat 4:00 PM - 5:30 PM',
        'location': 'School Playground',
        'instructor': 'Coach',
        'teams': ['Junior Team', 'Senior Team', 'Girls Team', 'Boys Team'],
        'positions': ['Raider', 'Defender', 'All-Rounder']
    },
    {
        'name': 'Cricket',
        'category': 'Team Sport',
        'description': 'Popular bat-and-ball game played between two teams',
        'fee': 1200,
        'schedule': 'Mon,Wed,Sat 3:30 PM - 5:30 PM',
        'location': 'School Cricket Ground',
        'instructor': 'Coach'
    },
    {
        'name': 'Volleyball',
        'category': 'Team Sport',
        'description': 'Team sport in which two teams of six players are separated by a net',
        'fee': 800,
        'schedule': 'Tue,Thu 3:30 PM - 5:00 PM',
        'location': 'School Volleyball Court',
        'instructor': 'Coach'
    },
    {
        'name': 'Silambam',
        'category': 'Martial Arts',
        'description': 'Traditional Tamil martial art which focuses on the bamboo staff as the main weapon',
        'fee': 1300,
        'schedule': 'Mon,Wed,Fri 3:00 PM - 4:30 PM',
        'location': 'School Martial Arts Hall',
        'instructor': 'Master'
    },
    {
        'name': 'Yoga',
        'category': 'Fitness',
        'description': 'Group of physical, mental, and spiritual practices or disciplines',
        'fee': 900,
        'schedule': 'Tue,Thu,Sat 7:00 AM - 8:00 AM',
        'location': 'School Yoga Hall',
        'instructor': 'Guru'
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
    cursor.execute("SELECT code FROM boards")
    existing_codes = [row[0] for row in cursor.fetchall()]

    if existing_codes:
        print(f"Boards table already has {len(existing_codes)} records.")
        print("Adding only new boards...")

    # Insert boards
    added_count = 0
    for board in indian_boards:
        if board['code'] not in existing_codes:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                cursor.execute('''
                    INSERT INTO boards (name, code, description, state, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (board['name'], board['code'], board['description'], board['state'], 1, now, now))
                added_count += 1
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate board: {board['name']} ({board['code']})")

    conn.commit()
    print(f"Added {added_count} new boards to the database.")

def populate_standards(conn):
    """Populate the standards table with Tamil Nadu standards"""
    print("Populating standards table...")
    cursor = conn.cursor()

    # Get all board IDs
    cursor.execute("SELECT id FROM boards")
    board_ids = [row[0] for row in cursor.fetchall()]

    # Check existing standards
    cursor.execute("SELECT name, board_id FROM standards")
    existing_standards = [(row[0], row[1]) for row in cursor.fetchall()]

    if existing_standards:
        print(f"Standards table already has {len(existing_standards)} records.")
        print("Adding only new standards...")

    # Insert standards for each board
    standard_count = 0
    for board_id in board_ids:
        for std in tn_standards:
            # Check if this standard already exists for this board
            if (std['name'], board_id) not in existing_standards:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    cursor.execute('''
                        INSERT INTO standards (name, description, board_id, academic_year, is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (std['name'], std['description'], board_id, '2023-2024', 1, now, now))
                    standard_count += 1
                except sqlite3.IntegrityError:
                    print(f"Skipping duplicate standard: {std['name']} for board ID {board_id}")

    conn.commit()
    print(f"Added {standard_count} new standards to the database.")

def populate_sections(conn):
    """Populate the sections table"""
    print("Populating sections table...")
    cursor = conn.cursor()

    # Get all standard IDs
    cursor.execute("SELECT id FROM standards")
    standard_ids = [row[0] for row in cursor.fetchall()]

    # Check existing sections
    cursor.execute("SELECT name, standard_id FROM sections")
    existing_sections = [(row[0], row[1]) for row in cursor.fetchall()]

    if existing_sections:
        print(f"Sections table already has {len(existing_sections)} records.")
        print("Adding only new sections...")

    # Insert sections for each standard
    section_count = 0
    for standard_id in standard_ids:
        num_sections = random.randint(2, 6)  # Random number of sections between 2 and 6
        for i in range(num_sections):
            if i < len(section_names):
                # Check if this section already exists for this standard
                if (section_names[i], standard_id) not in existing_sections:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    try:
                        cursor.execute('''
                            INSERT INTO sections (name, standard_id, description, capacity, is_active, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (section_names[i], standard_id, f"Section {section_names[i]}", random.randint(30, 45), 1, now, now))
                        section_count += 1
                    except sqlite3.IntegrityError:
                        print(f"Skipping duplicate section: {section_names[i]} for standard ID {standard_id}")

    conn.commit()
    print(f"Added {section_count} new sections to the database.")

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

def populate_sports(conn):
    """Populate the sports table with sports data, focusing on Karate and Kabaddi"""
    print("Populating sports table...")
    cursor = conn.cursor()

    # Check if sports already exist
    cursor.execute("SELECT name FROM sports")
    existing_sports = [row[0] for row in cursor.fetchall()]

    if existing_sports:
        print(f"Sports table already has {len(existing_sports)} records.")
        print("Adding only new sports...")

    # Get teacher IDs for instructors
    cursor.execute("SELECT id FROM teacher_profiles LIMIT 10")
    teacher_ids = [row[0] for row in cursor.fetchall()]

    if not teacher_ids:
        print("No teachers found. Please populate teachers first.")
        return

    # Insert sports
    added_count = 0
    for sport in sports_data:
        if sport['name'] not in existing_sports:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            instructor_id = random.choice(teacher_ids)

            try:
                cursor.execute('''
                    INSERT INTO sports (name, category, instructor_id, schedule, location, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    sport['name'],
                    sport['category'],
                    instructor_id,
                    sport['schedule'],
                    sport['location'],
                    sport['description']
                ))
                added_count += 1

                # Get the sport ID
                sport_id = cursor.lastrowid

                # Add sport fee
                cursor.execute('''
                    INSERT INTO sport_fees (sport_id, fee_amount, fee_description, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    sport_id,
                    sport['fee'],
                    f"Monthly fee for {sport['name']}",
                    1,
                    now,
                    now
                ))

            except sqlite3.IntegrityError:
                print(f"Skipping duplicate sport: {sport['name']}")

    conn.commit()
    print(f"Added {added_count} new sports to the database.")

def populate_parents(conn, num_parents=150):
    """Populate the parents table with Tamil parents"""
    print(f"Populating parents table with {num_parents} parents...")
    cursor = conn.cursor()

    # Check if parents already exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'parent'")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Parents table already has {count} records. Skipping.")
        return

    # Tamil occupations
    occupations = [
        'Teacher', 'Engineer', 'Doctor', 'Lawyer', 'Business Owner',
        'Government Employee', 'Farmer', 'Shopkeeper', 'Driver', 'Technician',
        'Accountant', 'Banker', 'Police Officer', 'Military Personnel', 'Nurse',
        'Software Developer', 'Professor', 'Electrician', 'Plumber', 'Carpenter',
        'Chef', 'Tailor', 'Fisherman', 'Temple Priest', 'Textile Worker'
    ]

    # Create parents
    for i in range(num_parents):
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first_name = random.choice(tamil_male_first_names)
            relation = 'Father'
        else:
            first_name = random.choice(tamil_female_first_names)
            relation = 'Mother'

        last_name = random.choice(tamil_surnames)
        username = f"parent{i+1}"
        email = f"{username}@gmail.com"

        # Create user
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        password_hash = generate_password_hash('parent123')

        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, first_name, last_name, 'parent', 1, now))

        parent_id = cursor.lastrowid

        # Create parent profile
        cursor.execute('''
            INSERT INTO parent_profiles (user_id, phone, alternate_phone, occupation, annual_income,
                address, relation_to_student, emergency_contact, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            parent_id,
            f"+91 {random.randint(6000000000, 9999999999)}",
            f"+91 {random.randint(6000000000, 9999999999)}",
            random.choice(occupations),
            random.randint(200000, 2000000),
            f"{random.randint(1, 100)}, {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road', 'Nehru Street'])}, {random.choice(tn_districts)}",
            relation,
            f"+91 {random.randint(6000000000, 9999999999)}",
            1
        ))

    conn.commit()
    print(f"Added {num_parents} parents to the database.")
    print("Default parent login: username: parent1, password: parent123")

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

    # Get all parent IDs
    cursor.execute("SELECT id FROM parent_profiles")
    parent_ids = [row[0] for row in cursor.fetchall()]

    if not parent_ids:
        print("No parents found. Please populate parents first.")
        return

    # Get all sports
    cursor.execute("SELECT id, name FROM sports")
    sports = cursor.fetchall()

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

        # Assign to a random parent
        parent_id = random.choice(parent_ids)

        # Create student profile
        cursor.execute('''
            INSERT INTO student_profiles (user_id, roll_number, date_of_birth, standard_id, section_id,
                admission_date, parent_id, blood_group, address, emergency_contact, medical_conditions,
                previous_school, academic_year, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id,
            f"STU{1000+i:04d}",
            generate_random_date(2005, 2015).strftime('%Y-%m-%d'),
            standard_id,
            section_id,
            generate_random_date(2018, 2023).strftime('%Y-%m-%d'),
            parent_id,
            random.choice(blood_groups),
            f"{random.randint(1, 100)}, {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road', 'Nehru Street'])}, {random.choice(tn_districts)}",
            f"+91 {random.randint(6000000000, 9999999999)}",
            random.choice([None, 'Asthma', 'Allergies', 'Diabetes', 'None']),
            f"{random.choice(tn_school_prefixes)} {random.choice(tn_school_types)}, {random.choice(tn_districts)}",
            '2023-2024',
            1
        ))

        # Enroll some students in sports (about 40% chance)
        if random.random() < 0.4 and sports:
            # Choose 1-2 sports for the student
            num_sports = random.randint(1, min(2, len(sports)))
            chosen_sports = random.sample(sports, num_sports)

            for sport_id, sport_name in chosen_sports:
                try:
                    # Add student to sport
                    cursor.execute('''
                        INSERT INTO sport_students (sport_id, student_id, join_date, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        sport_id,
                        student_id,
                        generate_random_date(2023, 2024).strftime('%Y-%m-%d'),
                        'Active',
                        now,
                        now
                    ))

                    # Get sport fee
                    cursor.execute("SELECT id, fee_amount FROM sport_fees WHERE sport_id = ?", (sport_id,))
                    fee_data = cursor.fetchone()

                    if fee_data:
                        fee_id, fee_amount = fee_data

                        # Create fee schedule for the student
                        for month in range(1, 13):  # 12 months
                            due_date = date(2024, month, 10).strftime('%Y-%m-%d')
                            cursor.execute('''
                                INSERT INTO sport_fee_schedules (sport_fee_id, student_id, due_date, amount, status, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                fee_id,
                                student_id,
                                due_date,
                                fee_amount,
                                'Pending' if month > 5 else 'Paid',  # First 5 months paid
                                now,
                                now
                            ))

                            # Add payment for paid months
                            if month <= 5:
                                payment_date = date(2024, month, random.randint(1, 10)).strftime('%Y-%m-%d')
                                cursor.execute('''
                                    INSERT INTO sport_fee_payments (student_id, sport_fee_id, amount, payment_date, payment_method, created_at, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    student_id,
                                    fee_id,
                                    fee_amount,
                                    payment_date,
                                    random.choice(['Cash', 'Online Transfer', 'Cheque']),
                                    now,
                                    now
                                ))

                except sqlite3.IntegrityError:
                    print(f"Error enrolling student {student_id} in sport {sport_id}")

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
        # Populate the database tables in the correct order
        print("\n=== Step 1: Populating boards ===")
        populate_boards(conn)

        print("\n=== Step 2: Populating standards ===")
        populate_standards(conn)

        print("\n=== Step 3: Populating sections ===")
        populate_sections(conn)

        print("\n=== Step 4: Creating admin user ===")
        populate_admin_user(conn)

        print("\n=== Step 5: Populating teachers ===")
        populate_teachers(conn, 100)  # Generate 100 teachers

        print("\n=== Step 6: Populating sports ===")
        populate_sports(conn)  # Add sports with focus on Karate and Kabaddi

        print("\n=== Step 7: Populating parents ===")
        populate_parents(conn, 150)  # Generate 150 parents

        print("\n=== Step 8: Populating students ===")
        populate_students(conn, 200)  # Generate 200 students

        print("\n=== Database population completed successfully! ===")
        print("\nLogin credentials:")
        print("Admin: username: admin, password: admin123")
        print("Teacher: username: teacher1, password: teacher123")
        print("Parent: username: parent1, password: parent123")
        print("Student: username: student1, password: student123")
    except sqlite3.Error as e:
        print(f"Error populating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
