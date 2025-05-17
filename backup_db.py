#!/usr/bin/env python
"""
Script to backup the database for the School Management System.
"""

import os
import sys
import shutil
import datetime
from pathlib import Path

def backup_database():
    """Backup the database file"""
    print("Backing up database...")
    
    # Get the database file path
    instance_dir = Path('instance')
    db_path = instance_dir / 'school.db'
    
    # Check if the database file exists
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        return False
    
    # Create backups directory if it doesn't exist
    backups_dir = Path('backups')
    if not backups_dir.exists():
        backups_dir.mkdir()
        print(f"Created backups directory at {backups_dir}")
    
    # Create a timestamped backup file
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backups_dir / f"school_db_backup_{timestamp}.db"
    
    # Copy the database file to the backup location
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up successfully to {backup_path}")
        return True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return False

if __name__ == "__main__":
    if backup_database():
        print("Backup completed successfully!")
    else:
        print("Backup failed. Please check the error messages above.")
        sys.exit(1)
