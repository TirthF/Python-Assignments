"""
Student Assignment Tracker GUI Implementation
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv
import os

FILE = "assignments.json"
data = []

def load_data():
    """Loads existing data from the JSON file."""
    global data
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Could not load data file.")
            data = []

def save_data():
    """Saves the current data state to JSON."""
    try:
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)
    except IOError:
        messagebox.showerror("Error", "Could not save to file.")


def add_student():
    """Validates and adds a new student record to the tracker."""
    enrollment = entry_enrollment.get().strip()
    name = entry_name.get().strip()
    assignment = entry_assignment.get().strip()
    status = status_var.get()
    marks = entry_marks.get().strip()
    remarks = entry_remarks.get().strip()

    # Validation
    if not enrollment or not name or not assignment:
        messagebox.showerror("Error", "Please fill all required fields (Enrollment, Name, Assignment)")
        return

    try:
        marks_value = float(marks) if marks else 0
        if marks_value < 0:
            messagebox.showerror("Error", "Marks cannot be negative.")
            return
    except ValueError:
        messagebox.showerror("Error", "Marks must be a numeric value.")
        return

    record = {
        "enrollment": enrollment,
        "name": name,
        "assignment": assignment,
        "status": status,
        "marks": marks_value,
        "remarks": remarks
    }

    data.append(record)
    save_data()
    clear_fields()
    display_data()

    messagebox.showinfo("Success", "Record added successfully")


def clear_fields():
    """Clears all input fields in the form."""
    entry_enrollment.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_assignment.delete(0, tk.END)
    entry_marks.delete(0, tk.END)
    entry_remarks.delete(0, tk.END)
    status_var.set("Pending")


def display_data(records=None):
    """Displays records in the TreeView."""
    for item in tree.get_children():
        tree.delete(item)

    if records is None:
        records = data

    for record in records:
        tree.insert(
            "",
            tk.END,
            values=(
                record["enrollment"],
                record["name"],
                record["assignment"],
                record["status"],
                record["marks"],
                record["remarks"]
            )
        )


def filter_data():
    """Filters the displayed data based on status."""
    status = filter_var.get()

    if status == "All":
        display_data()
    else:
        filtered = [
            record for record in data
            if record["status"] == status
        ]
        display_data(filtered)


def export_csv():
    """Exports the current data to a CSV file."""
    if not data:
        messagebox.showwarning("Warning", "No data available to export.")
        return

    try:
        with open("assignment_report.csv", "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "enrollment",
                    "name",
                    "assignment",
                    "status",
                    "marks",
                    "remarks"
                ]
            )

            writer.writeheader()
            writer.writerows(data)

        messagebox.showinfo(
            "Success",
            "CSV report exported as assignment_report.csv"
        )
    except IOError:
        messagebox.showerror("Error", "Could not export CSV file.")

# Main Application Initialization
root = tk.Tk()
root.title("Assignment Tracker")
root.geometry("950x600")

# Load existing data
load_data()

title = tk.Label(
    root,
    text="Student Assignment Tracker",
    font=("Arial", 20, "bold")
)
title.pack(pady=10)

form = tk.Frame(root)
form.pack(pady=10)

tk.Label(form, text="Enrollment").grid(row=0, column=0, padx=5, pady=5)
entry_enrollment = tk.Entry(form)
entry_enrollment.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form, text="Name").grid(row=0, column=2, padx=5, pady=5)
entry_name = tk.Entry(form)
entry_name.grid(row=0, column=3, padx=5, pady=5)

tk.Label(form, text="Assignment").grid(row=1, column=0, padx=5, pady=5)
entry_assignment = tk.Entry(form)
entry_assignment.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form, text="Status").grid(row=1, column=2, padx=5, pady=5)

status_var = tk.StringVar(value="Pending")

status_box = ttk.Combobox(
    form,
    textvariable=status_var,
    values=["Pending", "Completed"],
    state="readonly"
)
status_box.grid(row=1, column=3, padx=5, pady=5)

tk.Label(form, text="Marks").grid(row=2, column=0, padx=5, pady=5)
entry_marks = tk.Entry(form)
entry_marks.grid(row=2, column=1, padx=5, pady=5)

tk.Label(form, text="Remarks").grid(row=2, column=2, padx=5, pady=5)
entry_remarks = tk.Entry(form)
entry_remarks.grid(row=2, column=3, padx=5, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Add Student",
    command=add_student
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame,
    text="Export CSV",
    command=export_csv
).grid(row=0, column=2, padx=5)

tk.Label(button_frame, text="Filter").grid(
    row=0, column=3, padx=5
)

filter_var = tk.StringVar(value="All")

filter_box = ttk.Combobox(
    button_frame,
    textvariable=filter_var,
    values=["All", "Pending", "Completed"],
    state="readonly",
    width=12
)
filter_box.grid(row=0, column=4, padx=5)

tk.Button(
    button_frame,
    text="Apply",
    command=filter_data
).grid(row=0, column=5, padx=5)

columns = (
    "Enrollment",
    "Name",
    "Assignment",
    "Status",
    "Marks",
    "Remarks"
)

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings"
)

for column in columns:
    tree.heading(column, text=column)
    tree.column(column, width=140)

tree.pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)

display_data()

root.mainloop()