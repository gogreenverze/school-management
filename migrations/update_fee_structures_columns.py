"""
Migration script to update the fee_structures table with missing columns.
This script adds the missing columns to the fee_structures table to match the model definition.
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
    """Run the migration to add missing columns to fee_structures table"""
    print(f"Connecting to database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_structures'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("Error: fee_structures table does not exist!")
            return False
        
        # Get current columns in the table
        cursor.execute("PRAGMA table_info(fee_structures)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns to add
        new_columns = {
            'standard_id': 'INTEGER',
            'section_id': 'INTEGER',
            'name': 'VARCHAR(64) NOT NULL DEFAULT "Fee Structure"',
            'frequency': 'VARCHAR(20) NOT NULL DEFAULT "annually"',
            'installments_allowed': 'BOOLEAN DEFAULT 0',
            'max_installments': 'INTEGER DEFAULT 1',
            'late_fee_frequency': 'VARCHAR(20)',
            'discount_available': 'BOOLEAN DEFAULT 0',
            'discount_percentage': 'FLOAT DEFAULT 0.0',
            'discount_conditions': 'TEXT',
            'is_active': 'BOOLEAN DEFAULT 1'
        }
        
        # Add each column if it doesn't exist
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                print(f"Adding column {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE fee_structures ADD COLUMN {column_name} {column_type}")
        
        # Add foreign key constraints
        # Note: SQLite doesn't support adding foreign key constraints to existing tables
        # We'll need to create a new table with the constraints and migrate the data
        # For now, we'll just add the columns without constraints
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(fee_structures)")
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
