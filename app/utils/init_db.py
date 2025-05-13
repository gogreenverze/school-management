from app import db
from app.models.user import User, AdminProfile, ROLE_ADMIN
from app.models.academic import ContentBlock
from datetime import datetime

def create_initial_data():
    """Create initial data for the application if it doesn't exist."""
    
    # Check if we already have users
    if User.query.count() > 0:
        return
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@school.com',
        first_name='Admin',
        last_name='User',
        role=ROLE_ADMIN
    )
    admin.set_password('admin123')  # In production, use a secure password
    db.session.add(admin)
    db.session.flush()  # Flush to get the ID
    
    # Create admin profile
    admin_profile = AdminProfile(
        user_id=admin.id,
        department='Administration',
        phone='123-456-7890'
    )
    db.session.add(admin_profile)
    
    # Create initial content blocks
    home_content = ContentBlock(
        name='home_welcome',
        title='Welcome to Our School',
        content='<p>Welcome to our school management system. We provide quality education and comprehensive management of all school activities.</p>',
        location='home',
        order=1,
        is_active=True,
        created_by=admin.id
    )
    db.session.add(home_content)
    
    about_content = ContentBlock(
        name='about_school',
        title='About Our School',
        content='<p>Our school was established with the vision to provide quality education to all students. We focus on holistic development of students through academics, sports, and extracurricular activities.</p>',
        location='about',
        order=1,
        is_active=True,
        created_by=admin.id
    )
    db.session.add(about_content)
    
    contact_content = ContentBlock(
        name='contact_info',
        title='Contact Information',
        content='<p>Address: 123 School Street, City, Country</p><p>Phone: 123-456-7890</p><p>Email: info@school.com</p>',
        location='contact',
        order=1,
        is_active=True,
        created_by=admin.id
    )
    db.session.add(contact_content)
    
    # Commit changes
    db.session.commit()
