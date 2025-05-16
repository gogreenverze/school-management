from app import create_app, db
from app.models.user import User, StudentProfile, TeacherProfile
from app.models.attendance import Class, Attendance
from datetime import datetime

app = create_app()
with app.app_context():
    # Get Eswari teacher
    teacher = User.query.filter_by(first_name='Eswari').first()

    class_obj = Class.query.filter_by(id=347).first()
    students = StudentProfile.query.filter_by(standard_id=class_obj.standard_id, section_id=class_obj.section_id).all()
    today = datetime.now().date()

    for student in students:
        # Check if attendance already exists for this student, class, and date
        existing_attendance = Attendance.query.filter_by(
            class_id=class_obj.id,
            student_id=student.id,
            date=today
        ).first()

        if existing_attendance:
            print(f'Attendance already marked for student {student.user.first_name} {student.user.last_name} in class {class_obj.name}')
        else:
            attendance = Attendance(
                class_id=class_obj.id,
                student_id=student.id,
                date=today,
                status='present',
                recorded_by=teacher.id
            )
            db.session.add(attendance)
            db.session.commit()
            print(f'Attendance marked for student {student.user.first_name} {student.user.last_name} in class {class_obj.name}')
