"""
Script to generate sample data for the School Management System
with Tamil Nadu specific names and information.
"""
import random
from datetime import datetime, timedelta, date
from faker import Faker
from app import db, create_app
from app.models.user import User, AdminProfile, TeacherProfile, ParentProfile, StudentProfile
from app.models.academic_structure import Board, Standard, Section
from app.models.attendance import Class, Sport
from werkzeug.security import generate_password_hash

# Initialize Faker
fake = Faker('en_IN')  # Indian English locale

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
higher_secondary_groups = [
    'Pure Science (Physics, Chemistry, Mathematics, Biology)',
    'Computer Science (Physics, Chemistry, Mathematics, Computer Science)',
    'Commerce (Accountancy, Commerce, Economics, Computer Applications)',
    'Arts (History, Geography, Political Science, Economics)',
    'Vocational (Automobile, Electronics, IT, Agriculture)'
]

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
    return start_date + timedelta(days=random_days)

def generate_data():
    """Generate sample data for the School Management System"""
    # Use a clean app instance without registering blueprints
    from app import db
    from flask import Flask
    from app import login_manager, mail, admin, migrate

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-key-for-development'

    # Initialize extensions with app
    db.init_app(app)

    with app.app_context():
        print("Starting data generation...")

        # Create boards
        boards = []
        for board_data in tn_boards:
            board = Board(
                name=board_data['name'],
                code=board_data['code'],
                description=board_data['description'],
                state=board_data['state'],
                is_active=True
            )
            db.session.add(board)
            db.session.flush()
            boards.append(board)

        print(f"Created {len(boards)} boards")

        # Create standards for each board
        standards = []
        for board in boards:
            for std_data in tn_standards:
                standard = Standard(
                    name=std_data['name'],
                    description=std_data['description'],
                    board_id=board.id,
                    academic_year='2023-2024',
                    is_active=True
                )
                db.session.add(standard)
                db.session.flush()
                standards.append(standard)

        print(f"Created {len(standards)} standards")

        # Create sections for each standard
        sections = []
        for standard in standards:
            num_sections = random.randint(2, 6)  # Random number of sections between 2 and 6
            for i in range(num_sections):
                section = Section(
                    name=section_names[i],
                    standard_id=standard.id,
                    description=f"Section {section_names[i]} for {standard.name}",
                    capacity=random.randint(30, 45),
                    is_active=True
                )
                db.session.add(section)
                db.session.flush()
                sections.append(section)

        print(f"Created {len(sections)} sections")

        # Create teachers
        teachers = []
        teacher_profiles = []

        for i in range(100):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = random.choice(tamil_male_first_names)
                prefix = 'Mr.'
            else:
                first_name = random.choice(tamil_female_first_names)
                prefix = random.choice(['Ms.', 'Mrs.'])

            last_name = random.choice(tamil_surnames)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@schoolmail.com"

            # Create user
            teacher_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='teacher',
                is_active=True
            )
            teacher_user.password_hash = generate_password_hash('password123')
            db.session.add(teacher_user)
            db.session.flush()

            # Create teacher profile
            qualification = random.choice(teacher_qualifications)
            primary_subject = qualification.split('.')[-1].strip()

            teacher_profile = TeacherProfile(
                user_id=teacher_user.id,
                employee_id=f"TCH{100+i:03d}",
                date_of_birth=generate_random_date(1970, 1995),
                date_of_joining=generate_random_date(2000, 2022),
                primary_subject=primary_subject,
                secondary_subjects=', '.join(random.sample(primary_subjects + middle_subjects, 2)),
                qualification=qualification,
                experience_years=random.randint(1, 25),
                phone=f"+91 {random.randint(6000000000, 9999999999)}",
                emergency_contact=f"+91 {random.randint(6000000000, 9999999999)}",
                address=fake.address(),
                specialization=random.choice(['Primary', 'Middle School', 'High School', 'Higher Secondary']),
                bio=f"{prefix} {first_name} {last_name} is an experienced educator with expertise in {primary_subject}.",
                is_active=True
            )
            db.session.add(teacher_profile)
            db.session.flush()

            teachers.append(teacher_user)
            teacher_profiles.append(teacher_profile)

        print(f"Created {len(teachers)} teachers")

        # Create parents
        parents = []
        parent_profiles = []

        for i in range(150):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = random.choice(tamil_male_first_names)
            else:
                first_name = random.choice(tamil_female_first_names)

            last_name = random.choice(tamil_surnames)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@gmail.com"

            # Create user
            parent_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='parent',
                is_active=True
            )
            parent_user.password_hash = generate_password_hash('password123')
            db.session.add(parent_user)
            db.session.flush()

            # Create parent profile
            occupation = random.choice([
                'Teacher', 'Engineer', 'Doctor', 'Lawyer', 'Business Owner',
                'Government Employee', 'Farmer', 'Shopkeeper', 'Driver', 'Technician',
                'Accountant', 'Banker', 'Police Officer', 'Military Personnel', 'Nurse'
            ])

            parent_profile = ParentProfile(
                user_id=parent_user.id,
                phone=f"+91 {random.randint(6000000000, 9999999999)}",
                alternate_phone=f"+91 {random.randint(6000000000, 9999999999)}",
                occupation=occupation,
                annual_income=random.randint(200000, 2000000),
                address=fake.address(),
                relation_to_student=random.choice(['Father', 'Mother', 'Guardian']),
                emergency_contact=f"+91 {random.randint(6000000000, 9999999999)}",
                is_active=True
            )
            db.session.add(parent_profile)
            db.session.flush()

            parents.append(parent_user)
            parent_profiles.append(parent_profile)

        print(f"Created {len(parents)} parents")

        # Create students
        students = []
        student_profiles = []

        for i in range(200):
            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = random.choice(tamil_male_first_names)
            else:
                first_name = random.choice(tamil_female_first_names)

            last_name = random.choice(tamil_surnames)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@schoolmail.com"

            # Create user
            student_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='student',
                is_active=True
            )
            student_user.password_hash = generate_password_hash('password123')
            db.session.add(student_user)
            db.session.flush()

            # Assign to a random section
            random_section = random.choice(sections)
            random_standard = Standard.query.get(random_section.standard_id)

            # Assign to a random parent
            random_parent = random.choice(parent_profiles)

            # Create student profile
            student_profile = StudentProfile(
                user_id=student_user.id,
                roll_number=f"STU{1000+i:04d}",
                date_of_birth=generate_random_date(2005, 2015),
                standard_id=random_standard.id,
                section_id=random_section.id,
                admission_date=generate_random_date(2018, 2023),
                parent_id=random_parent.id,
                blood_group=random.choice(blood_groups),
                address=fake.address(),
                emergency_contact=f"+91 {random.randint(6000000000, 9999999999)}",
                medical_conditions=random.choice([None, 'Asthma', 'Allergies', 'Diabetes', 'None']),
                previous_school=f"{random.choice(['St.', 'Holy', 'Government', 'Public', 'Modern'])} {random.choice(['School', 'Higher Secondary School', 'Matriculation School'])}, {random.choice(tn_districts)}",
                academic_year='2023-2024',
                is_active=True
            )
            db.session.add(student_profile)
            db.session.flush()

            students.append(student_user)
            student_profiles.append(student_profile)

        print(f"Created {len(students)} students")

        # Create classes
        classes = []

        # Get all standards
        all_standards = Standard.query.all()

        # For each standard, create classes for different subjects
        for standard in all_standards:
            # Get sections for this standard
            standard_sections = Section.query.filter_by(standard_id=standard.id).all()

            # Determine subjects based on standard level
            if 'LKG' in standard.name or 'UKG' in standard.name or any(f"Standard {i}" in standard.name for i in range(1, 6)):
                subjects = primary_subjects
            elif any(f"Standard {i}" in standard.name for i in range(6, 10)):
                subjects = middle_subjects
            else:
                subjects = high_subjects

            # Create a class for each subject in each section
            for section in standard_sections:
                for subject in subjects:
                    # Assign a random teacher who teaches this subject
                    suitable_teachers = [t for t in teacher_profiles if subject in t.primary_subject or subject in t.secondary_subjects]
                    if not suitable_teachers:
                        suitable_teachers = teacher_profiles  # Fallback

                    teacher = random.choice(suitable_teachers)

                    # Create class
                    class_obj = Class(
                        name=f"{standard.name} {section.name} - {subject}",
                        standard_id=standard.id,
                        section_id=section.id,
                        subject=subject,
                        teacher_id=teacher.id,
                        schedule=f"{random.choice(['Mon,Wed,Fri', 'Tue,Thu', 'Mon,Thu', 'Wed,Fri'])} {random.randint(8, 15)}:00-{random.randint(9, 16)}:00",
                        room=f"{random.choice(['A', 'B', 'C', 'D'])}-{random.randint(101, 305)}",
                        academic_year='2023-2024',
                        is_active=True
                    )
                    db.session.add(class_obj)
                    db.session.flush()
                    classes.append(class_obj)

        print(f"Created {len(classes)} classes")

        # Create sports
        sports = []

        for sport_data in sports_list:
            # Assign a random teacher as instructor
            instructor = random.choice(teacher_profiles)

            sport = Sport(
                name=sport_data['name'],
                category=sport_data['category'],
                instructor_id=instructor.id,
                schedule=f"{random.choice(['Mon,Wed,Fri', 'Tue,Thu,Sat', 'Mon,Thu', 'Wed,Fri,Sat'])} {random.choice(['Morning', 'Afternoon', 'Evening'])}",
                location=random.choice(['Main Ground', 'Indoor Stadium', 'Swimming Pool', 'Sports Complex', 'School Yard']),
                description=f"{sport_data['name']} training for students of all age groups."
            )
            db.session.add(sport)
            db.session.flush()
            sports.append(sport)

        print(f"Created {len(sports)} sports")

        # Commit the session to save all data
        db.session.commit()
        print("Data generation completed successfully!")

if __name__ == "__main__":
    generate_data()
