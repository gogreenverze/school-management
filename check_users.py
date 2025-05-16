from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print('Available users:')
    for user in users:
        print(f'Username: {user.username}, Role: {user.role}')
