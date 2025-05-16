from app import create_app, db
from app.models.academic_structure import Standard

app = create_app()
with app.app_context():
    total_standards = Standard.query.count()
    active_standards = Standard.query.filter_by(is_active=True).count()
    
    print(f'Total standards: {total_standards}')
    print(f'Active standards: {active_standards}')
