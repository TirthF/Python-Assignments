"""
File: Enrollment_2_3.py (Replace 'Enrollment' with your Student ID / Enrollment Number)
Assignment: 2, Question: 3
Problem: MySQL Database Connection, Batch CSV Ingestion, and Indexed Querying
Language: Python 3.10 or above

Required Packages:
    pip install pymysql
    OR
    pip install mysql-connector-python

Database Schema:
    - Student(student_id VARCHAR(50) PK, name VARCHAR(100), spi DECIMAL(4,2), INDEX idx_student_spi(spi, student_id))
    - CourseRegistration(course_id VARCHAR(50), student_id VARCHAR(50), PRIMARY KEY(course_id, student_id),
                         INDEX idx_reg_student(student_id), FOREIGN KEY(student_id) REFERENCES Student(student_id))

Run Instructions:
    python Enrollment_2_3.py
"""

import sys
import os
import csv

# Support either pymysql or mysql.connector seamlessly
try:
    import pymysql as mysql_driver
    DB_ERROR_BASE = mysql_driver.MySQLError
except ImportError:
    try:
        import mysql.connector as mysql_driver
        from mysql.connector import Error as DB_ERROR_BASE
    except ImportError:
        sys.stderr.write("Error: Neither 'pymysql' nor 'mysql-connector-python' is installed.\n")
        sys.stderr.write("Please run: pip install pymysql\n")
        sys.exit(1)


def connect_to_database(host: str, user: str, password: str, db_name: str):
    """
    Establishes connection to MySQL server and selects/creates the database.
    """
    try:
        # First connect without db to ensure database exists
        connection = mysql_driver.connect(
            host=host,
            user=user,
            password=password,
            autocommit=False
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        cursor.execute(f"USE `{db_name}`;")
        connection.commit()
        return connection, cursor
    except DB_ERROR_BASE as err:
        sys.stderr.write(f"Database Connection Error: {err}\n")
        return None, None


def create_tables_and_indexes(cursor, connection) -> bool:
    """
    Creates Student and CourseRegistration tables if they do not exist.
    Creates indexes to support O(log n) filtering for course and SPI.
    """
    create_student_table = """
    CREATE TABLE IF NOT EXISTS Student (
        student_id VARCHAR(50) NOT NULL,
        name VARCHAR(100) NOT NULL,
        spi DECIMAL(4, 2) NOT NULL,
        PRIMARY KEY (student_id),
        INDEX idx_student_spi (spi, student_id)
    ) ENGINE=InnoDB;
    """

    create_registration_table = """
    CREATE TABLE IF NOT EXISTS CourseRegistration (
        student_id VARCHAR(50) NOT NULL,
        course_id VARCHAR(50) NOT NULL,
        PRIMARY KEY (course_id, student_id),
        INDEX idx_reg_student (student_id),
        FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """

    try:
        cursor.execute(create_student_table)
        cursor.execute(create_registration_table)
        connection.commit()
        return True
    except DB_ERROR_BASE as err:
        connection.rollback()
        sys.stderr.write(f"Schema Creation Error: {err}\n")
        return False


def insert_student_records_from_csv(file_path: str, cursor, connection, batch_size: int = 5000) -> int:
    """
    Batch inserts student records from CSV.
    Memory complexity: O(batch_size).
    """
    if not os.path.isfile(file_path):
        sys.stderr.write(f"File Error: student.csv not found at '{file_path}'\n")
        return 0

    insert_sql = "INSERT IGNORE INTO Student (student_id, name, spi) VALUES (%s, %s, %s);"
    inserted_count = 0
    batch = []

    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader, None)

            # Detect if header exists (non-numeric 3rd column)
            if header and len(header) >= 3:
                try:
                    float(header[2])
                    # Header was actually data
                    batch.append((header[0].strip(), header[1].strip(), float(header[2].strip())))
                except ValueError:
                    pass  # Proper header, continue

            for row in reader:
                if not row or len(row) < 3:
                    continue
                try:
                    s_id = row[0].strip()
                    name = row[1].strip()
                    spi_val = float(row[2].strip())
                    batch.append((s_id, name, spi_val))

                    if len(batch) >= batch_size:
                        cursor.executemany(insert_sql, batch)
                        connection.commit()
                        inserted_count += len(batch)
                        batch.clear()
                except ValueError:
                    continue

            if batch:
                cursor.executemany(insert_sql, batch)
                connection.commit()
                inserted_count += len(batch)

        return inserted_count
    except (DB_ERROR_BASE, OSError) as err:
        connection.rollback()
        sys.stderr.write(f"Student Ingestion Error: {err}\n")
        return inserted_count


def insert_registration_records_from_csv(file_path: str, cursor, connection, batch_size: int = 5000) -> int:
    """
    Batch inserts course registration records from CSV.
    Memory complexity: O(batch_size).
    """
    if not os.path.isfile(file_path):
        sys.stderr.write(f"File Error: registration.csv not found at '{file_path}'\n")
        return 0

    insert_sql = "INSERT IGNORE INTO CourseRegistration (student_id, course_id) VALUES (%s, %s);"
    inserted_count = 0
    batch = []

    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader, None)

            # Skip header if present
            if header and len(header) >= 2:
                if header[0].lower() not in ("student_id", "id", "studentid"):
                    batch.append((header[0].strip(), header[1].strip()))

            for row in reader:
                if not row or len(row) < 2:
                    continue
                s_id = row[0].strip()
                c_id = row[1].strip()
                batch.append((s_id, c_id))

                if len(batch) >= batch_size:
                    cursor.executemany(insert_sql, batch)
                    connection.commit()
                    inserted_count += len(batch)
                    batch.clear()

            if batch:
                cursor.executemany(insert_sql, batch)
                connection.commit()
                inserted_count += len(batch)

        return inserted_count
    except (DB_ERROR_BASE, OSError) as err:
        connection.rollback()
        sys.stderr.write(f"Registration Ingestion Error: {err}\n")
        return inserted_count


def query_registered_students(cursor, course_id: str, spi_threshold: float) -> list:
    """
    Executes parameterized query using indexes:
      1. B-tree index on CourseRegistration(course_id, student_id) in O(log n)
      2. Primary key on Student(student_id)
      3. Index on Student(spi, student_id)
    Returns sorted rows: SPI descending, student_id ascending.
    """
    query = """
    SELECT s.student_id, s.name, s.spi, r.course_id
    FROM Student s
    JOIN CourseRegistration r ON s.student_id = r.student_id
    WHERE r.course_id = %s AND s.spi > %s
    ORDER BY s.spi DESC, s.student_id ASC;
    """
    try:
        cursor.execute(query, (course_id, spi_threshold))
        return cursor.fetchall()
    except DB_ERROR_BASE as err:
        sys.stderr.write(f"Query Execution Error: {err}\n")
        return []


def display_results(rows: list) -> None:
    """
    Outputs student id, name, SPI, and course id.
    Format: student_id name spi course_id
    """
    for r in rows:
        student_id = r[0]
        name = r[1]
        spi_val = float(r[2])
        course_id = r[3]
        print(f"{student_id} {name} {spi_val} {course_id}")


def main() -> None:
    # 1. Collect inputs with interactive prompts / fallback defaults
    is_interactive = sys.stdin.isatty()

    def get_input(prompt_text, default_val=""):
        if is_interactive:
            val = input(f"{prompt_text} [{default_val}]: ").strip()
            return val if val else default_val
        val = sys.stdin.readline().strip()
        return val if val else default_val

    host = get_input("Database Host", "localhost")
    user = get_input("Database User", "root")
    password = get_input("Database Password", "")
    db_name = get_input("Database Name", "student_records")
    student_csv = get_input("Path to student.csv", "student.csv").strip('"\'')
    reg_csv = get_input("Path to registration.csv", "registration.csv").strip('"\'')
    course_id = get_input("Course ID", "PY101")
    
    threshold_str = get_input("SPI Threshold", "8.0")
    try:
        spi_threshold = float(threshold_str)
        if not (0.0 <= spi_threshold <= 10.0):
            sys.stderr.write(f"Warning: SPI threshold {spi_threshold} outside [0.0, 10.0].\n")
    except ValueError:
        sys.stderr.write(f"Error: Invalid SPI threshold '{threshold_str}'. Defaulting to 8.0.\n")
        spi_threshold = 8.0

    # 2. Database Connection
    connection, cursor = connect_to_database(host, user, password, db_name)
    if not connection or not cursor:
        sys.exit(1)

    try:
        # 3. Create Tables and Indexes
        if not create_tables_and_indexes(cursor, connection):
            sys.exit(1)

        # 4. Ingest CSV Data
        insert_student_records_from_csv(student_csv, cursor, connection)
        insert_registration_records_from_csv(reg_csv, cursor, connection)

        # 5. Query and Display Results
        results = query_registered_students(cursor, course_id, spi_threshold)
        display_results(results)

    finally:
        # 6. Safe Resource Cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
