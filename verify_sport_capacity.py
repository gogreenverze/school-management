"""
Script to verify that all sports have capacity values.
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

def check_sport_capacity(conn):
    """Check if all sports have capacity values"""
    cursor = conn.cursor()
    
    # Get all sports
    cursor.execute("SELECT id, name, capacity FROM sports")
    sports = cursor.fetchall()
    
    print(f"Found {len(sports)} sports")
    
    # Check if any sport has a NULL capacity
    null_capacity = [sport for sport in sports if sport[2] is None]
    
    if null_capacity:
        print(f"Found {len(null_capacity)} sports with NULL capacity")
        for sport in null_capacity:
            print(f"  - ID: {sport[0]}, Name: {sport[1]}")
    else:
        print("All sports have capacity values")
        
    # Print all sports
    print("\nAll sports:")
    for sport in sports:
        print(f"  - ID: {sport[0]}, Name: {sport[1]}, Capacity: {sport[2]}")

def main():
    """Main function to verify the fix"""
    # Create a connection to the database
    conn = create_connection()
    if conn is None:
        return
    
    try:
        check_sport_capacity(conn)
        print("\nVerification completed successfully!")
    except sqlite3.Error as e:
        print(f"Error verifying fix: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
