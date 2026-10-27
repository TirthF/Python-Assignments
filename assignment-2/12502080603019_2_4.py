import sys
import os
import re
import json

COLUMN_WHITELIST = {
    "student.id": "student.student_id",
    "student.student_id": "student.student_id",
    "student.name": "student.name",
    "student.spi": "student.spi",
    "course.id": "course.id",
    "course.course_id": "course.id",
    "course.name": "course.name",
    "courseregistration.student_id": "courseregistration.student_id",
    "courseregistration.course_id": "courseregistration.course_id"
}

# Allowed operators for WHERE filters
ALLOWED_OPERATORS = {"=", "!=", "<>", ">=", "<=", ">", "<", "LIKE"}

# Dangerous SQL keywords and characters for injection detection
DANGEROUS_PATTERNS = re.compile(
    r'(--|/\*|\*/|;|UNION|DROP|ALTER|EXEC|EXECUTE|INSERT|UPDATE|DELETE|CREATE|INFORMATION_SCHEMA)',
    re.IGNORECASE
)

def get_database_connection():
 
    try:
        import pymysql
        conn = pymysql.connect(host="localhost", user="root", password="", autocommit=False)
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS student_records;")
        cur.execute("USE student_records;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Student (
                student_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                spi DECIMAL(4, 2) NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Course (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS CourseRegistration (
                student_id VARCHAR(50) NOT NULL,
                course_id VARCHAR(50) NOT NULL,
                PRIMARY KEY (course_id, student_id)
            );
        """)
        # Populate seed data if empty
        cur.execute("INSERT IGNORE INTO Student VALUES ('2201', 'Asha', 9.1), ('2207', 'Dev', 8.4), ('2203', 'Rohan', 7.9);")
        cur.execute("INSERT IGNORE INTO Course VALUES ('PY101', 'Programming with Python'), ('CS102', 'Data Structures');")
        cur.execute("INSERT IGNORE INTO CourseRegistration VALUES ('2201', 'PY101'), ('2207', 'PY101'), ('2203', 'PY101');")
        conn.commit()
        return conn, cur, "%s"
    except Exception:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("CREATE TABLE Student (student_id TEXT PRIMARY KEY, name TEXT, spi REAL);")
        cur.execute("CREATE TABLE Course (id TEXT PRIMARY KEY, name TEXT);")
        cur.execute("CREATE TABLE CourseRegistration (student_id TEXT, course_id TEXT, PRIMARY KEY(course_id, student_id));")
        cur.execute("INSERT INTO Student VALUES ('2201', 'Asha', 9.1), ('2207', 'Dev', 8.4), ('2203', 'Rohan', 7.9);")
        cur.execute("INSERT INTO Course VALUES ('PY101', 'Programming with Python'), ('CS102', 'Data Structures');")
        cur.execute("INSERT INTO CourseRegistration VALUES ('2201', 'PY101'), ('2207', 'PY101'), ('2203', 'PY101');")
        conn.commit()
        return conn, cur, "?"


def parse_query_input(raw_text: str) -> dict:

    clean_text = raw_text.strip()

    if re.search(r'(--|/\*|\*/|UNION|DROP|ALTER|EXEC|EXECUTE|INSERT|UPDATE|DELETE|CREATE|INFORMATION_SCHEMA)', clean_text, re.IGNORECASE):
        raise ValueError("Unsafe SQL keyword or comment pattern detected in input.")

    if clean_text.startswith("{") and clean_text.endswith("}"):
        return json.loads(clean_text)

    config = {}
    tokens = [t.strip() for t in clean_text.split(";") if t.strip()]
    allowed_keys = {"columns", "where", "order", "limit"}

    for token in tokens:
        if ":" not in token:
            raise ValueError(f"Malformed input token (missing ':'): '{token}'")
        key, val = token.split(":", 1)
        k_clean = key.strip().lower()
        if k_clean not in allowed_keys:
            raise ValueError(f"Unrecognized configuration key: '{key.strip()}'")
        config[k_clean] = val.strip()

    return config

def validate_and_generate_query(config: dict, placeholder: str = "%s") -> tuple[str, list]:

    cols_raw = config.get("columns", "")
    if isinstance(cols_raw, list):
        col_list = [c.strip() for c in cols_raw if c.strip()]
    else:
        col_list = [c.strip() for c in cols_raw.split(",") if c.strip()]

    if not col_list:
        raise ValueError("No projection columns specified.")

    mapped_cols = []
    for col in col_list:
        norm_col = col.lower()
        if DANGEROUS_PATTERNS.search(norm_col) or norm_col not in COLUMN_WHITELIST:
            raise ValueError(f"Invalid or unauthorized column: '{col}'")
        mapped_cols.append(COLUMN_WHITELIST[norm_col])

    select_clause = ", ".join(mapped_cols)

    # Validate WHERE Clause & Extract Parameters
    where_raw = config.get("where", "").strip()
    where_clause = ""
    params = []

    if where_raw:
        if DANGEROUS_PATTERNS.search(where_raw):
            raise ValueError("Unsafe SQL pattern detected in WHERE clause.")

        # Split multiple filters by AND
        filter_parts = re.split(r'\s+AND\s+', where_raw, flags=re.IGNORECASE)
        condition_sql = []

        for f in filter_parts:
            # Pattern: column, comparison operator, value
            match = re.match(r'^([a-zA-Z0-9_.]+)\s*(=|!=|<>|>=|<=|>|<|LIKE)\s*(.+)$', f.strip(), re.IGNORECASE)
            if not match:
                raise ValueError(f"Malformed filter condition: '{f}'")

            col = match.group(1).strip().lower()
            op = match.group(2).strip().upper()
            val = match.group(3).strip().strip("'\"")

            if col not in COLUMN_WHITELIST:
                raise ValueError(f"Unauthorized column in filter: '{col}'")

            if op not in ALLOWED_OPERATORS:
                raise ValueError(f"Unauthorized operator: '{op}'")

            condition_sql.append(f"{COLUMN_WHITELIST[col]} {op} {placeholder}")
            params.append(val)

        where_clause = "WHERE " + " AND ".join(condition_sql)

    # Validate ORDER BY
    order_raw = config.get("order", "").strip()
    order_clause = ""

    if order_raw:
        if DANGEROUS_PATTERNS.search(order_raw):
            raise ValueError("Unsafe SQL pattern detected in ORDER BY clause.")

        parts = order_raw.split()
        order_col = parts[0].strip().lower()

        if order_col not in COLUMN_WHITELIST:
            raise ValueError(f"Unauthorized column in ORDER BY: '{order_col}'")

        direction = parts[1].upper() if len(parts) > 1 else "ASC"
        if direction not in ("ASC", "DESC"):
            raise ValueError(f"Invalid sort direction: '{direction}' (must be ASC or DESC)")

        order_clause = f"ORDER BY {COLUMN_WHITELIST[order_col]} {direction}"

    # Validate LIMIT Constraint (1 <= LIMIT <= 1000)
    limit_raw = config.get("limit", 10)
    try:
        limit_val = int(limit_raw)
    except (ValueError, TypeError):
        raise ValueError(f"LIMIT must be an integer, got '{limit_raw}'")

    if not (1 <= limit_val <= 1000):
        raise ValueError(f"LIMIT constraint violated: must be between 1 and 1000, got {limit_val}")

    # Assemble Safe SQL Template
    sql_template = f"""
SELECT {select_clause}
FROM Student student
JOIN CourseRegistration courseregistration ON student.student_id = courseregistration.student_id
JOIN Course course ON course.id = courseregistration.course_id
{where_clause}
{order_clause}
LIMIT {placeholder};
""".strip()

    params.append(limit_val)
    return sql_template, params


def main():
    prompt_text = "Enter query builder input (key-values or JSON): " if sys.stdin.isatty() else ""
    try:
        raw_input = input(prompt_text).strip()
        while not raw_input:
            raw_input = input().strip()
    except (EOFError, KeyboardInterrupt):
        return

    # Parse and Validate Input against Whitelists
    try:
        config = parse_query_input(raw_input)
        conn, cursor, placeholder = get_database_connection()
        sql_template, params = validate_and_generate_query(config, placeholder)
    except ValueError as err:
        print(f"SQL_REJECTED: {err}")
        sys.exit(1)

    # Execute Parameterized Query
    try:
        cursor.execute(sql_template, params)
        rows = cursor.fetchall()

        print("SQL_OK")
        for row in rows:
            print(" ".join(str(item) for item in row))
    except Exception as err:
        print(f"SQL_REJECTED: Database execution error: {err}")
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
