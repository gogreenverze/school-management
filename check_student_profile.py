from app import create_app, db
from app.models.user import User, StudentProfile

app = create_app()
with app.app_context():
    student = User.query.filter_by(email='test.student@schoolmail.com').first()
    if student:
        print(f'Student: {student.first_name} {student.last_name}')
        print(f'Student ID: {student.id}')
        print(f'Role: {student.role}')
        print(f'Is active: {student.is_active}')
        
        profile = StudentProfile.query.filter_by(user_id=student.id).first()
        if profile:
            print(f'Student profile found: {profile.id}')
            print(f'Roll number: {profile.roll_number}')
            print(f'Standard ID: {profile.standard_id}')
            print(f'Section ID: {profile.section_id}')
        else:
            print('Student profile not found')
    else:
        print('Student not found')
