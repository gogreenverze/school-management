from app import create_app, db
from app.models.user import User, StudentProfile

app = create_app()
with app.app_context():
    username = 'bharath.ramachandran111923'
    user = User.query.filter_by(username=username).first()
    print(f'User found: {user is not None}')
    if user:
        print(f'User ID: {user.id}, Name: {user.first_name} {user.last_name}, Email: {user.email}')
        student = StudentProfile.query.filter_by(user_id=user.id).first()
        print(f'Student profile found: {student is not None}')
        if student:
            print(f'Student ID: {student.id}, Roll Number: {student.roll_number}')
