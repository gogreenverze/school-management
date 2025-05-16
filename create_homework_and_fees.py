"""
Script to create homework assignments from Rajkumar to Priya,
and add fee schedules and reminders.
"""
import sqlite3
from datetime import datetime, date, timedelta
import random

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

def get_user_ids(conn):
    """Get user IDs for Rajkumar and Priya"""
    cursor = conn.cursor()

    # Get Rajkumar's user ID and teacher profile ID
    cursor.execute("""
        SELECT u.id, tp.id
        FROM users u
        JOIN teacher_profiles tp ON u.id = tp.user_id
        WHERE u.username = 'rajkumar'
    """)
    rajkumar_data = cursor.fetchone()

    if not rajkumar_data:
        print("Rajkumar user not found. Please run create_specific_users.py first.")
        return None, None, None, None

    rajkumar_user_id, rajkumar_teacher_id = rajkumar_data

    # Get Priya's user ID and student profile ID
    cursor.execute("""
        SELECT u.id, sp.id, sp.standard_id, sp.section_id
        FROM users u
        JOIN student_profiles sp ON u.id = sp.user_id
        WHERE u.username = 'priya'
    """)
    priya_data = cursor.fetchone()

    if not priya_data:
        print("Priya user not found. Please run create_specific_users.py first.")
        return None, None, None, None

    priya_user_id, priya_student_id, standard_id, section_id = priya_data

    return rajkumar_user_id, rajkumar_teacher_id, priya_user_id, priya_student_id, standard_id, section_id

def create_class_for_rajkumar(conn, rajkumar_teacher_id, standard_id, section_id):
    """Create a class for Rajkumar if it doesn't exist"""
    cursor = conn.cursor()

    # Check if class already exists
    cursor.execute("""
        SELECT id FROM classes
        WHERE teacher_id = ? AND standard_id = ? AND section_id = ?
    """, (rajkumar_teacher_id, standard_id, section_id))

    class_id = cursor.fetchone()

    if class_id:
        return class_id[0]

    # Create class
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO classes (name, teacher_id, standard_id, section_id, subject, schedule, room, academic_year, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'Mathematics Class',
        rajkumar_teacher_id,
        standard_id,
        section_id,
        'Mathematics',
        'Mon,Wed,Fri 10:00 AM - 11:00 AM',
        'Room 101',
        '2023-2024',
        1,
        now,
        now
    ))

    class_id = cursor.lastrowid
    conn.commit()
    print(f"Created class for Rajkumar with ID: {class_id}")

    return class_id

def create_homework_assignments(conn, rajkumar_user_id, class_id):
    """Create homework assignments from Rajkumar"""
    cursor = conn.cursor()

    # Create multiple homework assignments
    homework_assignments = [
        {
            'title': 'Quadratic Equations Practice',
            'description': 'Solve the quadratic equations on page 45, problems 1-10.',
            'due_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'max_score': 20
        },
        {
            'title': 'Trigonometry Basics',
            'description': 'Complete the worksheet on sine, cosine, and tangent functions.',
            'due_date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'max_score': 15
        },
        {
            'title': 'Algebra Review',
            'description': 'Review algebraic expressions and solve the problems in Chapter 3.',
            'due_date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'max_score': 10
        },
        {
            'title': 'Geometry Problems',
            'description': 'Solve the geometry problems related to circles and triangles.',
            'due_date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'max_score': 25
        },
        {
            'title': 'Statistics Assignment',
            'description': 'Calculate mean, median, mode, and standard deviation for the given dataset.',
            'due_date': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'max_score': 30
        }
    ]

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for hw in homework_assignments:
        # Check if homework already exists
        cursor.execute("""
            SELECT id FROM homeworks
            WHERE title = ? AND class_id = ?
        """, (hw['title'], class_id))

        existing_hw = cursor.fetchone()

        if existing_hw:
            print(f"Homework '{hw['title']}' already exists. Skipping.")
            continue

        # Create homework
        cursor.execute("""
            INSERT INTO homeworks (title, description, class_id, due_date, max_score, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hw['title'],
            hw['description'],
            class_id,
            hw['due_date'],
            hw['max_score'],
            rajkumar_user_id,
            now,
            now
        ))

        print(f"Created homework: {hw['title']}")

    conn.commit()

def create_fee_categories(conn):
    """Create fee categories if they don't exist"""
    cursor = conn.cursor()

    # Define fee categories
    fee_categories = [
        {
            'name': 'Tuition Fee',
            'description': 'Regular tuition fee for academic year',
            'frequency': 'Monthly',
            'is_recurring': True,
            'fee_type': 'Academic'
        },
        {
            'name': 'Examination Fee',
            'description': 'Fee for conducting examinations',
            'frequency': 'Term',
            'is_recurring': False,
            'fee_type': 'Academic'
        },
        {
            'name': 'Library Fee',
            'description': 'Fee for library services',
            'frequency': 'Annual',
            'is_recurring': False,
            'fee_type': 'Facility'
        },
        {
            'name': 'Computer Lab Fee',
            'description': 'Fee for computer lab usage',
            'frequency': 'Term',
            'is_recurring': False,
            'fee_type': 'Facility'
        },
        {
            'name': 'Sports Fee',
            'description': 'Fee for sports activities',
            'frequency': 'Annual',
            'is_recurring': False,
            'fee_type': 'Extracurricular'
        }
    ]

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for category in fee_categories:
        # Check if category already exists
        cursor.execute("SELECT id FROM fee_categories WHERE name = ?", (category['name'],))
        existing_category = cursor.fetchone()

        if existing_category:
            print(f"Fee category '{category['name']}' already exists. Skipping.")
            continue

        # Create category
        cursor.execute("""
            INSERT INTO fee_categories (name, description, frequency, is_recurring, fee_type, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            category['name'],
            category['description'],
            category['frequency'],
            category['is_recurring'],
            category['fee_type'],
            1,
            now,
            now
        ))

        print(f"Created fee category: {category['name']}")

    conn.commit()

    # Return all fee categories
    cursor.execute("SELECT id, name FROM fee_categories")
    return cursor.fetchall()

def create_fee_structures(conn, standard_id, fee_categories):
    """Create fee structures for Priya's standard"""
    cursor = conn.cursor()

    # Define fee amounts
    fee_amounts = {
        'Tuition Fee': 2500,
        'Examination Fee': 1000,
        'Library Fee': 500,
        'Computer Lab Fee': 800,
        'Sports Fee': 1200
    }

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for category_id, category_name in fee_categories:
        # Check if fee structure already exists
        cursor.execute("""
            SELECT id FROM fee_structures
            WHERE category_id = ? AND standard_id = ?
        """, (category_id, standard_id))

        existing_structure = cursor.fetchone()

        if existing_structure:
            print(f"Fee structure for '{category_name}' already exists. Skipping.")
            continue

        # Get the standard grade
        cursor.execute("SELECT name FROM standards WHERE id = ?", (standard_id,))
        standard_name = cursor.fetchone()[0]

        # Create fee structure
        cursor.execute("""
            INSERT INTO fee_structures (category_id, standard_id, name, grade, amount, academic_year,
                                       frequency, installments_allowed, max_installments, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            category_id,
            standard_id,
            f"{category_name} for {standard_name}",
            standard_name.replace('Standard ', ''),  # Extract grade number
            fee_amounts.get(category_name, 1000),  # Default to 1000 if not specified
            '2023-2024',
            'Monthly' if category_name == 'Tuition Fee' else 'One-time',
            True,
            12 if category_name == 'Tuition Fee' else 1,
            1,
            now,
            now
        ))

        print(f"Created fee structure: {category_name}")

    conn.commit()

    # Return all fee structures for this standard
    cursor.execute("""
        SELECT fs.id, fc.name, fs.amount
        FROM fee_structures fs
        JOIN fee_categories fc ON fs.category_id = fc.id
        WHERE fs.standard_id = ?
    """, (standard_id,))

    return cursor.fetchall()

def create_student_fee_structures(conn, priya_student_id, fee_structures):
    """Create student-specific fee structures for Priya"""
    cursor = conn.cursor()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for structure_id, structure_name, amount in fee_structures:
        # Check if student fee structure already exists
        cursor.execute("""
            SELECT id FROM student_fee_structures
            WHERE student_id = ? AND fee_structure_id = ?
        """, (priya_student_id, structure_id))

        existing_structure = cursor.fetchone()

        if existing_structure:
            print(f"Student fee structure for '{structure_name}' already exists. Skipping.")
            continue

        # Create student fee structure
        cursor.execute("""
            INSERT INTO student_fee_structures (student_id, fee_structure_id, discount_percentage,
                                              custom_amount, installments, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            priya_student_id,
            structure_id,
            0,  # No discount
            amount,  # Use the same amount
            12 if structure_name == 'Tuition Fee' else 1,  # 12 installments for tuition, 1 for others
            1,
            now,
            now
        ))

        print(f"Created student fee structure: {structure_name}")

    conn.commit()

    # Return all student fee structures
    cursor.execute("""
        SELECT sfs.id, fc.name, COALESCE(sfs.custom_amount, fs.amount) as amount
        FROM student_fee_structures sfs
        JOIN fee_structures fs ON sfs.fee_structure_id = fs.id
        JOIN fee_categories fc ON fs.category_id = fc.id
        WHERE sfs.student_id = ?
    """, (priya_student_id,))

    return cursor.fetchall()

def create_fee_schedules(conn, priya_student_id, student_fee_structures):
    """Create fee schedules for Priya"""
    cursor = conn.cursor()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create monthly schedules for the next 6 months
    for i in range(6):
        due_date = (date.today() + timedelta(days=30 * i)).strftime('%Y-%m-%d')

        for structure_id, structure_name, amount in student_fee_structures:
            # For non-monthly fees, only create one schedule
            if structure_name != 'Tuition Fee' and i > 0:
                continue

            # Check if fee schedule already exists
            cursor.execute("""
                SELECT id FROM fee_schedules
                WHERE student_fee_structure_id = ? AND installment_number = ?
            """, (structure_id, i+1))

            existing_schedule = cursor.fetchone()

            if existing_schedule:
                print(f"Fee schedule for '{structure_name}' installment {i+1} already exists. Skipping.")
                continue

            # Create fee schedule
            cursor.execute("""
                INSERT INTO fee_schedules (student_fee_structure_id, installment_number, amount, due_date, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                structure_id,
                i+1,  # Installment number
                amount,
                due_date,
                'Pending' if i > 0 else 'Paid',  # First month is paid, rest are pending
                now,
                now
            ))

            fee_schedule_id = cursor.lastrowid

            # If first month, create a payment record
            if i == 0:
                payment_date = (date.today() - timedelta(days=5)).strftime('%Y-%m-%d')

                # Check the schema of fee_payments
                cursor.execute("PRAGMA table_info(fee_payments)")
                columns = [row[1] for row in cursor.fetchall()]

                if 'student_id' in columns and 'fee_schedule_id' in columns:
                    cursor.execute("""
                        INSERT INTO fee_payments (student_id, fee_schedule_id, amount, payment_date, payment_method, receipt_number, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        priya_student_id,
                        fee_schedule_id,
                        amount,
                        payment_date,
                        'Online Transfer',
                        f"RCPT-{random.randint(10000, 99999)}",
                        'Completed',
                        now,
                        now
                    ))

                    # Update the fee schedule with the payment ID
                    payment_id = cursor.lastrowid
                    cursor.execute("UPDATE fee_schedules SET payment_id = ? WHERE id = ?", (payment_id, fee_schedule_id))

                print(f"Created payment for {structure_name} installment {i+1}")

            print(f"Created fee schedule: {structure_name} installment {i+1} due on {due_date}")

    conn.commit()

def create_fee_reminders(conn, priya_student_id, priya_user_id):
    """Create fee reminders for Priya"""
    cursor = conn.cursor()

    # Get pending fee schedules
    cursor.execute("""
        SELECT fs.id, fc.name, fs.due_date, fs.amount
        FROM fee_schedules fs
        JOIN student_fee_structures sfs ON fs.student_fee_structure_id = sfs.id
        JOIN fee_structures fst ON sfs.fee_structure_id = fst.id
        JOIN fee_categories fc ON fst.category_id = fc.id
        WHERE sfs.student_id = ? AND fs.status = 'Pending'
    """, (priya_student_id,))

    pending_fees = cursor.fetchall()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if fee_reminders table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_reminders'")
    if not cursor.fetchone():
        print("fee_reminders table does not exist. Skipping reminders.")
        return

    # Check the schema of fee_reminders
    cursor.execute("PRAGMA table_info(fee_reminders)")
    columns = [row[1] for row in cursor.fetchall()]

    for fee_id, fee_name, due_date, amount in pending_fees:
        # Create reminder if the table has the right columns
        if 'student_id' in columns and 'fee_schedule_id' in columns:
            cursor.execute("""
                INSERT INTO fee_reminders (student_id, fee_schedule_id, reminder_date, message, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                priya_student_id,
                fee_id,
                (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                f"Reminder: Your {fee_name} payment of ₹{amount} is due on {due_date}. Please make the payment at your earliest convenience.",
                'Sent',
                now,
                now
            ))

        # Create notification
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, is_read, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            priya_user_id,
            f"Fee Reminder: {fee_name}",
            f"Your {fee_name} payment of ₹{amount} is due on {due_date}. Please make the payment at your earliest convenience.",
            0,  # Not read
            now,
            now
        ))

        print(f"Created fee reminder and notification for: {fee_name} due on {due_date}")

    conn.commit()

def create_invoices(conn, priya_student_id, priya_user_id):
    """Create invoices for Priya"""
    cursor = conn.cursor()

    # Check if invoices table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
    if not cursor.fetchone():
        print("invoices table does not exist. Skipping invoices.")
        return

    # Get all fee schedules
    cursor.execute("""
        SELECT fs.id, fc.name, fs.due_date, fs.amount, fs.status
        FROM fee_schedules fs
        JOIN student_fee_structures sfs ON fs.student_fee_structure_id = sfs.id
        JOIN fee_structures fst ON sfs.fee_structure_id = fst.id
        JOIN fee_categories fc ON fst.category_id = fc.id
        WHERE sfs.student_id = ?
    """, (priya_student_id,))

    fee_schedules = cursor.fetchall()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Group by month
    invoices_by_month = {}

    for fee_id, fee_name, due_date, amount, status in fee_schedules:
        month = due_date[:7]  # YYYY-MM

        if month not in invoices_by_month:
            invoices_by_month[month] = []

        invoices_by_month[month].append((fee_id, fee_name, due_date, amount, status))

    # Check the schema of invoices
    cursor.execute("PRAGMA table_info(invoices)")
    invoice_columns = [row[1] for row in cursor.fetchall()]

    # Check the schema of invoice_items
    cursor.execute("PRAGMA table_info(invoice_items)")
    invoice_item_columns = [row[1] for row in cursor.fetchall()]

    # Check the schema of invoice_payments
    cursor.execute("PRAGMA table_info(invoice_payments)")
    invoice_payment_columns = [row[1] for row in cursor.fetchall()]

    # Create one invoice per month
    for month, fees in invoices_by_month.items():
        # Check if invoice already exists for this month
        cursor.execute("""
            SELECT id FROM invoices
            WHERE student_id = ? AND invoice_date LIKE ?
        """, (priya_student_id, f"{month}%"))

        existing_invoice = cursor.fetchone()

        if existing_invoice:
            print(f"Invoice for {month} already exists. Skipping.")
            continue

        # Calculate total
        total_amount = sum(amount for _, _, _, amount, _ in fees)

        # Create invoice if the table has the right columns
        if 'student_id' in invoice_columns and 'invoice_number' in invoice_columns:
            cursor.execute("""
                INSERT INTO invoices (student_id, invoice_number, invoice_date, due_date, subtotal, tax, discount, total, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                priya_student_id,
                f"INV-{random.randint(10000, 99999)}",
                f"{month}-01",  # First day of month
                f"{month}-15",  # 15th of month
                total_amount,
                0,  # No tax
                0,  # No discount
                total_amount,
                'Paid' if all(status == 'Paid' for _, _, _, _, status in fees) else 'Pending',
                now,
                now
            ))

            invoice_id = cursor.lastrowid

            # Create invoice items if the table has the right columns
            if 'invoice_id' in invoice_item_columns and 'description' in invoice_item_columns:
                for fee_id, fee_name, due_date, amount, _ in fees:
                    cursor.execute("""
                        INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        invoice_id,
                        f"{fee_name} for {month}",
                        1,
                        amount,
                        amount,
                        now,
                        now
                    ))

            # If paid, create payment if the table has the right columns
            if all(status == 'Paid' for _, _, _, _, status in fees) and 'invoice_id' in invoice_payment_columns:
                cursor.execute("""
                    INSERT INTO invoice_payments (invoice_id, amount, payment_date, payment_method, transaction_id, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    total_amount,
                    f"{month}-05",  # 5th of month
                    'Online Transfer',
                    f"TXN-{random.randint(10000, 99999)}",
                    'Completed',
                    now,
                    now
                ))

            print(f"Created invoice for {month} with {len(fees)} items, total: ₹{total_amount}")

    conn.commit()

def main():
    """Main function to create homework and fees"""
    # Create a connection to the database
    conn = create_connection()
    if conn is None:
        return

    try:
        # Get user IDs
        user_data = get_user_ids(conn)
        if not user_data:
            return

        rajkumar_user_id, rajkumar_teacher_id, priya_user_id, priya_student_id, standard_id, section_id = user_data

        # Create class for Rajkumar
        class_id = create_class_for_rajkumar(conn, rajkumar_teacher_id, standard_id, section_id)

        # Create homework assignments
        create_homework_assignments(conn, rajkumar_user_id, class_id)

        # Create fee categories
        fee_categories = create_fee_categories(conn)

        # Create fee structures
        fee_structures = create_fee_structures(conn, standard_id, fee_categories)

        # Create student fee structures
        student_fee_structures = create_student_fee_structures(conn, priya_student_id, fee_structures)

        # Create fee schedules
        create_fee_schedules(conn, priya_student_id, student_fee_structures)

        # Create fee reminders
        create_fee_reminders(conn, priya_student_id, priya_user_id)

        # Create invoices
        create_invoices(conn, priya_student_id, priya_user_id)

        print("Homework assignments and fees created successfully!")
    except sqlite3.Error as e:
        print(f"Error creating data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
