from app import create_app, db
from app.models.finance import SportFee

app = create_app()
with app.app_context():
    print('Table name:', SportFee.__tablename__)
    print('Columns:', [c.name for c in SportFee.__table__.columns])
