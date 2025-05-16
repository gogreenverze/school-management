"""
Script to create an admin user for the School Management System.
"""
from app import create_app, db
from app.models.user import User, AdminProfile
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    """Create an admin user for the application"""
    print("Creating admin user...")
    
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists.")
            return True
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@school.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            created_at=datetime.now()
        )
        admin.password_hash = generate_password_hash('admin123')
        
        # Create admin profile
        admin_profile = AdminProfile(
            department='Administration',
            phone='+91 9876543210'
        )
        
        # Add to session
        db.session.add(admin)
        db.session.flush()  # Flush to get the admin.id
        
        admin_profile.user_id = admin.id
        db.session.add(admin_profile)
        
        # Create teacher user
        teacher = User(
            username='teacher1',
            email='teacher1@school.com',
            first_name='Teacher',
            last_name='One',
            role='teacher',
            is_active=True,
            created_at=datetime.now()
        )
        teacher.password_hash = generate_password_hash('teacher123')
        db.session.add(teacher)
        
        # Create student user
        student = User(
            username='student1',
            email='student1@school.com',
            first_name='Student',
            last_name='One',
            role='student',
            is_active=True,
            created_at=datetime.now()
        )
        student.password_hash = generate_password_hash('student123')
        db.session.add(student)
        
        # Commit the session
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Teacher user created successfully!")
        print("Username: teacher1")
        print("Password: teacher123")
        print("Student user created successfully!")
        print("Username: student1")
        print("Password: student123")
        return True

if __name__ == "__main__":
    create_admin_user()
