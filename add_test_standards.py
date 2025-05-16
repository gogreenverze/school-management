from app import create_app, db
from app.models.academic_structure import Standard

app = create_app()

with app.app_context():
    # Check current standards count
    current_count = Standard.query.count()
    print(f'Current standards count: {current_count}')
    
    # Add test standards if needed
    if current_count < 5:
        for i in range(1, 6):
            standard = Standard(
                name=f'Test Standard {i}',
                description=f'Test description for standard {i}',
                academic_year='2023-2024',
                is_active=True
            )
            db.session.add(standard)
        
        db.session.commit()
        print('Added test standards')
        print(f'New standards count: {Standard.query.count()}')
    else:
        print('Enough standards already exist')
