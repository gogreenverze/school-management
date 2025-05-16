from app import create_app, db
from app.models.finance import Invoice, InvoiceItem, InvoicePayment
from app.models.user import StudentProfile, User
from flask import current_app

app = create_app()

with app.app_context():
    # Check if there are any invoices
    invoice_count = Invoice.query.count()
    print(f"Number of invoices: {invoice_count}")
    
    if invoice_count > 0:
        # Get the first invoice
        invoice = Invoice.query.first()
        print(f"Invoice ID: {invoice.id}")
        print(f"Invoice Number: {invoice.invoice_number}")
        print(f"Student ID: {invoice.student_id}")
        
        # Check if student exists
        student = StudentProfile.query.get(invoice.student_id)
        if student:
            print(f"Student exists: {student.id}")
            if student.user:
                print(f"Student user: {student.user.first_name} {student.user.last_name}")
            else:
                print("Student user does not exist")
        else:
            print("Student does not exist")
        
        # Check if creator exists
        if invoice.created_by:
            creator = User.query.get(invoice.created_by)
            if creator:
                print(f"Creator exists: {creator.first_name} {creator.last_name}")
            else:
                print("Creator does not exist")
        else:
            print("No creator ID")
    else:
        print("No invoices found in the database")
