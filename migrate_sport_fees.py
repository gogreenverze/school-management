"""
Migration script to add missing columns to the sport_fees table.
"""
from app import create_app, db
import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_columns_to_sport_fees():
    """Add missing columns to the sport_fees table."""
    app = create_app()

    # Get the database path from the app config
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if db_path.startswith('/'):
            # Absolute path
            database_path = db_path
        else:
            # Relative path
            database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)

    logger.info(f"Using database at: {database_path}")

    # List of database files to update
    database_files = [
        database_path,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance/school.db'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/school.db')
    ]

    for db_file in database_files:
        if os.path.exists(db_file):
            logger.info(f"Updating database: {db_file}")

            # Connect to the database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Check if the table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sport_fees'")
            if not cursor.fetchone():
                logger.info(f"Table 'sport_fees' does not exist in {db_file}")
                conn.close()
                continue

            # Check if the columns already exist
            cursor.execute("PRAGMA table_info(sport_fees)")
            columns = [column[1] for column in cursor.fetchall()]

            # Add the missing columns if they don't exist
            if 'late_fee' not in columns:
                logger.info(f"Adding 'late_fee' column to sport_fees table in {db_file}")
                cursor.execute("ALTER TABLE sport_fees ADD COLUMN late_fee FLOAT DEFAULT 0.0")

            if 'late_fee_frequency' not in columns:
                logger.info(f"Adding 'late_fee_frequency' column to sport_fees table in {db_file}")
                cursor.execute("ALTER TABLE sport_fees ADD COLUMN late_fee_frequency VARCHAR(20)")

            # Commit the changes
            conn.commit()
            conn.close()
        else:
            logger.info(f"Database file not found: {db_file}")

    logger.info("Migration completed successfully")

if __name__ == '__main__':
    add_columns_to_sport_fees()
