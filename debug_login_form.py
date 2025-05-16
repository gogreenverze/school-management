from app import create_app, db
from app.forms.auth import LoginForm
from flask import request

app = create_app()
with app.app_context():
    form = LoginForm()
    print(f'Form fields: {form._fields.keys()}')
    print(f'Username field: {form.username}')
    print(f'Password field: {form.password}')
    print(f'Remember me field: {form.remember_me}')
    print(f'Submit field: {form.submit}')
