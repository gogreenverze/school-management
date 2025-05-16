from app import create_app, db
from app.models.user import User, StudentProfile
from app.models.finance import Invoice

app = create_app()
with app.app_context():
    # Find the user
    user = User.query.filter_by(username='bharath.ramachandran111923').first()
    if user:
        print(f'User found: {user.id} - {user.first_name} {user.last_name} - Role: {user.role}')
        
        # Find the student profile
        student = StudentProfile.query.filter_by(user_id=user.id).first()
        if student:
            print(f'Student profile found: {student.id} - {student.roll_number}')
            
            # Find invoices for this student
            invoices = Invoice.query.filter_by(student_id=student.id).all()
            print(f'Invoices found: {len(invoices)}')
            
            for invoice in invoices:
                print(f'Invoice {invoice.id}: {invoice.invoice_number} - Status: {invoice.status} - Student ID: {invoice.student_id}')
        else:
            print('Student profile not found')
    else:
        print('User not found')
