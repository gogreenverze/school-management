"""
Migration script to update the fee_structures table with new columns.
"""
import sqlite3
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the database path
from app import create_app
app = create_app()
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

def run_migration():
    """Run the migration to update the fee_structures table"""
    print(f"Connecting to database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the fee_categories table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_categories'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("Creating fee_categories table")
        cursor.execute("""
        CREATE TABLE fee_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            description VARCHAR(256),
            is_recurring BOOLEAN DEFAULT 0,
            frequency VARCHAR(20),
            fee_type VARCHAR(20) NOT NULL DEFAULT 'tuition',
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Insert some default fee categories
        cursor.execute("""
        INSERT INTO fee_categories (name, description, is_recurring, frequency, fee_type)
        VALUES
        ('Tuition Fee', 'Regular tuition fee for academic classes', 1, 'quarterly', 'tuition'),
        ('Admission Fee', 'One-time fee paid at the time of admission', 0, NULL, 'tuition'),
        ('Examination Fee', 'Fee for conducting examinations', 1, 'semi_annually', 'exam'),
        ('Library Fee', 'Fee for library services', 1, 'annually', 'library'),
        ('Laboratory Fee', 'Fee for laboratory services', 1, 'annually', 'laboratory'),
        ('Sports Fee', 'Fee for sports activities', 1, 'monthly', 'sports'),
        ('Transportation Fee', 'Fee for transportation services', 1, 'monthly', 'transportation')
        """)

    # Check if the fee_structures table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_structures'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("Creating fee_structures table")
        cursor.execute("""
        CREATE TABLE fee_structures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            standard_id INTEGER,
            section_id INTEGER,
            name VARCHAR(64) NOT NULL DEFAULT 'Fee Structure',
            grade VARCHAR(10) NOT NULL,
            amount FLOAT NOT NULL,
            academic_year VARCHAR(10) NOT NULL,
            frequency VARCHAR(20) NOT NULL DEFAULT 'annually',
            installments_allowed BOOLEAN DEFAULT 0,
            max_installments INTEGER DEFAULT 1,
            due_date DATE,
            late_fee FLOAT DEFAULT 0.0,
            late_fee_frequency VARCHAR(20),
            discount_available BOOLEAN DEFAULT 0,
            discount_percentage FLOAT DEFAULT 0.0,
            discount_conditions TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES fee_categories(id)
        )
        """)
    else:
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(fee_structures)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add new columns if they don't exist
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

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"Adding column {column_name} to fee_structures table")
                cursor.execute(f"ALTER TABLE fee_structures ADD COLUMN {column_name} {column_type}")

    # Create the student_fee_structures table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_fee_structures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        fee_structure_id INTEGER NOT NULL,
        custom_amount FLOAT,
        discount_percentage FLOAT DEFAULT 0.0,
        discount_reason VARCHAR(256),
        installments INTEGER DEFAULT 1,
        custom_due_date DATE,
        is_active BOOLEAN DEFAULT 1,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student_profiles(id),
        FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(id)
    )
    """)

    # Create the fee_schedules table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_fee_structure_id INTEGER NOT NULL,
        installment_number INTEGER NOT NULL DEFAULT 1,
        amount FLOAT NOT NULL,
        due_date DATE NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        payment_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_fee_structure_id) REFERENCES student_fee_structures(id),
        FOREIGN KEY (payment_id) REFERENCES fee_payments(id)
    )
    """)

    # Create the transportation_fees table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transportation_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(64) NOT NULL,
        route_description TEXT,
        distance_km FLOAT,
        amount FLOAT NOT NULL,
        frequency VARCHAR(20) NOT NULL DEFAULT 'monthly',
        pickup_time VARCHAR(20),
        drop_time VARCHAR(20),
        vehicle_type VARCHAR(50),
        capacity INTEGER,
        late_fee FLOAT DEFAULT 0.0,
        late_fee_frequency VARCHAR(20),
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create the student_transportation table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_transportation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        transportation_fee_id INTEGER NOT NULL,
        pickup_address TEXT,
        drop_address TEXT,
        start_date DATE NOT NULL,
        end_date DATE,
        custom_amount FLOAT,
        discount_percentage FLOAT DEFAULT 0.0,
        discount_reason VARCHAR(256),
        is_active BOOLEAN DEFAULT 1,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student_profiles(id),
        FOREIGN KEY (transportation_fee_id) REFERENCES transportation_fees(id)
    )
    """)

    # Create the transportation_fee_schedules table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transportation_fee_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_transportation_id INTEGER NOT NULL,
        installment_number INTEGER NOT NULL DEFAULT 1,
        amount FLOAT NOT NULL,
        due_date DATE NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        payment_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_transportation_id) REFERENCES student_transportation(id),
        FOREIGN KEY (payment_id) REFERENCES transportation_fee_payments(id)
    )
    """)

    # Create the transportation_fee_payments table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transportation_fee_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        transportation_fee_id INTEGER NOT NULL,
        amount_paid FLOAT NOT NULL,
        payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        payment_method VARCHAR(20) NOT NULL,
        transaction_id VARCHAR(64),
        receipt_number VARCHAR(20) NOT NULL,
        status VARCHAR(20) NOT NULL,
        late_fee_paid FLOAT DEFAULT 0.0,
        discount_applied FLOAT DEFAULT 0.0,
        remarks VARCHAR(256),
        collected_by INTEGER NOT NULL,
        academic_year VARCHAR(10),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student_profiles(id),
        FOREIGN KEY (transportation_fee_id) REFERENCES transportation_fees(id),
        FOREIGN KEY (collected_by) REFERENCES users(id)
    )
    """)

    # Create the sport_fee_schedules table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sport_fee_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        sport_id INTEGER NOT NULL,
        sport_fee_id INTEGER NOT NULL,
        installment_number INTEGER NOT NULL DEFAULT 1,
        amount FLOAT NOT NULL,
        due_date DATE NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        payment_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student_profiles(id),
        FOREIGN KEY (sport_id) REFERENCES sports(id),
        FOREIGN KEY (sport_fee_id) REFERENCES sport_fees(id),
        FOREIGN KEY (payment_id) REFERENCES sport_fee_payments(id)
    )
    """)

    # Check if the fee_payments table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_payments'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("Creating fee_payments table")
        cursor.execute("""
        CREATE TABLE fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            fee_structure_id INTEGER NOT NULL,
            amount_paid FLOAT NOT NULL,
            payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            payment_method VARCHAR(20) NOT NULL,
            transaction_id VARCHAR(64),
            receipt_number VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL,
            late_fee_paid FLOAT DEFAULT 0.0,
            discount_applied FLOAT DEFAULT 0.0,
            remarks VARCHAR(256),
            collected_by INTEGER NOT NULL,
            academic_year VARCHAR(10) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student_profiles(id),
            FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(id),
            FOREIGN KEY (collected_by) REFERENCES users(id)
        )
        """)
    else:
        # Update existing fee_payments table with new columns if needed
        cursor.execute("PRAGMA table_info(fee_payments)")
        columns = [column[1] for column in cursor.fetchall()]

        new_columns = {
            'late_fee_paid': 'FLOAT DEFAULT 0.0',
            'discount_applied': 'FLOAT DEFAULT 0.0',
            'academic_year': 'VARCHAR(10)',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"Adding column {column_name} to fee_payments table")
                cursor.execute(f"ALTER TABLE fee_payments ADD COLUMN {column_name} {column_type}")

    # Check if the sport_fees table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sport_fees'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("Creating sport_fees table")
        cursor.execute("""
        CREATE TABLE sport_fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport_id INTEGER NOT NULL,
            name VARCHAR(64) NOT NULL,
            amount FLOAT NOT NULL,
            frequency VARCHAR(20) NOT NULL,
            duration INTEGER,
            description TEXT,
            late_fee FLOAT DEFAULT 0.0,
            late_fee_frequency VARCHAR(20),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sport_id) REFERENCES sports(id)
        )
        """)
    else:
        # Update existing sport_fees table with new columns if needed
        cursor.execute("PRAGMA table_info(sport_fees)")
        columns = [column[1] for column in cursor.fetchall()]

        new_columns = {
            'late_fee': 'FLOAT DEFAULT 0.0',
            'late_fee_frequency': 'VARCHAR(20)'
        }

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"Adding column {column_name} to sport_fees table")
                cursor.execute(f"ALTER TABLE sport_fees ADD COLUMN {column_name} {column_type}")

    # Check if the sport_fee_payments table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sport_fee_payments'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("Creating sport_fee_payments table")
        cursor.execute("""
        CREATE TABLE sport_fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            sport_id INTEGER NOT NULL,
            sport_fee_id INTEGER NOT NULL,
            amount_paid FLOAT NOT NULL,
            payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            payment_method VARCHAR(20) NOT NULL,
            transaction_id VARCHAR(64),
            receipt_number VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL,
            late_fee_paid FLOAT DEFAULT 0.0,
            discount_applied FLOAT DEFAULT 0.0,
            remarks VARCHAR(256),
            collected_by INTEGER NOT NULL,
            academic_year VARCHAR(10),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student_profiles(id),
            FOREIGN KEY (sport_id) REFERENCES sports(id),
            FOREIGN KEY (sport_fee_id) REFERENCES sport_fees(id),
            FOREIGN KEY (collected_by) REFERENCES users(id)
        )
        """)
    else:
        # Update existing sport_fee_payments table with new columns if needed
        cursor.execute("PRAGMA table_info(sport_fee_payments)")
        columns = [column[1] for column in cursor.fetchall()]

        new_columns = {
            'late_fee_paid': 'FLOAT DEFAULT 0.0',
            'discount_applied': 'FLOAT DEFAULT 0.0',
            'academic_year': 'VARCHAR(10)',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"Adding column {column_name} to sport_fee_payments table")
                cursor.execute(f"ALTER TABLE sport_fee_payments ADD COLUMN {column_name} {column_type}")

    # Check if the fee_reminders table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_reminders'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        print("Creating fee_reminders table")
        cursor.execute("""
        CREATE TABLE fee_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            fee_structure_id INTEGER,
            fee_schedule_id INTEGER,
            reminder_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            due_date DATE NOT NULL,
            amount_due FLOAT NOT NULL,
            message TEXT,
            sent BOOLEAN DEFAULT 0,
            sent_date DATETIME,
            notification_type VARCHAR(20) DEFAULT 'email',
            reminder_type VARCHAR(20) DEFAULT 'upcoming',
            response_received BOOLEAN DEFAULT 0,
            response_date DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student_profiles(id),
            FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(id),
            FOREIGN KEY (fee_schedule_id) REFERENCES fee_schedules(id)
        )
        """)
    else:
        # Update existing fee_reminders table with new columns if needed
        cursor.execute("PRAGMA table_info(fee_reminders)")
        columns = [column[1] for column in cursor.fetchall()]

        new_columns = {
            'notification_type': 'VARCHAR(20) DEFAULT "email"',
            'reminder_type': 'VARCHAR(20) DEFAULT "upcoming"',
            'response_received': 'BOOLEAN DEFAULT 0',
            'response_date': 'DATETIME',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"Adding column {column_name} to fee_reminders table")
                cursor.execute(f"ALTER TABLE fee_reminders ADD COLUMN {column_name} {column_type}")

    conn.commit()
    conn.close()

    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
