"""
Migration script to update the database with the new fee management system models.
Run this script after deploying the new code to create the necessary tables.
"""
from app import create_app, db
from app.models.finance import (
    FeeCategory, FeeStructure, StudentFeeStructure, FeeSchedule, FeePayment, FeeReminder,
    TransportationFee, StudentTransportation, TransportationFeeSchedule, TransportationFeePayment,
    SportFeeSchedule
)
from app.models.user import User, ROLE_ADMIN
from datetime import datetime, timedelta, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upgrade_database():
    """Upgrade the database with the new fee management system models"""
    app = create_app()
    
    with app.app_context():
        logger.info("Starting fee system database upgrade...")
        
        # Create new tables
        logger.info("Creating new tables...")
        db.create_all()
        
        # Check if we need to create initial fee categories
        if FeeCategory.query.count() == 0:
            logger.info("Creating initial fee categories...")
            create_initial_fee_categories()
        
        logger.info("Fee system database upgrade completed successfully!")
        return True

def create_initial_fee_categories():
    """Create initial fee categories"""
    categories = [
        {
            'name': 'Tuition Fee',
            'description': 'Regular tuition fee for academic classes',
            'is_recurring': True,
            'frequency': 'quarterly',
            'fee_type': 'tuition',
            'is_active': True
        },
        {
            'name': 'Admission Fee',
            'description': 'One-time fee paid at the time of admission',
            'is_recurring': False,
            'frequency': None,
            'fee_type': 'tuition',
            'is_active': True
        },
        {
            'name': 'Examination Fee',
            'description': 'Fee for conducting examinations',
            'is_recurring': True,
            'frequency': 'semi_annually',
            'fee_type': 'exam',
            'is_active': True
        },
        {
            'name': 'Library Fee',
            'description': 'Fee for library services',
            'is_recurring': True,
            'frequency': 'annually',
            'fee_type': 'library',
            'is_active': True
        },
        {
            'name': 'Laboratory Fee',
            'description': 'Fee for laboratory services',
            'is_recurring': True,
            'frequency': 'annually',
            'fee_type': 'laboratory',
            'is_active': True
        },
        {
            'name': 'Sports Fee',
            'description': 'Fee for sports activities',
            'is_recurring': True,
            'frequency': 'monthly',
            'fee_type': 'sports',
            'is_active': True
        },
        {
            'name': 'Transportation Fee',
            'description': 'Fee for transportation services',
            'is_recurring': True,
            'frequency': 'monthly',
            'fee_type': 'transportation',
            'is_active': True
        },
        {
            'name': 'Uniform Fee',
            'description': 'Fee for school uniforms',
            'is_recurring': False,
            'frequency': None,
            'fee_type': 'uniform',
            'is_active': True
        },
        {
            'name': 'Books Fee',
            'description': 'Fee for textbooks and notebooks',
            'is_recurring': False,
            'frequency': None,
            'fee_type': 'books',
            'is_active': True
        }
    ]
    
    for category_data in categories:
        category = FeeCategory(**category_data)
        db.session.add(category)
    
    db.session.commit()
    logger.info(f"Created {len(categories)} initial fee categories")

def create_initial_transportation_fees():
    """Create initial transportation fees"""
    transportation_fees = [
        {
            'name': 'Zone A (0-5 km)',
            'route_description': 'Areas within 5 km radius of the school',
            'distance_km': 5.0,
            'amount': 800.0,
            'frequency': 'monthly',
            'pickup_time': '7:30 AM',
            'drop_time': '4:30 PM',
            'vehicle_type': 'School Bus',
            'capacity': 40,
            'late_fee': 50.0,
            'late_fee_frequency': 'weekly',
            'is_active': True
        },
        {
            'name': 'Zone B (5-10 km)',
            'route_description': 'Areas between 5-10 km radius of the school',
            'distance_km': 10.0,
            'amount': 1000.0,
            'frequency': 'monthly',
            'pickup_time': '7:00 AM',
            'drop_time': '5:00 PM',
            'vehicle_type': 'School Bus',
            'capacity': 40,
            'late_fee': 50.0,
            'late_fee_frequency': 'weekly',
            'is_active': True
        },
        {
            'name': 'Zone C (10-15 km)',
            'route_description': 'Areas between 10-15 km radius of the school',
            'distance_km': 15.0,
            'amount': 1200.0,
            'frequency': 'monthly',
            'pickup_time': '6:30 AM',
            'drop_time': '5:30 PM',
            'vehicle_type': 'School Bus',
            'capacity': 40,
            'late_fee': 50.0,
            'late_fee_frequency': 'weekly',
            'is_active': True
        }
    ]
    
    for fee_data in transportation_fees:
        fee = TransportationFee(**fee_data)
        db.session.add(fee)
    
    db.session.commit()
    logger.info(f"Created {len(transportation_fees)} initial transportation fees")

if __name__ == '__main__':
    upgrade_database()
