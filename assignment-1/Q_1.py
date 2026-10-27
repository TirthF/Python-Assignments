"""
Campus Merit Analyzer Implementations
"""

def get_n_k_m_input():
    """Helper function to get n, k, and m with validation."""
    while True:
        try:
            user_input = input("Enter number of students (n), top K students (k), and number of subjects (m) separated by space: ")
            parts = user_input.split()
            if len(parts) != 3:
                print("Error: Expected exactly 3 values (n, k, m). Please try again.")
                continue
            
            n, k, m = map(int, parts)
            
            if n < 0 or k < 0 or m < 0:
                print("Error: Values cannot be negative. Please try again.")
                continue
                
            return n, k, m
        except ValueError:
            print("Error: Please enter valid integers for n, k, and m.")

def get_student_data(m):
    """Helper function to get a valid student record."""
    while True:
        try:
            user_input = input(f"Enter enrollment, name, semester, cpi, and {m} subject marks separated by space: ")
            data = user_input.split()
            
            if len(data) != 4 + m:
                print(f"Error: Expected {4 + m} values, but got {len(data)}. Please try again.")
                continue
            
            enrollment = data[0]
            name = data[1]
            semester = int(data[2])
            cpi = float(data[3])
            marks = tuple(map(int, data[4:4 + m]))
            
            return enrollment, name, semester, cpi, marks
        except ValueError:
            print("Error: Invalid data format. Ensure semester and marks are integers, and cpi is a float.")

def main():
    # 1. Get initial configuration (n, k, m)
    n, k, m = get_n_k_m_input()

    semester_students = {}
    students = []

    # 2. Read 'n' student records
    if n > 0:
        print(f"\nPlease enter the details for {n} students:")
        
    for i in range(n):
        print(f"Student {i + 1}:")
        enrollment, name, semester, cpi, marks = get_student_data(m)
        
        avg_marks = sum(marks) / m if m > 0 else 0
        student = (enrollment, name, semester, cpi, marks, avg_marks)
        
        students.append(student)

        # Group students by semester for ranking
        if semester not in semester_students:
            semester_students[semester] = []
        semester_students[semester].append(student)

    print("\n--- Results ---")
    
    # 3. Calculate and print top K students for each semester
    for semester in sorted(semester_students.keys()):
        # Sort by: CPI (descending), Average Marks (descending), Enrollment (ascending)
        ranked_students = sorted(
            semester_students[semester],
            key=lambda x: (-x[3], -x[5], x[0])
        )

        top_k = ranked_students[:k]

        print(
            f"Semester {semester}:",
            *[student[0] for student in top_k]
        )

    # 4. Calculate and print toppers for each subject
    for subject_index in range(m):
        highest_mark = -1
        toppers = []

        for student in students:
            enrollment = student[0]
            marks = student[4]
            mark = marks[subject_index]

            if mark > highest_mark:
                highest_mark = mark
                toppers = [enrollment]
            elif mark == highest_mark:
                toppers.append(enrollment)

        # Sort toppers by enrollment ID for consistent output
        toppers.sort()
        print(f"S{subject_index + 1}:", *toppers)


if __name__ == "__main__":
    main()