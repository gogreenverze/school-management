"""
Script to update the sports table with new columns.
"""
import sqlite3
import os
from datetime import datetime

def update_sports_table():
    """Update the sports table with new columns"""
    try:
        # Check all possible database locations
        possible_db_paths = [
            os.path.join('app', 'school.db'),
            os.path.join('instance', 'school.db'),
            'school.db',
            'app.db'
        ]

        db_path = None
        for path in possible_db_paths:
            if os.path.exists(path):
                # Check if the database has the sports table
                try:
                    temp_conn = sqlite3.connect(path)
                    temp_cursor = temp_conn.cursor()
                    temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sports'")
                    if temp_cursor.fetchone():
                        db_path = path
                        print(f"Found sports table in {path}")
                        temp_conn.close()
                        break
                    temp_conn.close()
                except Exception as e:
                    print(f"Error checking {path}: {e}")

        if not db_path:
            raise Exception("Could not find a database with the sports table")

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(sports)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add new columns if they don't exist
        if 'image' not in columns:
            cursor.execute("ALTER TABLE sports ADD COLUMN image VARCHAR(256)")
            print("Added 'image' column to sports table")

        if 'icon' not in columns:
            cursor.execute("ALTER TABLE sports ADD COLUMN icon VARCHAR(64)")
            print("Added 'icon' column to sports table")

        if 'capacity' not in columns:
            cursor.execute("ALTER TABLE sports ADD COLUMN capacity INTEGER DEFAULT 30")
            print("Added 'capacity' column to sports table")

        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE sports ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("Added 'is_active' column to sports table")

        if 'created_at' not in columns:
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"ALTER TABLE sports ADD COLUMN created_at DATETIME DEFAULT '{current_time}'")
            print("Added 'created_at' column to sports table")

        if 'updated_at' not in columns:
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"ALTER TABLE sports ADD COLUMN updated_at DATETIME DEFAULT '{current_time}'")
            print("Added 'updated_at' column to sports table")

        # Set default values for existing sports
        cursor.execute("UPDATE sports SET image = NULL WHERE image IS NULL")
        cursor.execute("UPDATE sports SET icon = NULL WHERE icon IS NULL")
        cursor.execute("UPDATE sports SET capacity = 30 WHERE capacity IS NULL")
        cursor.execute("UPDATE sports SET is_active = 1 WHERE is_active IS NULL")

        # Create sport_students table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_students (
            sport_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            PRIMARY KEY (sport_id, student_id),
            FOREIGN KEY (sport_id) REFERENCES sports (id),
            FOREIGN KEY (student_id) REFERENCES student_profiles (id)
        )
        """)
        print("Created or verified 'sport_students' table")

        # Create sport_fees table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            amount FLOAT NOT NULL,
            frequency VARCHAR(20) NOT NULL,
            duration INTEGER,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (sport_id) REFERENCES sports (id)
        )
        """)
        print("Created or verified 'sport_fees' table")

        # Create sport_fee_payments table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sport_fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            sport_id INTEGER NOT NULL,
            sport_fee_id INTEGER NOT NULL,
            amount_paid FLOAT NOT NULL,
            payment_date DATETIME,
            payment_method VARCHAR(20) NOT NULL,
            transaction_id VARCHAR(64),
            receipt_number VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL,
            remarks VARCHAR(256),
            collected_by INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES student_profiles (id),
            FOREIGN KEY (sport_id) REFERENCES sports (id),
            FOREIGN KEY (sport_fee_id) REFERENCES sport_fees (id),
            FOREIGN KEY (collected_by) REFERENCES users (id)
        )
        """)
        print("Created or verified 'sport_fee_payments' table")

        # Commit changes and close connection
        conn.commit()
        conn.close()

        print("Sports table updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating sports table: {e}")
        return False

if __name__ == "__main__":
    update_sports_table()
