from app import create_app, db
from app.models.user import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    student = User.query.filter_by(email='test.student@schoolmail.com').first()
    if student:
        print(f'Student: {student.first_name} {student.last_name}')
        print(f'Password hash: {student.password_hash}')
        print(f'Check password "test123": {check_password_hash(student.password_hash, "test123")}')
    else:
        print('Student not found')
