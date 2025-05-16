from app import create_app, db
from app.models.finance import Invoice, INVOICE_STATUS_SENT

app = create_app()
with app.app_context():
    # Find the invoice
    invoice = Invoice.query.get(2)  # Invoice ID 2 from the previous check
    
    if invoice:
        print(f'Found invoice: {invoice.invoice_number} - Current status: {invoice.status}')
        
        # Update the status
        old_status = invoice.status
        invoice.status = INVOICE_STATUS_SENT
        
        # Commit the changes
        db.session.commit()
        
        print(f'Updated invoice status from {old_status} to {invoice.status}')
    else:
        print('Invoice not found')
