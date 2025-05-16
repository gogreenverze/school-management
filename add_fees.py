from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.finance import (
    FeeCategory, FeeStructure, StudentFeeStructure, FeeSchedule,
    STATUS_PENDING, FREQUENCY_MONTHLY, FREQUENCY_QUARTERLY, FREQUENCY_ANNUALLY,
    FEE_TYPE_TUITION, FEE_TYPE_EXAM, FEE_TYPE_LABORATORY
)
from app.utils.fee_utils import generate_fee_schedules
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
    
    # Check if fee categories exist, if not create them
    tuition_category = FeeCategory.query.filter_by(fee_type=FEE_TYPE_TUITION).first()
    if not tuition_category:
        tuition_category = FeeCategory(
            name="Tuition Fee",
            description="Regular tuition fee for academic year",
            is_recurring=True,
            frequency=FREQUENCY_QUARTERLY,
            fee_type=FEE_TYPE_TUITION,
            is_active=True
        )
        db.session.add(tuition_category)
        print("Created Tuition Fee category")
    
    exam_category = FeeCategory.query.filter_by(fee_type=FEE_TYPE_EXAM).first()
    if not exam_category:
        exam_category = FeeCategory(
            name="Examination Fee",
            description="Fee for examinations",
            is_recurring=True,
            frequency=FREQUENCY_QUARTERLY,
            fee_type=FEE_TYPE_EXAM,
            is_active=True
        )
        db.session.add(exam_category)
        print("Created Examination Fee category")
    
    lab_category = FeeCategory.query.filter_by(fee_type=FEE_TYPE_LABORATORY).first()
    if not lab_category:
        lab_category = FeeCategory(
            name="Laboratory Fee",
            description="Fee for laboratory usage",
            is_recurring=False,
            frequency=FREQUENCY_ANNUALLY,
            fee_type=FEE_TYPE_LABORATORY,
            is_active=True
        )
        db.session.add(lab_category)
        print("Created Laboratory Fee category")
    
    db.session.commit()
    
    # Check if fee structures exist, if not create them
    current_year = datetime.now().year
    academic_year = f"{current_year}-{current_year+1}"
    
    # Tuition Fee Structure
    tuition_structure = FeeStructure.query.filter_by(
        category_id=tuition_category.id,
        name="Regular Tuition Fee",
        academic_year=academic_year
    ).first()
    
    if not tuition_structure:
        tuition_structure = FeeStructure(
            category_id=tuition_category.id,
            name="Regular Tuition Fee",
            grade="All",
            amount=15000.00,
            academic_year=academic_year,
            frequency=FREQUENCY_QUARTERLY,
            installments_allowed=True,
            max_installments=4,
            due_date=date.today() + timedelta(days=15),
            late_fee=500.00,
            late_fee_frequency="monthly",
            is_active=True
        )
        db.session.add(tuition_structure)
        print("Created Tuition Fee structure")
    
    # Exam Fee Structure
    exam_structure = FeeStructure.query.filter_by(
        category_id=exam_category.id,
        name="Term Examination Fee",
        academic_year=academic_year
    ).first()
    
    if not exam_structure:
        exam_structure = FeeStructure(
            category_id=exam_category.id,
            name="Term Examination Fee",
            grade="All",
            amount=2000.00,
            academic_year=academic_year,
            frequency=FREQUENCY_QUARTERLY,
            installments_allowed=False,
            max_installments=1,
            due_date=date.today() + timedelta(days=10),
            late_fee=200.00,
            late_fee_frequency="weekly",
            is_active=True
        )
        db.session.add(exam_structure)
        print("Created Examination Fee structure")
    
    # Lab Fee Structure
    lab_structure = FeeStructure.query.filter_by(
        category_id=lab_category.id,
        name="Science Laboratory Fee",
        academic_year=academic_year
    ).first()
    
    if not lab_structure:
        lab_structure = FeeStructure(
            category_id=lab_category.id,
            name="Science Laboratory Fee",
            grade="All",
            amount=5000.00,
            academic_year=academic_year,
            frequency=FREQUENCY_ANNUALLY,
            installments_allowed=False,
            max_installments=1,
            due_date=date.today() + timedelta(days=5),
            late_fee=300.00,
            late_fee_frequency="weekly",
            is_active=True
        )
        db.session.add(lab_structure)
        print("Created Laboratory Fee structure")
    
    db.session.commit()
    
    # Assign fee structures to student
    # 1. Tuition Fee
    student_tuition = StudentFeeStructure.query.filter_by(
        student_id=student.id,
        fee_structure_id=tuition_structure.id,
        is_active=True
    ).first()
    
    if not student_tuition:
        student_tuition = StudentFeeStructure(
            student_id=student.id,
            fee_structure_id=tuition_structure.id,
            installments=4,
            is_active=True,
            notes="Regular tuition fee for academic year"
        )
        db.session.add(student_tuition)
        print("Assigned Tuition Fee to student")
    
    # 2. Exam Fee
    student_exam = StudentFeeStructure.query.filter_by(
        student_id=student.id,
        fee_structure_id=exam_structure.id,
        is_active=True
    ).first()
    
    if not student_exam:
        student_exam = StudentFeeStructure(
            student_id=student.id,
            fee_structure_id=exam_structure.id,
            installments=1,
            is_active=True,
            notes="Term examination fee"
        )
        db.session.add(student_exam)
        print("Assigned Examination Fee to student")
    
    # 3. Lab Fee
    student_lab = StudentFeeStructure.query.filter_by(
        student_id=student.id,
        fee_structure_id=lab_structure.id,
        is_active=True
    ).first()
    
    if not student_lab:
        student_lab = StudentFeeStructure(
            student_id=student.id,
            fee_structure_id=lab_structure.id,
            installments=1,
            is_active=True,
            notes="Annual laboratory fee"
        )
        db.session.add(student_lab)
        print("Assigned Laboratory Fee to student")
    
    db.session.commit()
    
    # Generate fee schedules for each assigned fee structure
    if student_tuition:
        generate_fee_schedules(student_tuition)
        print("Generated schedules for Tuition Fee")
    
    if student_exam:
        generate_fee_schedules(student_exam)
        print("Generated schedules for Examination Fee")
    
    if student_lab:
        generate_fee_schedules(student_lab)
        print("Generated schedules for Laboratory Fee")
    
    print("Successfully added fees to student:", user.first_name, user.last_name)
