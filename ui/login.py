import sys
import os
import customtkinter as ctk
from tkinter import messagebox

# =====================================================
# ACCESS SRC
# =====================================================

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import (
    login,
    register_user,
    send_otp,
    verify_otp_and_reset,
    view_employees,
    assign_manager
)
from dashboard import Dashboard
from database import debug_requirements


# =====================================================
# THEME
# =====================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Staffing CRM")
app.geometry("450x560")
app.resizable(False, False)

# =====================================================
# HEADING
# =====================================================

ctk.CTkLabel(
    app,
    text="STAFFING CRM",
    font=("Arial", 28, "bold")
).pack(pady=35)

ctk.CTkLabel(
    app,
    text="Login to continue",
    font=("Arial", 14)
).pack()

email = ctk.CTkEntry(
    app,
    width=280,
    placeholder_text="Official Email"
)
email.pack(pady=15)

password = ctk.CTkEntry(
    app,
    width=280,
    placeholder_text="Password",
    show="*"
)
password.pack()

message = ctk.CTkLabel(app, text="")
message.pack(pady=8)

# =====================================================
# LOGIN
# =====================================================

def authenticate():

    user = login(
        email.get().strip().lower(),
        password.get()
    )

    if user:
        app.destroy()
        Dashboard(user)
    else:
        message.configure(
            text="Invalid Email or Password",
            text_color="red"
        )
ctk.CTkButton(
app,
text="Login",
width=280,
command=authenticate
).pack(pady=15)


debug_requirements()

# =====================================================
# SIGN UP
# =====================================================

def signup():

    win = ctk.CTkToplevel(app)
    win.title("Create Recruiter")
    win.geometry("380x420")
    win.grab_set()

    ctk.CTkLabel(
        win,
        text="Create Recruiter",
        font=("Arial", 22, "bold")
    ).pack(pady=20)

    emp = ctk.CTkEntry(
    win,
    placeholder_text="User ID (REC201)"
    )
    emp.pack(fill="x", padx=25, pady=8)

    name = ctk.CTkEntry(
        win,
        placeholder_text="Full Name"
    )
    name.pack(fill="x", padx=25, pady=8)
    
    email_entry = ctk.CTkEntry(
        win,
        placeholder_text="Official Email"
    )
    email_entry.pack(fill="x", padx=25, pady=8)

    pwd = ctk.CTkEntry(
        win,
        placeholder_text="Password",
        show="*"
    )
    pwd.pack(fill="x", padx=25, pady=8)

    role = ctk.CTkComboBox(
        win,
        values=["Recruiter", "Head"]
    )
    role.pack(fill="x", padx=25, pady=8)
    role.set("Recruiter")

    def create():

        if not emp.get() or not name.get() or not email_entry.get() or not pwd.get():
            messagebox.showerror(
                "Error",
                "All fields are required"
            )
            return

        emp_id = emp.get().strip().upper()

        if not emp_id.isalnum():
            messagebox.showerror(
                "Invalid User ID",
                "User ID must be alphanumeric (Example: REC201 or EMP101)."
            )
            return
        

        result = register_user(
            emp_id,
            name.get().strip(),
            email_entry.get().strip(),
            pwd.get(),
            role.get()
        )

        if result == "success":

            messagebox.showinfo(
            "Success",
            f"Account Created Successfully!\n\nOfficial Email:\n{email_entry.get().strip()}"
            )
            win.destroy()

        elif result == "weak":
            messagebox.showerror(
                "Weak Password",
                "Password must contain:\n\n"
                "• Minimum 8 characters\n"
                "• One Uppercase\n"
                "• One Lowercase\n"
                "• One Number\n"
                "• One Special Character"
            )
            
        elif result == "email_exists":
           messagebox.showerror(
            "Duplicate Email",
            "This official email is already registered."
    )    

        else:
            messagebox.showerror(
                "Duplicate",
                "Employee ID already exists."
            )

    ctk.CTkButton(
        win,
        text="Create Account",
        command=create
    ).pack(fill="x", padx=25, pady=25)

# =====================================================
# FORGOT PASSWORD
# =====================================================

def forgot_password():

    win = ctk.CTkToplevel(app)
    win.title("Forgot Password")
    win.geometry("380x440")
    win.grab_set()

    ctk.CTkLabel(
        win,
        text="Reset Password",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    mail = ctk.CTkEntry(
        win,
        placeholder_text="Official Email"
    )
    mail.pack(fill="x", padx=25, pady=8)

    otp = ctk.CTkEntry(
        win,
        placeholder_text="Enter 6-digit OTP"
    )
    otp.pack(fill="x", padx=25, pady=8)

    new_pwd = ctk.CTkEntry(
        win,
        placeholder_text="New Password",
        show="*"
    )
    new_pwd.pack(fill="x", padx=25, pady=8)

    timer_label = ctk.CTkLabel(
        win,
        text="",
        text_color="red"
    )
    timer_label.pack(pady=5)

    time_left = 60

    def countdown():
        nonlocal time_left

        if time_left > 0:
            timer_label.configure(
                text=f"OTP expires in {time_left} sec"
            )
            time_left -= 1
            win.after(1000, countdown)
        else:
            timer_label.configure(text="OTP Expired")

    def send():
        nonlocal time_left

        result = send_otp(mail.get().strip())

        if result is True:
            time_left = 60
            countdown()

            messagebox.showinfo(
                "OTP Sent",
                "A 6-digit OTP has been sent to your registered email."
            )
        elif result is False:
            messagebox.showerror(
                "Error",
                "This email is not registered."
            )
        else:
            messagebox.showerror(
                "SMTP Error",
                str(result)
            )

    def reset():

        result = verify_otp_and_reset(
            mail.get().strip(),
            otp.get().strip(),
            new_pwd.get()
        )

        if result == "success":
            messagebox.showinfo(
                "Success",
                "Password reset successfully."
            )
            win.destroy()

        elif result == "weak":
            messagebox.showerror(
                "Weak Password",
                "Password must contain uppercase, lowercase, number and special character."
            )

        elif result == "expired":
            messagebox.showerror(
                "OTP Expired",
                "Please generate a new OTP."
            )

        else:
            messagebox.showerror(
                "Invalid OTP",
                "Incorrect OTP."
            )

            ctk.CTkButton(
                win,
                text="Send OTP",
                command=send
            ).pack(fill="x", padx=25, pady=(15,8))

            ctk.CTkButton(
                win,
                text="Reset Password",
                fg_color="#16A34A",
                command=reset
            ).pack(fill="x", padx=25)

# =====================================================
# BOTTOM BUTTONS
# =====================================================

ctk.CTkButton(
    app,
    text="Sign Up",
    width=280,
    fg_color="transparent",
    border_width=1,
    text_color="#2563EB",
    command=signup
).pack(pady=(5, 8))

ctk.CTkButton(
    app,
    text="Forgot Password?",
    width=280,
    fg_color="transparent",
    text_color="gray40",
    hover=False,
    command=forgot_password
).pack()

# =====================================================
# RUN
# =====================================================

app.mainloop()