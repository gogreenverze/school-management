from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.finance import (
    FeeSchedule, StudentFeeStructure, FeeCategory, FeeStructure,
    STATUS_PENDING, STATUS_COMPLETED, STATUS_OVERDUE
)
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
    
    print(f"Found {len(student_fee_structures)} active fee structures for student")
    
    # Get fee schedules for each fee structure
    for sfs in student_fee_structures:
        fee_structure = sfs.base_structure
        category = fee_structure.category
        
        print(f"\nFee Structure: {fee_structure.name} ({category.name})")
        print(f"Amount: ₹{fee_structure.amount}, Installments: {sfs.installments}")
        
        schedules = FeeSchedule.query.filter_by(
            student_fee_structure_id=sfs.id
        ).order_by(FeeSchedule.due_date).all()
        
        print(f"Found {len(schedules)} fee schedules:")
        
        for i, schedule in enumerate(schedules, 1):
            print(f"  {i}. Installment {schedule.installment_number}: ₹{schedule.amount}")
            print(f"     Due Date: {schedule.due_date.strftime('%d-%m-%Y')}")
            print(f"     Status: {schedule.status}")
            print(f"     Is Overdue: {schedule.is_overdue}")
            if schedule.is_overdue:
                print(f"     Days Overdue: {schedule.days_overdue}")
    
    print("\nFee summary complete.")
