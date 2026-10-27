"""
Enrollment_2_10.py
Assignment 2, Question 10: Python Data Visualization Dashboard Exporter
Input Format: Path of marks CSV and output folder path.
Output Format: cleaned_marks.csv, summary.csv, grade_distribution.png, subject_average.png, top_performers.png
Run Instructions:
    python Enrollment_2_10.py marks.csv ./output
    or simply:
    python Enrollment_2_10.py
Time Complexity: O(n * s) where s is number of subjects
Space Complexity: O(n * s)
"""

import sys
import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_grade(avg):
    if avg >= 85:
        return 'A'
    elif avg >= 70:
        return 'B'
    elif avg >= 55:
        return 'C'
    elif avg >= 40:
        return 'D'
    else:
        return 'F'

def create_sample_csv(filepath):
    sample_data = [
        ["enrollment", "name", "Python", "DBMS", "OS"],
        ["2201", "Asha", "92", "88", "95"],
        ["2202", "Dev", "78", "", "82"],
        ["2203", "Rohan", "65", "70", "58"],
        ["2204", "Priya", "85", "90", "89"],
        ["2205", "Amit", "", "60", "72"],
        ["2206", "Sneha", "95", "96", "98"],
        ["2207", "Rahul", "45", "52", "40"],
        ["2208", "Anjali", "72", "75", "80"]
    ]
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)

def main():
    if len(sys.argv) >= 3:
        input_csv = sys.argv[1]
        output_dir = sys.argv[2]
    elif len(sys.argv) == 2:
        input_csv = sys.argv[1]
        output_dir = "."
    else:
        print("=== Student Marks Data Cleaning & Visualization (Q10) ===")
        input_csv = input("Enter path to marks CSV (or press Enter for 'marks.csv'): ").strip()
        if not input_csv:
            input_csv = "marks.csv"
            if not os.path.exists(input_csv):
                create_sample_csv(input_csv)
                print(f"Created sample dataset: {input_csv}")

        output_dir = input("Enter output directory (or press Enter for current folder '.'): ").strip()
        if not output_dir:
            output_dir = "."

    if not os.path.exists(input_csv):
        print(f"Error: File '{input_csv}' not found.")
        return

    os.makedirs(output_dir, exist_ok=True)

    cleaned_rows = []
    subject_marks = {}

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        subjects = header[2:]

        for s in subjects:
            subject_marks[s] = []

        for row in reader:
            if not row:
                continue
            enrollment = row[0].strip()
            name = row[1].strip()
            marks = []

            for i, s in enumerate(subjects):
                val_str = row[2 + i].strip() if (2 + i) < len(row) else ""
                try:
                    m = float(val_str)
                    if m < 0 or m > 100:
                        m = 0.0
                except ValueError:
                    m = 0.0

                marks.append(m)
                subject_marks[s].append(m)

            total = sum(marks)
            avg = total / len(subjects) if subjects else 0.0
            grade = get_grade(avg)

            cleaned_rows.append({
                "enrollment": enrollment,
                "name": name,
                "marks": marks,
                "total": total,
                "avg": avg,
                "grade": grade
            })

    cleaned_csv_path = os.path.join(output_dir, "cleaned_marks.csv")
    with open(cleaned_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["enrollment", "name"] + subjects + ["Total", "Average", "Grade"])
        for r in cleaned_rows:
            writer.writerow([r["enrollment"], r["name"]] + [f"{m:.2f}" for m in r["marks"]] + [f"{r['total']:.2f}", f"{r['avg']:.2f}", r["grade"]])

    summary_csv_path = os.path.join(output_dir, "summary.csv")
    subject_averages = {}

    with open(summary_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Count", "Mean", "Min", "Max"])
        for s in subjects:
            vals = subject_marks[s]
            count = len(vals)
            mean_val = sum(vals) / count if count else 0.0
            min_val = min(vals) if count else 0.0
            max_val = max(vals) if count else 0.0
            subject_averages[s] = mean_val
            writer.writerow([s, count, f"{mean_val:.2f}", f"{min_val:.2f}", f"{max_val:.2f}"])

    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for r in cleaned_rows:
        grade_counts[r['grade']] += 1

    plt.figure(figsize=(6, 4))
    plt.bar(list(grade_counts.keys()), list(grade_counts.values()), color='#4A90E2')
    plt.title("Student Grade Distribution")
    plt.xlabel("Grade")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "grade_distribution.png")
    plt.savefig(chart1_path)
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.bar(list(subject_averages.keys()), list(subject_averages.values()), color='#50E3C2')
    plt.title("Subject-wise Average Marks")
    plt.xlabel("Subject")
    plt.ylabel("Average Marks (out of 100)")
    plt.ylim(0, 100)
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "subject_average.png")
    plt.savefig(chart2_path)
    plt.close()

    top_students = sorted(cleaned_rows, key=lambda x: x["avg"], reverse=True)[:5]
    names = [s["name"] for s in reversed(top_students)]
    scores = [s["avg"] for s in reversed(top_students)]

    plt.figure(figsize=(7, 4))
    plt.barh(names, scores, color='#F5A623')
    plt.title("Top Performing Students")
    plt.xlabel("Average Marks")
    plt.xlim(0, 100)
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "top_performers.png")
    plt.savefig(chart3_path)
    plt.close()

    print("\nSuccessfully generated output files:")
    print(f"1. {cleaned_csv_path}")
    print(f"2. {summary_csv_path}")
    print(f"3. {chart1_path}")
    print(f"4. {chart2_path}")
    print(f"5. {chart3_path}")

if __name__ == "__main__":
    main()
