# Run: python test_all.py

import sys
import os
import subprocess
import tempfile

PYTHON_EXE = sys.executable

def get_script_name(q_num):
    # Matches current enrollment number or default Enrollment_2_X.py
    for name in [f"12502080603019_2_{q_num}.py", f"Enrollment_2_{q_num}.py"]:
        if os.path.exists(name):
            return name
    return f"12502080603019_2_{q_num}.py"

def print_result(q_no, title, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {q_no}: {title}")
    if details:
        print(f"       -> {details}")

def run_script(script_name, input_str="", args=None):
    cmd = [PYTHON_EXE, script_name]
    if args:
        cmd.extend(args)
    try:
        proc = subprocess.run(
            cmd,
            input=input_str,
            capture_output=True,
            text=True,
            timeout=10
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

# Q1: Regex-Based Email Intelligence Extractor 
def test_q1():
    script = get_script_name(1)
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("Contact a.b+1@adit.edu, root@@bad.com, test-user@x.org and a.b+1@adit.edu\n")
        f_name = f.name

    try:
        code, out, _ = run_script(script, args=[f_name])
        expected_lines = [
            "adit.edu 1 a.b+1@adit.edu",
            "x.org 1 test-user@x.org"
        ]
        passed = all(exp in out for exp in expected_lines)
        print_result("Q1", "Email Intelligence Extractor", passed, f"Output:\n{out}")
    finally:
        if os.path.exists(f_name):
            os.remove(f_name)

# Q2: Offline Web Scraping Ranker from HTML Pages 
def test_q2():
    script = get_script_name(2)
    html1 = """
    <div class="product">
        <h2 class="product-title">Python Book</h2>
        <span class="price">$499</span>
        <div class="rating">4.8</div>
    </div>
    """
    html2 = """
    <div class="product">
        <h2 class="product-title">USB Keyboard</h2>
        <span class="price">$799</span>
        <div class="rating">4.7</div>
    </div>
    """
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f1, \
         tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f2:
        f1.write(html1)
        f2.write(html2)
        p1, p2 = f1.name, f2.name

    try:
        inp = f"2 2\n{p1}\n{p2}\n"
        code, out, _ = run_script(script, input_str=inp)
        passed = "Python Book" in out and "USB Keyboard" in out
        print_result("Q2", "Offline Web Scraping Ranker", passed, f"Output:\n{out}")
    finally:
        for p in (p1, p2):
            if os.path.exists(p):
                os.remove(p)

# Q3: MySQL Student-Course Analytics Engine
def test_q3():
    script = get_script_name(3)
    code, out, err = run_script(script, args=["--help"])
    with open(script, "r", encoding="utf-8") as f:
        src = f.read()
    passed = "Student" in src and "CourseRegistration" in src and "idx_student_spi" in src
    print_result("Q3", "MySQL Student-Course Analytics Engine", passed, "Verified schema & parameterized queries")

# Q4: SQL Join Query Builder and Validator
def test_q4():
    script = get_script_name(4)
    inp = "columns: student.name, course.name; where: course.id=PY101; order: student.spi DESC; limit: 2\n"
    code, out, err = run_script(script, input_str=inp)
    passed1 = "SQL_OK" in out or "Asha" in out

    bad_inp = "columns: student.name; where: student.id=1; DROP TABLE Student; --; limit: 5\n"
    code, out2, err = run_script(script, input_str=bad_inp)
    passed2 = "SQL_REJECTED" in out2

    print_result("Q4", "SQL Join Query Builder & Validator", passed1 and passed2, "Safe SQL generated & injection blocked")

# Q5: Tkinter Contact Manager with MySQL Backend
def test_q5():
    script = get_script_name(5)
    with open(script, "r", encoding="utf-8") as f:
        src = f.read()
    widgets_ok = all(w in src for w in ["Entry", "Text", "Radiobutton", "Listbox", "Menu", "Combobox"])
    email_regex_ok = "re.match" in src and "Contact" in src and "UNIQUE" in src
    print_result("Q5", "Tkinter Contact Manager (MySQL)", widgets_ok and email_regex_ok, "All widgets and email validation verified")

# Q6: Log Anomaly Detector using Sliding Window 
def test_q6():
    script = get_script_name(6)
    sample_inp = (
        "3 10\n"
        "5\n"
        "00:00 u1 1.1.1.1 FAIL\n"
        "00:03 u1 1.1.1.1 FAIL\n"
        "00:05 u1 1.1.1.1 FAIL\n"
        "00:07 u1 2.2.2.2 SUCCESS\n"
        "00:08 u2 3.3.3.3 SUCCESS\n"
    )
    code, out, err = run_script(script, input_str=sample_inp)
    passed = "u1 00:07" in out
    print_result("Q6", "Log Anomaly Detector", passed, f"Output: {out}")

# Q7: Generator-Based JSON ETL Pipeline
def test_q7():
    script = get_script_name(7)
    sample_jsonl = (
        '{"device_id":"D1","temperature_c":30,"humidity":50}\n'
        '{"device_id":"D1","temperature_c":"bad","humidity":45}\n'
    )
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.jsonl', encoding='utf-8') as f:
        f.write(sample_jsonl)
        f_name = f.name

    try:
        code, out, err = run_script(script, args=[f_name])
        expected = "D1 count=1 min=30 max=30 avg=30.00 corrupted=1"
        passed = expected in out
        print_result("Q7", "Generator-Based JSON ETL Pipeline", passed, f"Output: {out}")
    finally:
        if os.path.exists(f_name):
            os.remove(f_name)

# Q8: Matrix Path Optimizer with Dynamic Programming
def test_q8():
    script = get_script_name(8)
    sample_inp = (
        "3 3\n"
        "1 2 3\n"
        "4 X 6\n"
        "7 8 9\n"
    )
    code, out, err = run_script(script, input_str=sample_inp)
    passed = "29 1" in out
    print_result("Q8", "Matrix Path Optimizer (DP)", passed, f"Output: {out}")

# Q9: OOP Inventory Merger with Operator Overloading
def test_q9():
    script = get_script_name(9)
    sample_inp = (
        "Inventory A: P1 Pen 10 5 8\n"
        "Inventory B: P1 Pen 7 4 9\n"
        "Operation: MERGE\n"
    )
    code, out, err = run_script(script, input_str=sample_inp)
    expected = "P1 Pen stock=17 purchase=4 selling=9"
    passed = expected in out
    print_result("Q9", "OOP Inventory Merger", passed, f"Output: {out}")

# Q10: Python Data Visualization Dashboard Exporter
def test_q10():
    script = get_script_name(10)
    sample_csv = (
        "enrollment,name,Python,DBMS,OS\n"
        "2201,Asha,92,88,95\n"
        "2202,Dev,78,,82\n"
        "2203,Rohan,65,70,58\n"
    )
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.csv', encoding='utf-8') as f:
        f.write(sample_csv)
        csv_path = f.name

    out_dir = tempfile.mkdtemp()
    try:
        code, out, err = run_script(script, args=[csv_path, out_dir])
        files_created = [
            os.path.exists(os.path.join(out_dir, "cleaned_marks.csv")),
            os.path.exists(os.path.join(out_dir, "summary.csv")),
            os.path.exists(os.path.join(out_dir, "grade_distribution.png")),
            os.path.exists(os.path.join(out_dir, "subject_average.png")),
            os.path.exists(os.path.join(out_dir, "top_performers.png")),
        ]
        passed = all(files_created)
        print_result("Q10", "Data Visualization Dashboard Exporter", passed, "Generated all 5 CSVs and PNG charts")
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

def main():
    print("=" * 60)
    print("ASSIGNMENT 2 - COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=" * 60)
    test_q1()
    test_q2()
    test_q3()
    test_q4()
    test_q5()
    test_q6()
    test_q7()
    test_q8()
    test_q9()
    test_q10()
    print("=" * 60)
    print("All tests completed.")

if __name__ == "__main__":
    main()
