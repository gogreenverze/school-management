from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.finance import (
    FeeSchedule, StudentFeeStructure, FeeCategory, FeeStructure,
    STATUS_PENDING, STATUS_COMPLETED, STATUS_OVERDUE
)
from datetime import datetime, date, timedelta

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
    
    # Make the fee overdue by setting the due date to 10 days ago
    overdue_date = date.today() - timedelta(days=10)
    lab_fee_schedule.due_date = overdue_date
    
    db.session.commit()
    
    print(f"Updated laboratory fee schedule due date to: {overdue_date.strftime('%d-%m-%Y')}")
    print(f"Fee is now overdue by {(date.today() - overdue_date).days} days")
    
    # Verify the change
    updated_schedule = FeeSchedule.query.get(lab_fee_schedule.id)
    print(f"Verified: Due date is now {updated_schedule.due_date.strftime('%d-%m-%Y')}")
    print(f"Is overdue: {updated_schedule.is_overdue}")
    print(f"Days overdue: {updated_schedule.days_overdue}")
    
    print("Successfully made laboratory fee overdue.")
