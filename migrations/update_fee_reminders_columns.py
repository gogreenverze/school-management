"""
Migration script to update the fee_reminders table with missing columns.
This script adds the missing columns to the fee_reminders table to match the model definition.
"""
import sqlite3
import os
import sys
from datetime import datetime

# Get the absolute path to the project directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add the project directory to the Python path
sys.path.insert(0, project_dir)

# Database path
db_path = os.path.join(project_dir, 'instance', 'school.db')

def run_migration():
    """Run the migration to add missing columns to fee_reminders table"""
    print(f"Connecting to database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_reminders'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("Error: fee_reminders table does not exist!")
            return False
        
        # Get current columns in the table
        cursor.execute("PRAGMA table_info(fee_reminders)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns to add
        new_columns = {
            'notification_type': 'VARCHAR(20) DEFAULT "email"',
            'reminder_type': 'VARCHAR(20) DEFAULT "upcoming"',
            'response_received': 'BOOLEAN DEFAULT 0',
            'response_date': 'DATETIME',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }
        
        # Add each column if it doesn't exist
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                print(f"Adding column {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE fee_reminders ADD COLUMN {column_name} {column_type}")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(fee_reminders)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {updated_columns}")
        
        return True
    
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
