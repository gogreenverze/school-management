#!/usr/bin/env python
"""
Script to import the database content from SQL statements for the School Management System.
This recreates the database with all the mock data.
"""

import os
import sqlite3

def import_database(sql_file, db_path):
    """Import the database from SQL statements"""
    # Check if the database file already exists
    db_exists = os.path.exists(db_path)
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Read the SQL file
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Execute the SQL
    conn.executescript(sql)
    
    # Close the connection
    conn.close()
    
    print(f"Database {'updated' if db_exists else 'created'} at {db_path}")

def main():
    """Main function"""
    # Get the SQL file path
    sql_file = 'database_export.sql'
    
    # Check if the SQL file exists
    if not os.path.exists(sql_file):
        print(f"Error: SQL file not found at {sql_file}")
        return False
    
    # Get the database file path
    db_path = os.path.join('instance', 'school.db')
    
    # Backup the existing database if it exists
    if os.path.exists(db_path):
        backup_path = db_path + '.backup'
        print(f"Backing up existing database to {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
    
    # Import the database
    import_database(sql_file, db_path)
    
    return True

if __name__ == "__main__":
    if main():
        print("Import completed successfully!")
    else:
        print("Import failed. Please check the error messages above.")
