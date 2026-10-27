import re
import tkinter as tk

def validate_enrollment(enrollment: str) -> bool:
    pattern = r"^\d{10}$"               #to validate enrollment
    return bool(re.fullmatch(pattern, enrollment.strip()))


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@adit\.ac\.in$"               #for college email ending with @adit.ac.in
    return bool(re.fullmatch(pattern, email.strip(), re.IGNORECASE))


def show_alert(title: str, message: str, is_success: bool = False):
    alert = tk.Toplevel(root)
    alert.title(title)
    alert.geometry("550x300")
    alert.resizable(False, False)
    alert.configure(bg="#FFFFFF")
    alert.transient(root)
    alert.grab_set()

    header_bg = "#2E7D32" if is_success else "#D32F2F"
    header_title = "Validation Passed" if is_success else "Validation Failed"

    banner = tk.Label(
        alert,
        text=header_title,
        font=("Segoe UI", 15, "bold"),
        fg="#FFFFFF",
        bg=header_bg,
        pady=10,
    )
    banner.pack(fill=tk.X, side=tk.TOP)

    content_box = tk.Frame(
        alert,
        bg="#FFFFFF",
        highlightbackground="#000000",
        highlightthickness=1,
        padx=15,
        pady=12,
    )
    content_box.pack(padx=24, pady=(18, 14), fill=tk.BOTH, expand=True)

    tk.Label(
        content_box,
        text=message,
        font=("Segoe UI", 13, "bold"),
        fg="#222222",
        bg="#FFFFFF",
        justify=tk.LEFT,
        anchor="w",
    ).pack(fill=tk.BOTH, expand=True)

    btn_ok = tk.Button(
        alert,
        text="OK",
        font=("Segoe UI", 13, "bold"),
        bg="#1976D2",
        fg="white",
        activebackground="#1565C0",
        activeforeground="white",
        relief=tk.FLAT,
        width=20, 
        pady=4,
        cursor="hand2",
        command=alert.destroy,
    )
    btn_ok.pack(side=tk.BOTTOM, pady=(0, 16))

def handle_validation():
    # Clear previous error labels
    lbl_err_user.config(text="")
    lbl_err_email.config(text="")

    enrollment_input = entry_enrollment.get().strip()
    email_input = entry_email.get().strip()

    errors = []

    # Enrollment validation
    if not enrollment_input:
        err = "- Enter Enrollment number."
        lbl_err_user.config(text=err)
        errors.append(err)
    elif not validate_enrollment(enrollment_input):
        err = "- Invalid Enrollment Number: Must be 10 digits."
        lbl_err_user.config(text=err)
        errors.append(err)

    # Email validation
    if not email_input:
        err = "- Enter College Email."
        lbl_err_email.config(text=err)
        errors.append(err)
    elif not validate_email(email_input):
        err = "- Invalid College Email: Must end with '@adit.ac.in'."
        lbl_err_email.config(text=err)
        errors.append(err)

    if errors:
        show_alert("Validation Failed", "\n\n".join(errors), is_success=False)
    else:
        show_alert(
            "Success",
            f"Welcome !\n\nUser: {enrollment_input}\nEmail: {email_input}",
            is_success=True,
        )


def clear_fields():
    entry_enrollment.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    lbl_err_user.config(text="")
    lbl_err_email.config(text="")


# --- GUI ---
root = tk.Tk()
root.title("ADIT Student Portal Validation")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg="#87CEEB")

# Header
lbl_header = tk.Label(
    root,
    text="Student Login",
    font=("Times New Roman", 20, "bold"),
    bg="#FFFFFF",
    fg="#1565C0",
)
lbl_header.pack(pady=12)

# Form Container
frame = tk.Frame(root, bg="#FFFFFF", padx=25, pady=25, relief=tk.RIDGE, bd=1)
frame.pack(padx=25, pady=10, fill=tk.BOTH, expand=True)

# Enrollment Input
lbl_enroll = tk.Label(
    frame,
    text="Enter User name: ",
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
)
lbl_enroll.pack(anchor="w", pady=(0, 2))
entry_enrollment = tk.Entry(frame, font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
entry_enrollment.pack(fill=tk.X)

# error text 
lbl_err_user = tk.Label(
    frame,
    text="",
    font=("Segoe UI", 9),
    fg="#D32F2F",
    bg="#FFFFFF",
    anchor="w",
)
lbl_err_user.pack(fill=tk.X, pady=(2, 8))

# Email Input
lbl_mail = tk.Label(
    frame,
    text="Enter College Email: ",
    font=("Segoe UI", 11, "bold"),
    bg="#FFFFFF",
)
lbl_mail.pack(anchor="w", pady=(0, 2))
entry_email = tk.Entry(frame, font=("Segoe UI", 11), relief=tk.SOLID, bd=1)
entry_email.pack(fill=tk.X)

# error text 
lbl_err_email = tk.Label(
    frame,
    text="",
    font=("Segoe UI", 9),
    fg="#D32F2F",
    bg="#FFFFFF",
    anchor="w",
)
lbl_err_email.pack(fill=tk.X, pady=(2, 10))

# Button Row
btn_frame = tk.Frame(frame, bg="#FFFFFF")
btn_frame.pack(side=tk.BOTTOM, pady=(10, 0))

btn_validate = tk.Button(
    btn_frame,
    text="Submit",
    font=("Segoe UI", 10, "bold"),
    bg="#1976D2",
    fg="white",
    activebackground="#1565C0",
    activeforeground="white",
    cursor="hand2",
    relief=tk.FLAT,
    padx=22,
    pady=4,
    command=handle_validation,
)
btn_validate.pack(side=tk.LEFT, padx=6)

btn_clear = tk.Button(
    btn_frame,
    text="Clear",
    font=("Segoe UI", 10),
    bg="#E0E0E0",
    fg="#333333",
    activebackground="#D6D6D6",
    cursor="hand2",
    relief=tk.FLAT,
    padx=22,
    pady=4,
    command=clear_fields,
)
btn_clear.pack(side=tk.LEFT, padx=6)

if __name__ == "__main__":
    root.mainloop()
