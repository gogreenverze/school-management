"""
Script to verify that the homework submissions page is working correctly.
"""
import sqlite3

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

def check_homework_assigned_dates(conn):
    """Check if all homework assignments have assigned dates"""
    cursor = conn.cursor()
    
    # Get all homework assignments
    cursor.execute("SELECT id, title, assigned_date FROM homeworks")
    homeworks = cursor.fetchall()
    
    print(f"Found {len(homeworks)} homework assignments")
    
    # Check if any homework has a NULL assigned_date
    null_assigned_dates = [hw for hw in homeworks if hw[2] is None]
    
    if null_assigned_dates:
        print(f"Found {len(null_assigned_dates)} homework assignments with NULL assigned_date")
        for hw in null_assigned_dates:
            print(f"  - ID: {hw[0]}, Title: {hw[1]}")
    else:
        print("All homework assignments have assigned dates")
        
    # Print all homework assignments
    print("\nAll homework assignments:")
    for hw in homeworks:
        print(f"  - ID: {hw[0]}, Title: {hw[1]}, Assigned Date: {hw[2]}")

def main():
    """Main function to verify the fix"""
    # Create a connection to the database
    conn = create_connection()
    if conn is None:
        return
    
    try:
        check_homework_assigned_dates(conn)
        print("\nVerification completed successfully!")
    except sqlite3.Error as e:
        print(f"Error verifying fix: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
