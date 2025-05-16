from app import create_app, db
from app.models.finance import Invoice, InvoiceItem, InvoicePayment

app = create_app()

with app.app_context():
    # Create the invoice tables
    db.create_all()
    
    print("Invoice tables created successfully!")
