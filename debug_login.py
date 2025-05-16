from app import create_app, db
from app.models.user import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    # Try to login with username
    username = 'test.student'
    password = 'test123'
    
    user = User.query.filter_by(username=username).first()
    if user:
        print(f'User found by username: {user.first_name} {user.last_name}')
        print(f'Password check: {check_password_hash(user.password_hash, password)}')
        print(f'Role: {user.role}')
        print(f'Is active: {user.is_active}')
    else:
        print(f'No user found with username: {username}')
    
    # Try to login with email
    email = 'test.student@schoolmail.com'
    user = User.query.filter_by(email=email).first()
    if user:
        print(f'User found by email: {user.first_name} {user.last_name}')
        print(f'Password check: {check_password_hash(user.password_hash, password)}')
        print(f'Role: {user.role}')
        print(f'Is active: {user.is_active}')
    else:
        print(f'No user found with email: {email}')
