from app import create_app, db
from app.models.finance import InvoiceItem
from sqlalchemy import Column, Integer, ForeignKey, text

app = create_app()

with app.app_context():
    # Add the sport_id column to the invoice_items table if it doesn't exist
    inspector = db.inspect(db.engine)
    columns = [column['name'] for column in inspector.get_columns('invoice_items')]

    if 'sport_id' not in columns:
        print("Adding sport_id column to invoice_items table...")
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE invoice_items ADD COLUMN sport_id INTEGER REFERENCES sports(id)'))
            conn.commit()
        print("Column added successfully!")
    else:
        print("sport_id column already exists in invoice_items table.")

    print("Database update completed!")
