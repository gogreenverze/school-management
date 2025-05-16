from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.finance import FeeSchedule, StudentFeeStructure
from app.models.academic import Notification
from datetime import datetime

app = create_app()
with app.app_context():
    # Find the student by username
    username = 'bharath.ramachandran111923'
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"User with username {username} not found.")
        exit(1)
    
    print(f"Found user: {user.first_name} {user.last_name}")
    
    # Get student profile
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    
    if not student:
        print(f"Student profile for user {user.first_name} {user.last_name} not found.")
        exit(1)
    
    print(f"Found student profile with ID: {student.id}")
    
    # Get student fee structures
    student_fee_structures = StudentFeeStructure.query.filter_by(
        student_id=student.id,
        is_active=True
    ).all()
    
    # Find the laboratory fee structure
    lab_fee_structure = None
    for sfs in student_fee_structures:
        if sfs.base_structure.name == "Science Laboratory Fee":
            lab_fee_structure = sfs
            break
    
    if not lab_fee_structure:
        print("Laboratory fee structure not found.")
        exit(1)
    
    print(f"Found laboratory fee structure: {lab_fee_structure.base_structure.name}")
    
    # Get the fee schedule for the laboratory fee
    lab_fee_schedule = FeeSchedule.query.filter_by(
        student_fee_structure_id=lab_fee_structure.id,
        installment_number=1
    ).first()
    
    if not lab_fee_schedule:
        print("Laboratory fee schedule not found.")
        exit(1)
    
    print(f"Found laboratory fee schedule with due date: {lab_fee_schedule.due_date.strftime('%d-%m-%Y')}")
    
    # Create a notification for the student
    notification = Notification(
        user_id=user.id,
        title="Overdue Fee Payment",
        message=f"Fee payment of ₹{lab_fee_schedule.amount} for {lab_fee_structure.base_structure.name} was due on {lab_fee_schedule.due_date.strftime('%d-%m-%Y')} and is now {lab_fee_schedule.days_overdue} days overdue.",
        category="fee",
        related_id=lab_fee_schedule.id
    )
    db.session.add(notification)
    db.session.commit()
    
    print(f"Created notification for {user.first_name} {user.last_name}:")
    print(f"Title: {notification.title}")
    print(f"Message: {notification.message}")
    print(f"Created at: {notification.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
    
    print("Notification created successfully.")
