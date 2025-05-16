"""
Script to insert sample data directly using SQL.
"""
import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash

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

# Tamil Nadu board and standards
tn_boards = [
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
        'name': 'Tamil Nadu Anglo-Indian School Leaving Certificate',
        'code': 'TNAISLC',
        'description': 'Board for Anglo-Indian schools in Tamil Nadu',
        'state': 'Tamil Nadu'
    },
    {
        'name': 'Tamil Nadu Oriental School Leaving Certificate',
        'code': 'TNOSLC',
        'description': 'Board for Oriental schools in Tamil Nadu',
        'state': 'Tamil Nadu'
    }
]

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

# Subjects for different standards
primary_subjects = ['Tamil', 'English', 'Mathematics', 'Environmental Science', 'General Knowledge']
middle_subjects = ['Tamil', 'English', 'Mathematics', 'Science', 'Social Science', 'Hindi/Sanskrit/French']
high_subjects = ['Tamil', 'English', 'Mathematics', 'Science', 'Social Science', 'Hindi/Sanskrit/French', 'Computer Science']

# Sports offered in Tamil Nadu schools
sports_list = [
    {'name': 'Cricket', 'category': 'Team Sport'},
    {'name': 'Football', 'category': 'Team Sport'},
    {'name': 'Volleyball', 'category': 'Team Sport'},
    {'name': 'Basketball', 'category': 'Team Sport'},
    {'name': 'Kabaddi', 'category': 'Team Sport'},
    {'name': 'Kho Kho', 'category': 'Team Sport'},
    {'name': 'Badminton', 'category': 'Racquet Sport'},
    {'name': 'Table Tennis', 'category': 'Racquet Sport'},
    {'name': 'Tennis', 'category': 'Racquet Sport'},
    {'name': 'Athletics', 'category': 'Track and Field'},
    {'name': 'Swimming', 'category': 'Aquatics'},
    {'name': 'Karate', 'category': 'Martial Arts'},
    {'name': 'Silambam', 'category': 'Martial Arts'},
    {'name': 'Chess', 'category': 'Board Game'},
    {'name': 'Carrom', 'category': 'Board Game'},
    {'name': 'Yoga', 'category': 'Fitness'}
]

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

# Blood groups
blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

def generate_random_date(start_year, end_year):
    """Generate a random date between start_year and end_year"""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

def insert_sample_data():
    """Insert sample data directly using SQL"""
    print("Inserting sample data...")

    try:
        # Connect to the database
        conn = sqlite3.connect('instance/school.db')
        cursor = conn.cursor()

        # Clear existing data
        print("Clearing existing data...")
        cursor.executescript('''
        DELETE FROM sports;
        DELETE FROM classes;
        DELETE FROM student_profiles;
        DELETE FROM parent_profiles;
        DELETE FROM teacher_profiles;
        DELETE FROM admin_profiles;
        DELETE FROM users;
        DELETE FROM sections;
        DELETE FROM standards;
        DELETE FROM boards;
        ''')
        conn.commit()
        print("Existing data cleared")

        # Insert admin user
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@school.com', generate_password_hash('admin123'), 'Admin', 'User', 'admin', 1, now))

        admin_id = cursor.lastrowid

        # Insert admin profile
        cursor.execute('''
        INSERT INTO admin_profiles (user_id, department, phone)
        VALUES (?, ?, ?)
        ''', (admin_id, 'Administration', '123-456-7890'))

        # Insert boards
        board_ids = []
        for board in tn_boards:
            cursor.execute('''
            INSERT INTO boards (name, code, description, state, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (board['name'], board['code'], board['description'], board['state'], 1, now, now))
            board_ids.append(cursor.lastrowid)

        print(f"Created {len(board_ids)} boards")

        # Insert standards
        standard_ids = []
        for board_id in board_ids:
            for std in tn_standards:
                cursor.execute('''
                INSERT INTO standards (name, description, board_id, academic_year, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (std['name'], std['description'], board_id, '2023-2024', 1, now, now))
                standard_ids.append(cursor.lastrowid)

        print(f"Created {len(standard_ids)} standards")

        # Insert sections
        section_ids = []
        for std_id in standard_ids:
            num_sections = random.randint(2, 6)
            for i in range(num_sections):
                cursor.execute('''
                INSERT INTO sections (name, standard_id, description, capacity, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (section_names[i], std_id, f"Section {section_names[i]}", random.randint(30, 45), 1, now, now))
                section_ids.append(cursor.lastrowid)

        print(f"Created {len(section_ids)} sections")

        # Insert teachers
        teacher_ids = []
        teacher_profile_ids = []

        for i in range(100):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = random.choice(tamil_male_first_names)
            else:
                first_name = random.choice(tamil_female_first_names)

            last_name = random.choice(tamil_surnames)
            username = f"{first_name.lower()}.{last_name.lower()}.teacher{random.randint(1, 999999)}"
            email = f"{username}@schoolmail.com"

            # Insert user
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, generate_password_hash('password123'), first_name, last_name, 'teacher', 1, now))

            teacher_id = cursor.lastrowid
            teacher_ids.append(teacher_id)

            # Insert teacher profile
            qualification = random.choice(teacher_qualifications)
            primary_subject = qualification.split('.')[-1].strip()

            cursor.execute('''
            INSERT INTO teacher_profiles (user_id, employee_id, date_of_birth, date_of_joining, primary_subject,
                                         secondary_subjects, qualification, experience_years, phone,
                                         emergency_contact, address, specialization, bio, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                teacher_id,
                f"TCH{100+i:03d}",
                generate_random_date(1970, 1995),
                generate_random_date(2000, 2022),
                primary_subject,
                ', '.join(random.sample(primary_subjects + middle_subjects, 2)),
                qualification,
                random.randint(1, 25),
                f"+91 {random.randint(6000000000, 9999999999)}",
                f"+91 {random.randint(6000000000, 9999999999)}",
                f"{random.randint(1, 100)} {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road'])}, {random.choice(tn_districts)}",
                random.choice(['Primary', 'Middle School', 'High School', 'Higher Secondary']),
                f"{first_name} {last_name} is an experienced educator with expertise in {primary_subject}.",
                1
            ))

            teacher_profile_id = cursor.lastrowid
            teacher_profile_ids.append(teacher_profile_id)

        print(f"Created {len(teacher_ids)} teachers")

        # Insert parents
        parent_ids = []
        parent_profile_ids = []

        for i in range(150):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = random.choice(tamil_male_first_names)
            else:
                first_name = random.choice(tamil_female_first_names)

            last_name = random.choice(tamil_surnames)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999999)}"
            email = f"{username}@gmail.com"

            # Insert user
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, generate_password_hash('password123'), first_name, last_name, 'parent', 1, now))

            parent_id = cursor.lastrowid
            parent_ids.append(parent_id)

            # Insert parent profile
            occupation = random.choice([
                'Teacher', 'Engineer', 'Doctor', 'Lawyer', 'Business Owner',
                'Government Employee', 'Farmer', 'Shopkeeper', 'Driver', 'Technician',
                'Accountant', 'Banker', 'Police Officer', 'Military Personnel', 'Nurse'
            ])

            cursor.execute('''
            INSERT INTO parent_profiles (user_id, phone, occupation, address)
            VALUES (?, ?, ?, ?)
            ''', (
                parent_id,
                f"+91 {random.randint(6000000000, 9999999999)}",
                occupation,
                f"{random.randint(1, 100)} {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road'])}, {random.choice(tn_districts)}"
            ))

            parent_profile_id = cursor.lastrowid
            parent_profile_ids.append(parent_profile_id)

        print(f"Created {len(parent_ids)} parents")

        # Insert students
        student_ids = []
        student_profile_ids = []

        for i in range(200):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = random.choice(tamil_male_first_names)
            else:
                first_name = random.choice(tamil_female_first_names)

            last_name = random.choice(tamil_surnames)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999999)}"
            email = f"{username}@schoolmail.com"

            # Insert user
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, generate_password_hash('password123'), first_name, last_name, 'student', 1, now))

            student_id = cursor.lastrowid
            student_ids.append(student_id)

            # Assign to a random section
            random_section_id = random.choice(section_ids)

            # Get the standard_id for this section
            cursor.execute('SELECT standard_id FROM sections WHERE id = ?', (random_section_id,))
            random_standard_id = cursor.fetchone()[0]

            # Assign to a random parent
            random_parent_profile_id = random.choice(parent_profile_ids)

            # Insert student profile
            cursor.execute('''
            INSERT INTO student_profiles (user_id, roll_number, date_of_birth, standard_id, section_id,
                                         admission_date, parent_id, blood_group, address, emergency_contact,
                                         medical_conditions, previous_school, academic_year, is_active,
                                         created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_id,
                f"STU{1000+i:04d}",
                generate_random_date(2005, 2015),
                random_standard_id,
                random_section_id,
                generate_random_date(2018, 2023),
                random_parent_profile_id,
                random.choice(blood_groups),
                f"{random.randint(1, 100)} {random.choice(['Main Road', 'Cross Street', 'Temple Street', 'Gandhi Road'])}, {random.choice(tn_districts)}",
                f"+91 {random.randint(6000000000, 9999999999)}",
                random.choice([None, 'Asthma', 'Allergies', 'Diabetes', 'None']),
                f"{random.choice(['St.', 'Holy', 'Government', 'Public', 'Modern'])} {random.choice(['School', 'Higher Secondary School', 'Matriculation School'])}, {random.choice(tn_districts)}",
                '2023-2024',
                1,
                now,
                now
            ))

            student_profile_id = cursor.lastrowid
            student_profile_ids.append(student_profile_id)

        print(f"Created {len(student_ids)} students")

        # Insert classes
        class_ids = []

        # For each standard, create classes for different subjects
        cursor.execute('SELECT id FROM standards')
        all_standard_ids = [row[0] for row in cursor.fetchall()]

        for standard_id in all_standard_ids:
            # Get sections for this standard
            cursor.execute('SELECT id FROM sections WHERE standard_id = ?', (standard_id,))
            standard_section_ids = [row[0] for row in cursor.fetchall()]

            # Get the standard name to determine subjects
            cursor.execute('SELECT name FROM standards WHERE id = ?', (standard_id,))
            standard_name = cursor.fetchone()[0]

            # Determine subjects based on standard level
            if 'LKG' in standard_name or 'UKG' in standard_name or any(f"Standard {i}" in standard_name for i in range(1, 6)):
                subjects = primary_subjects
            elif any(f"Standard {i}" in standard_name for i in range(6, 10)):
                subjects = middle_subjects
            else:
                subjects = high_subjects

            # Create a class for each subject in each section
            for section_id in standard_section_ids:
                cursor.execute('SELECT name FROM sections WHERE id = ?', (section_id,))
                section_name = cursor.fetchone()[0]

                for subject in subjects:
                    # Assign a random teacher
                    teacher_profile_id = random.choice(teacher_profile_ids)

                    # Insert class
                    cursor.execute('''
                    INSERT INTO classes (name, standard_id, section_id, subject, teacher_id, schedule, room,
                                        academic_year, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        f"{standard_name} {section_name} - {subject}",
                        standard_id,
                        section_id,
                        subject,
                        teacher_profile_id,
                        f"{random.choice(['Mon,Wed,Fri', 'Tue,Thu', 'Mon,Thu', 'Wed,Fri'])} {random.randint(8, 15)}:00-{random.randint(9, 16)}:00",
                        f"{random.choice(['A', 'B', 'C', 'D'])}-{random.randint(101, 305)}",
                        '2023-2024',
                        1,
                        now,
                        now
                    ))

                    class_ids.append(cursor.lastrowid)

        print(f"Created {len(class_ids)} classes")

        # Insert sports
        sport_ids = []

        for sport_data in sports_list:
            # Assign a random teacher as instructor
            instructor_id = random.choice(teacher_profile_ids)

            cursor.execute('''
            INSERT INTO sports (name, category, instructor_id, schedule, location, description)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                sport_data['name'],
                sport_data['category'],
                instructor_id,
                f"{random.choice(['Mon,Wed,Fri', 'Tue,Thu,Sat', 'Mon,Thu', 'Wed,Fri,Sat'])} {random.choice(['Morning', 'Afternoon', 'Evening'])}",
                random.choice(['Main Ground', 'Indoor Stadium', 'Swimming Pool', 'Sports Complex', 'School Yard']),
                f"{sport_data['name']} training for students of all age groups."
            ))

            sport_ids.append(cursor.lastrowid)

        print(f"Created {len(sport_ids)} sports")

        # Commit the changes
        conn.commit()
        conn.close()

        print("Sample data inserted successfully!")
        return True
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

if __name__ == "__main__":
    insert_sample_data()
