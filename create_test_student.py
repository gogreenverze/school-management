from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.attendance import Class, Attendance
from app.models.academic import Homework, HomeworkSubmission
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Get Eswari teacher
    teacher = User.query.filter_by(first_name='Eswari').first()

    # Get the class
    class_obj = Class.query.filter_by(id=347).first()

    # Create a new test student
    test_student = User.query.filter_by(email='test.student@schoolmail.com').first()
    if not test_student:
        test_student = User(
            first_name='Test',
            last_name='Student',
            email='test.student@schoolmail.com',
            username='test.student',
            role='student'
        )
        test_student.set_password('test123')
        db.session.add(test_student)
        db.session.commit()
        print(f'Created new student: ID: {test_student.id}, Name: {test_student.first_name} {test_student.last_name}, Email: {test_student.email}')
    else:
        print(f'Student already exists: ID: {test_student.id}, Name: {test_student.first_name} {test_student.last_name}, Email: {test_student.email}')
        test_student.set_password('test123')
        db.session.commit()
        print('Password reset to test123')

    # Create or update student profile
    student_profile = StudentProfile.query.filter_by(user_id=test_student.id).first()
    if not student_profile:
        student_profile = StudentProfile(
            user_id=test_student.id,
            standard_id=class_obj.standard_id,
            section_id=class_obj.section_id,
            roll_number='TEST001',
            date_of_birth=datetime.now() - timedelta(days=365*16),
            admission_date=datetime.now() - timedelta(days=365),
            blood_group='O+',
            address='123 Test Street',
            emergency_contact='1234567890',
            academic_year='2023-2024'
        )
        db.session.add(student_profile)
        db.session.commit()
        print(f'Created student profile for {test_student.first_name} {test_student.last_name}')
    else:
        student_profile.standard_id = class_obj.standard_id
        student_profile.section_id = class_obj.section_id
        db.session.commit()
        print(f'Updated student profile for {test_student.first_name} {test_student.last_name}')

    # Assign homework to the student
    homework = Homework.query.filter_by(title='English Essay Writing').first()
    if not homework:
        homework = Homework(
            title='English Essay Writing',
            description='Write a 500-word essay on the topic "The Importance of Education in Modern Society".',
            class_id=class_obj.id,
            created_by=teacher.id,
            due_date=datetime.now() + timedelta(days=7)
        )
        db.session.add(homework)
        db.session.commit()
        print(f'Created homework: ID: {homework.id}, Title: {homework.title}, Due Date: {homework.due_date}')
    else:
        print(f'Homework already exists: ID: {homework.id}, Title: {homework.title}, Due Date: {homework.due_date}')

    # Mark attendance for the student
    today = datetime.now().date()
    existing_attendance = Attendance.query.filter_by(
        class_id=class_obj.id,
        student_id=student_profile.id,
        date=today
    ).first()

    if not existing_attendance:
        attendance = Attendance(
            class_id=class_obj.id,
            student_id=student_profile.id,
            date=today,
            status='present',
            recorded_by=teacher.id
        )
        db.session.add(attendance)
        db.session.commit()
        print(f'Attendance marked for student {test_student.first_name} {test_student.last_name} in class {class_obj.name}')
    else:
        print(f'Attendance already marked for student {test_student.first_name} {test_student.last_name} in class {class_obj.name}')

    print(f'\nLogin Information:')
    print(f'Email: {test_student.email}')
    print(f'Password: test123')
    print(f'Student ID: {test_student.id}')
    print(f'Name: {test_student.first_name} {test_student.last_name}')
    print(f'Class: {class_obj.name}')
