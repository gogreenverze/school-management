from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.attendance import Attendance, Class
from app.models.academic import Homework, HomeworkSubmission
from datetime import datetime

app = create_app()
with app.app_context():
    student = User.query.filter_by(username='test.student').first()
    if student:
        print(f'Student: {student.first_name} {student.last_name}')
        
        # Check student profile
        profile = StudentProfile.query.filter_by(user_id=student.id).first()
        if profile:
            print(f'Student profile found: {profile.id}')
            print(f'Standard: {profile.standard.name if profile.standard else "None"}')
            print(f'Section: {profile.section.name if profile.section else "None"}')
            
            # Check classes
            classes = Class.query.filter_by(standard_id=profile.standard_id, section_id=profile.section_id).all()
            print(f'Classes: {len(classes)}')
            for class_obj in classes[:3]:  # Show first 3 classes
                print(f'  - {class_obj.name} ({class_obj.subject})')
            
            # Check attendance
            attendances = Attendance.query.filter_by(student_id=profile.id).all()
            print(f'Attendance records: {len(attendances)}')
            for attendance in attendances[:3]:  # Show first 3 attendance records
                class_obj = Class.query.get(attendance.class_id)
                print(f'  - {attendance.date}: {attendance.status} in {class_obj.name if class_obj else "Unknown class"}')
            
            # Check homework
            homeworks = []
            for class_obj in classes:
                class_homeworks = Homework.query.filter_by(class_id=class_obj.id).all()
                homeworks.extend(class_homeworks)
            
            print(f'Homework assignments: {len(homeworks)}')
            for homework in homeworks[:3]:  # Show first 3 homework assignments
                class_obj = Class.query.get(homework.class_id)
                print(f'  - {homework.title} for {class_obj.name if class_obj else "Unknown class"}, due {homework.due_date}')
                
                # Check submissions
                submission = HomeworkSubmission.query.filter_by(homework_id=homework.id, student_id=profile.id).first()
                if submission:
                    print(f'    Submitted: {submission.submission_date}, Grade: {submission.grade if submission.grade else "Not graded"}')
                else:
                    print(f'    Not submitted')
        else:
            print('Student profile not found')
    else:
        print('Student not found')
