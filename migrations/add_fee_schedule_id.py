"""
Migration script to add fee_schedule_id to FeeReminder model.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app, db
from sqlalchemy import Column, Integer, ForeignKey
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Run the migration to add fee_schedule_id to FeeReminder model"""
    app = create_app()
    with app.app_context():
        logger.info("Starting migration to add fee_schedule_id to FeeReminder model")

        # Check if the column already exists
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('fee_reminders')]

        if 'fee_schedule_id' not in columns:
            logger.info("Adding fee_schedule_id column to fee_reminders table")

            # Add the column
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE fee_reminders ADD COLUMN fee_schedule_id INTEGER"))
                conn.commit()

            logger.info("Successfully added fee_schedule_id column to fee_reminders table")
        else:
            logger.info("fee_schedule_id column already exists in fee_reminders table")

        logger.info("Migration completed successfully")

if __name__ == "__main__":
    run_migration()
