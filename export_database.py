#!/usr/bin/env python
"""
Script to export the database content to SQL statements for the School Management System.
This allows the database to be recreated with all the mock data.
"""

import os
import sqlite3
import datetime

def get_table_names(conn):
    """Get all table names from the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables if table[0] != 'sqlite_sequence']

def get_table_schema(conn, table_name):
    """Get the schema for a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return columns

def get_table_data(conn, table_name):
    """Get all data from a table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    return rows

def format_value(value):
    """Format a value for SQL insertion"""
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, (datetime.date, datetime.datetime)):
        return f"'{value.isoformat()}'"
    else:
        # Escape single quotes in string values
        return "'" + str(value).replace("'", "''") + "'"

def generate_insert_statement(table_name, columns, row):
    """Generate an INSERT statement for a row"""
    column_names = [col[1] for col in columns]
    values = [format_value(val) for val in row]

    columns_str = ", ".join(column_names)
    values_str = ", ".join(values)

    return f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"

def export_database(db_path, output_file):
    """Export the database to SQL statements"""
    conn = sqlite3.connect(db_path)

    with open(output_file, 'w') as f:
        # Write header
        f.write("-- School Management System Database Export\n")
        f.write(f"-- Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Get all tables
        tables = get_table_names(conn)

        # Write PRAGMA for foreign keys
        f.write("PRAGMA foreign_keys=OFF;\n")
        f.write("BEGIN TRANSACTION;\n\n")

        # Process each table
        for table_name in tables:
            f.write(f"-- Table: {table_name}\n")

            # Get table schema
            columns = get_table_schema(conn, table_name)

            # Get table data
            rows = get_table_data(conn, table_name)

            # Generate INSERT statements
            for row in rows:
                insert_stmt = generate_insert_statement(table_name, columns, row)
                f.write(insert_stmt + "\n")

            f.write("\n")

        # Write commit
        f.write("COMMIT;\n")
        f.write("PRAGMA foreign_keys=ON;\n")

    conn.close()
    print(f"Database exported to {output_file}")

def main():
    """Main function"""
    # Get the database file path
    db_path = os.path.join('instance', 'school.db')

    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False

    # Create the output file
    output_file = 'database_export.sql'

    # Export the database
    export_database(db_path, output_file)

    return True

if __name__ == "__main__":
    if main():
        print("Export completed successfully!")
    else:
        print("Export failed. Please check the error messages above.")
