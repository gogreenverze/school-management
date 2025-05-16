"""
Script to update existing homework assignments with assigned dates.
"""
import sqlite3
from datetime import datetime

# Database path
DB_PATH = 'instance/school.db'

def create_connection():
    """Create a connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def update_homework_assigned_dates(conn):
    """Update existing homework assignments with assigned dates"""
    cursor = conn.cursor()
    
    # Get all homework assignments without assigned dates
    cursor.execute("SELECT id FROM homeworks WHERE assigned_date IS NULL")
    homework_ids = [row[0] for row in cursor.fetchall()]
    
    if not homework_ids:
        print("No homework assignments found without assigned dates.")
        return
    
    # Update each homework with today's date as assigned date
    assigned_date = datetime.now().strftime('%Y-%m-%d')
    
    for homework_id in homework_ids:
        cursor.execute("UPDATE homeworks SET assigned_date = ? WHERE id = ?", (assigned_date, homework_id))
        print(f"Updated homework ID {homework_id} with assigned date {assigned_date}")
    
    conn.commit()
    print(f"Updated {len(homework_ids)} homework assignments with assigned dates.")

def main():
    """Main function to update homework assigned dates"""
    # Create a connection to the database
    conn = create_connection()
    if conn is None:
        return
    
    try:
        update_homework_assigned_dates(conn)
        print("Homework assigned dates updated successfully!")
    except sqlite3.Error as e:
        print(f"Error updating homework assigned dates: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
