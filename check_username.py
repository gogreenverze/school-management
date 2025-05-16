from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    student = User.query.filter_by(email='test.student@schoolmail.com').first()
    if student:
        print(f'Student: {student.first_name} {student.last_name}')
        print(f'Username: {student.username}')
        print(f'Email: {student.email}')
    else:
        print('Student not found')
