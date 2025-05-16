"""
Script to find the database file.
"""
import os

def find_db_files(start_path):
    """Find all .db files in the directory tree"""
    db_files = []
    
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.db'):
                db_path = os.path.join(root, file)
                db_files.append(db_path)
    
    return db_files

if __name__ == "__main__":
    start_path = '/Users/arkprabha/Desktop/School'
    db_files = find_db_files(start_path)
    
    if db_files:
        print("Found database files:")
        for db_file in db_files:
            print(f"  - {db_file}")
    else:
        print("No database files found.")
