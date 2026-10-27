"""
Enrollment_2_5.py
Assignment 2, Question 5: Tkinter Contact Manager with MySQL Backend
Problem Statement: Develop a Tkinter contact manager that stores contacts in MySQL. It must support create,
update, delete, search by name/email/phone, and sorted display. Use Entry, Text, Radio Button or Check Button,
Listbox/Menu and Combobox widgets. Validate email using regex before insert/update.
Input Format: GUI-based inputs and MySQL database configuration.
Output Format: Interactive GUI and database table Contact(id, name, email, phone, category, notes).
Constraints: At least 10000 contacts should be searchable. Email validation must follow the syllabus pattern style.
Duplicate email must be rejected.
Expected Time Complexity: O(log n) for indexed search; O(n) acceptable for unindexed prototype but must be documented
Expected Space Complexity: O(result size) in Python; database stores persistent records
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import mysql.connector

# Connect to MySQL and create database & table
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port=3306
)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS contact_db")
cursor.execute("USE contact_db")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    category VARCHAR(50),
    notes TEXT,
    INDEX idx_name (name),
    INDEX idx_phone (phone)
)
""")
conn.commit()

selected_contact_id = None

# Email regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def validate_email(email):
    return re.match(EMAIL_REGEX, email) is not None

def load_contacts(rows=None):
    listbox.delete(0, tk.END)
    if rows is None:
        order_col = sort_by_combo.get()
        order_dir = sort_order_var.get()
        cursor.execute(f"SELECT * FROM Contact ORDER BY {order_col} {order_dir}")
        rows = cursor.fetchall()

    for r in rows:
        listbox.insert(tk.END, f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")

def clear_fields():
    global selected_contact_id
    selected_contact_id = None
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    category_combo.set("Faculty")
    notes_text.delete("1.0", tk.END)

def on_select(event):
    global selected_contact_id
    selected = listbox.curselection()
    if not selected:
        return
    text = listbox.get(selected[0])
    cid = text.split(" | ")[0]
    cursor.execute("SELECT * FROM Contact WHERE id = %s", (cid,))
    row = cursor.fetchone()
    if row:
        clear_fields()
        selected_contact_id = row[0]
        name_entry.insert(0, row[1])
        email_entry.insert(0, row[2])
        phone_entry.insert(0, row[3] or "")
        category_combo.set(row[4] or "Faculty")
        notes_text.insert("1.0", row[5] or "")

def add_contact():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    category = category_combo.get()
    notes = notes_text.get("1.0", tk.END).strip()

    if not name or not email:
        messagebox.showerror("Error", "Name and Email are required!")
        return

    if not validate_email(email):
        messagebox.showerror("Error", "Invalid email format! Example: asha@adit.edu")
        return

    # Check for duplicate email
    cursor.execute("SELECT id FROM Contact WHERE email = %s", (email,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Email already exists! Duplicate emails are not allowed.")
        return

    cursor.execute(
        "INSERT INTO Contact (name, email, phone, category, notes) VALUES (%s, %s, %s, %s, %s)",
        (name, email, phone, category, notes)
    )
    conn.commit()
    messagebox.showinfo("Success", "Contact added successfully!")
    clear_fields()
    load_contacts()

def update_contact():
    global selected_contact_id
    if selected_contact_id is None:
        messagebox.showwarning("Warning", "Select a contact from the list first!")
        return

    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    category = category_combo.get()
    notes = notes_text.get("1.0", tk.END).strip()

    if not name or not email:
        messagebox.showerror("Error", "Name and Email are required!")
        return

    if not validate_email(email):
        messagebox.showerror("Error", "Invalid email format!")
        return

    # Check duplicate email excluding current contact
    cursor.execute("SELECT id FROM Contact WHERE email = %s AND id != %s", (email, selected_contact_id))
    if cursor.fetchone():
        messagebox.showerror("Error", "Email already used by another contact!")
        return

    cursor.execute(
        "UPDATE Contact SET name=%s, email=%s, phone=%s, category=%s, notes=%s WHERE id=%s",
        (name, email, phone, category, notes, selected_contact_id)
    )
    conn.commit()
    messagebox.showinfo("Success", "Contact updated successfully!")
    clear_fields()
    load_contacts()

def delete_contact():
    global selected_contact_id
    if selected_contact_id is None:
        messagebox.showwarning("Warning", "Select a contact to delete!")
        return

    if messagebox.askyesno("Confirm", "Are you sure you want to delete this contact?"):
        cursor.execute("DELETE FROM Contact WHERE id = %s", (selected_contact_id,))
        conn.commit()
        messagebox.showinfo("Success", "Contact deleted successfully!")
        clear_fields()
        load_contacts()

def search_contact():
    query = search_entry.get().strip()
    order_col = sort_by_combo.get()
    order_dir = sort_order_var.get()
    sql = f"""
    SELECT * FROM Contact 
    WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s 
    ORDER BY {order_col} {order_dir}
    """
    param = f"%{query}%"
    cursor.execute(sql, (param, param, param))
    rows = cursor.fetchall()
    load_contacts(rows)

root = tk.Tk()
root.title("Contact Manager (Q5)")
root.geometry("750x550")

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Clear", command=clear_fields)
file_menu.add_command(label="Exit", command=root.destroy)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=5)

tk.Label(top_frame, text="Search:").pack(side="left")
search_entry = tk.Entry(top_frame, width=20)
search_entry.pack(side="left", padx=5)

tk.Button(top_frame, text="Search", command=search_contact).pack(side="left", padx=2)
tk.Button(top_frame, text="Reset", command=lambda: [search_entry.delete(0, tk.END), load_contacts()]).pack(side="left", padx=2)

tk.Label(top_frame, text="Sort by:").pack(side="left", padx=(15, 2))
sort_by_combo = ttk.Combobox(top_frame, values=["name", "email", "phone", "category"], state="readonly", width=10)
sort_by_combo.set("name")
sort_by_combo.pack(side="left")

sort_order_var = tk.StringVar(value="ASC")
tk.Radiobutton(top_frame, text="ASC", variable=sort_order_var, value="ASC", command=load_contacts).pack(side="left", padx=2)
tk.Radiobutton(top_frame, text="DESC", variable=sort_order_var, value="DESC", command=load_contacts).pack(side="left", padx=2)

mid_frame = tk.Frame(root)
mid_frame.pack(fill="both", expand=True, padx=10, pady=5)

form_frame = tk.LabelFrame(mid_frame, text="Contact Details")
form_frame.pack(side="left", fill="both", padx=(0, 10))

tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
name_entry = tk.Entry(form_frame, width=25)
name_entry.grid(row=0, column=1, padx=5, pady=3)

tk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
email_entry = tk.Entry(form_frame, width=25)
email_entry.grid(row=1, column=1, padx=5, pady=3)

tk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
phone_entry = tk.Entry(form_frame, width=25)
phone_entry.grid(row=2, column=1, padx=5, pady=3)

category_combo = ttk.Combobox(form_frame, values=["Faculty", "Student", "Staff", "Other"], state="readonly", width=22)
category_combo.set("Faculty")
category_combo.grid(row=3, column=1, padx=5, pady=3)
tk.Label(form_frame, text="Notes:").grid(row=4, column=0, sticky="nw", padx=5, pady=3)
notes_text = tk.Text(form_frame, width=25, height=5)
notes_text.grid(row=4, column=1, padx=5, pady=3)

btn_frame = tk.Frame(form_frame)
btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

tk.Button(btn_frame, text="Add", command=add_contact, width=7).pack(side="left", padx=2)
tk.Button(btn_frame, text="Update", command=update_contact, width=7).pack(side="left", padx=2)
tk.Button(btn_frame, text="Delete", command=delete_contact, width=7).pack(side="left", padx=2)
tk.Button(btn_frame, text="Clear", command=clear_fields, width=7).pack(side="left", padx=2)

list_frame = tk.LabelFrame(mid_frame, text="Contacts List (ID | Name | Email | Phone | Category)")
list_frame.pack(side="right", fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
listbox.pack(fill="both", expand=True)
scrollbar.config(command=listbox.yview)
listbox.bind("<<ListboxSelect>>", on_select)

load_contacts()

root.mainloop()
conn.close()
