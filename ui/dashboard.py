import os
import sys
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import csv
from tkcalendar import DateEntry
import subprocess
from database import view_employees
from tkinter import ttk
from database import employee_details, get_team
from database import my_requirements, create_requirement
from database import requirement_candidates
from database import my_requirements, view_all_requirements, assign_requirement
from database import update_requirement_assignment
from database import assign_candidate_requirement, my_requirement_candidates
from database import employee_requirement_count
from database import add_requirement_history, requirement_history
from database import assigned_candidate_count
from database import close_requirement_if_filled
from database import requirement_progress
from database import requirement_dashboard_stats
from tkinter import filedialog


# =====================================================
# DATABASE
# =====================================================

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import (
    view_candidates,
    my_candidates,
    search_candidate,
    insert_candidate,
    update_candidate_status,
    update_remarks,
    get_resume,
    recruiter_report,
    client_report,
    status_report,
    register_user,
    candidates_by_date,
    delete_candidate,
    view_employees,
    get_team,
    employee_details,
    my_tasks,
    update_task_status,
    get_assignable_employees,
    employee_task_stats,
    team_workload,
    employee_recent_tasks,
    employee_activity,
    get_assignable_employees,
    assign_task,
    create_requirement,
    my_requirements
    )

# =====================================================
# THEME
# =====================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
SIDEBAR = "#0F172A"

BG = "#F4F7FB"
CARD = "#FFFFFF"

TEXT = "#111827"
SUB = "#64748B"

GREEN = "#16A34A"
PURPLE = "#7C3AED"
TEAL = "#0F766E"
ORANGE = "#EA580C"

BORDER = "#E5E7EB"

# =====================================================
# DASHBOARD CLASS
# =====================================================

class Dashboard:

    def __init__(self, user):

        self.user = user
        self.emp_id = user[0]
        self.user_name = user[1]
        self.role = user[2]
        self.view_emp_id = self.emp_id
        self.view_role = self.role

        self.selected_resume = ""

        self.app = ctk.CTk()
        self.app.title("IBOTIX Staffing Operations CRM")
        self.app.geometry("1450x850")
        self.app.configure(fg_color=BG)

        self.main = ctk.CTkFrame(
        self.app,
        fg_color=BG
        )
        self.main.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.build_sidebar()
        self.show_dashboard()
        self.app.mainloop()
     
    def show_settings(self):

        self.clear_main()
        self.highlight_menu("Settings")

        ctk.CTkLabel(
            self.main,
            text="Settings",
            font=("Segoe UI",28,"bold")
        ).pack(pady=30)

        ctk.CTkLabel(
            self.main,
            text=f"Logged in as: {self.user_name} ({self.role})",
            font=("Segoe UI",14)
        ).pack()

        if self.role.lower() == "head":
            ctk.CTkButton(
                self.main,
                text="Create Recruiter",
                fg_color=GREEN,
                command=self.create_recruiter
            ).pack(pady=20)
     
    def download_report(self):

        if self.role.lower() != "head":
            return

        win = ctk.CTkToplevel(self.app)
        win.title("Download Candidate Report")
        win.geometry("380x260")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Download Date-wise Data",
            font=("Segoe UI",18,"bold")
        ).pack(pady=15)

        ctk.CTkLabel(win, text="Start Date").pack(anchor="w", padx=25)

        start = DateEntry(
            win,
            width=22,
            date_pattern="yyyy-mm-dd",
            background="#2563EB",
            foreground="white"
        )
        start.pack(fill="x", padx=25)

        ctk.CTkLabel(win, text="End Date").pack(anchor="w", padx=25, pady=(10,0))

        end = DateEntry(
            win,
            width=22,
            date_pattern="yyyy-mm-dd",
            background="#2563EB",
            foreground="white"
        )
        end.pack(fill="x", padx=25)

        def export():

            rows = candidates_by_date(
            start.get_date().strftime("%Y-%m-%d"),
            end.get_date().strftime("%Y-%m-%d")
)

            if not rows:
                messagebox.showinfo("Empty","No records found.")
                return

            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV File","*.csv")],
                initialfile=f"Candidates_{start.get_date()}_{end.get_date()}.csv"
            )

            if not path:
                return

            with open(path,"w",newline="",encoding="utf-8") as f:
                writer = csv.writer(f)

                writer.writerow([
                    "ID","Name","Mobile","Email",
                    "Skill","Experience","Client",
                    "Status","Remarks","Created Date"
                ])

                writer.writerows(rows)

            messagebox.showinfo("Success","CSV exported successfully.")
            win.destroy()

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=25)

        ctk.CTkButton(
            btn_row,
            text="CSV",
            fg_color="#2563EB",
            width=140,
            command=lambda: export("csv")
        ).pack(side="left", padx=(0,10))

        ctk.CTkButton(
            btn_row,
            text="Excel",
            fg_color="#16A34A",
            width=140,
            command=lambda: export("excel")
        ).pack(side="left")
    
    
    def create_recruiter(self):

        win = ctk.CTkToplevel(self.app)
        win.title("Create Recruiter")
        win.geometry("420x460")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Create Recruiter",
            font=("Segoe UI",22,"bold")
        ).pack(pady=20)

        def field(label, show=""):

            ctk.CTkLabel(
                win,
                text=label,
                font=("Segoe UI",12,"bold")
            ).pack(anchor="w", padx=30, pady=(8,2))

            e = ctk.CTkEntry(
                win,
                height=38,
                show=show
            )
            e.pack(fill="x", padx=30)

            return e

        emp = field("Employee ID")
        name = field("Recruiter Name")
        password = field("Password", show="*")

        ctk.CTkLabel(
            win,
            text="Minimum 8 characters • Uppercase • Lowercase • Number • Special character",
            text_color=SUB,
            font=("Segoe UI",10),
            wraplength=340,
            justify="left"
        ).pack(anchor="w", padx=30, pady=(4,10))

        ctk.CTkLabel(
            win,
            text="Role",
            font=("Segoe UI",12,"bold")
        ).pack(anchor="w", padx=30)

        role = ctk.CTkComboBox(
            win,
            values=["Recruiter","Head"]
        )
        role.pack(fill="x", padx=30)
        role.set("Recruiter")

        def create():

            if emp.get()=="" or name.get()=="" or password.get()=="":

                messagebox.showerror(
                    "Required",
                    "All fields are mandatory."
                )
                return

            try:
                emp_id = int(emp.get())
            except:
                messagebox.showerror(
                    "Invalid",
                    "Employee ID must be numeric."
                )
                return

            result = register_user(
                emp_id,
                name.get().strip(),
                password.get(),
                role.get()
            )

            if result == "success":

                messagebox.showinfo(
                    "Success",
                    "Recruiter account created successfully."
                )

                win.destroy()

            elif result == "weak":

                messagebox.showerror(
                    "Weak Password",
                    "Password must contain:\n\n"
                    "• Minimum 8 characters\n"
                    "• One uppercase letter\n"
                    "• One lowercase letter\n"
                    "• One number\n"
                    "• One special character"
                )
                

            else:

                messagebox.showerror(
                    "Duplicate",
                    "Employee ID already exists."
                )

        ctk.CTkButton(
            win,
            text="Create Account",
            height=42,
            fg_color=GREEN,
            hover_color="#15803D",
            command=create
        ).pack(fill="x", padx=30, pady=28)
        
    def show_reports(self):

        if self.role.lower() != "head":
            messagebox.showwarning("Access Denied","Only Head can access reports.")
            return

        self.clear_main()
        self.highlight_menu("Reports")

        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20,10))

        ctk.CTkLabel(
            top,
            text="Executive Reports",
            font=("Segoe UI",28,"bold")
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="⬇ Download Data",
            fg_color=GREEN,
            command=self.download_report
        ).pack(side="right")

        body = ctk.CTkFrame(self.main, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25)

        left = ctk.CTkFrame(body, fg_color=CARD, corner_radius=14)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        ctk.CTkLabel(left,text="Recruiter Productivity",
            font=("Segoe UI",18,"bold")).pack(anchor="w", padx=15, pady=12)

        for name,count in recruiter_report():
            r = ctk.CTkFrame(left, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=5)

            ctk.CTkLabel(r,text=name).pack(side="left")
            ctk.CTkLabel(
                r,
                text=f"{count} Candidates",
                text_color=PRIMARY,
                font=("Segoe UI",12,"bold")
            ).pack(side="right")

        right = ctk.CTkFrame(body, fg_color=CARD, corner_radius=14)
        right.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(right,text="Client Distribution",
            font=("Segoe UI",18,"bold")).pack(anchor="w", padx=15, pady=12)

        for client,count in client_report():
            r = ctk.CTkFrame(right, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=5)

            ctk.CTkLabel(r,text=client).pack(side="left")
            ctk.CTkLabel(
                r,
                text=str(count),
                text_color=PURPLE,
                font=("Segoe UI",12,"bold")
            ).pack(side="right")

        bottom = ctk.CTkFrame(self.main, fg_color=CARD, corner_radius=14)
        bottom.pack(fill="x", padx=25, pady=15)

        ctk.CTkLabel(bottom,text="Status Summary",
            font=("Segoe UI",18,"bold")).pack(anchor="w", padx=15, pady=12)

        for status,count in status_report():
            r = ctk.CTkFrame(bottom, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=4)

            ctk.CTkLabel(r,text=status).pack(side="left")
            ctk.CTkLabel(
                r,
                text=str(count),
                text_color=TEAL,
                font=("Segoe UI",12,"bold")
            ).pack(side="right")    

    # =====================================================
    # CANDIDATES PAGE
    # =====================================================

    def show_candidates(self):

        self.clear_main()
        self.highlight_menu("Candidates")

        self.build_toolbar()
        self.build_table()
        self.load_candidates()
        
    
    def show_tasks(self):

        self.clear_main()
        self.highlight_menu("My Tasks")

        ctk.CTkLabel(
            self.main,
            text="My Assigned Tasks",
            font=("Segoe UI",28,"bold")
        ).pack(anchor="w", padx=25, pady=20)

        tasks = my_tasks(self.emp_id)

        if not tasks:
            ctk.CTkLabel(
                self.main,
                text="No tasks assigned yet.",
                text_color="gray"
            ).pack(pady=30)
            return

        for t in tasks:

            card = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
            card.pack(fill="x", padx=25, pady=8)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10,5))

            ctk.CTkLabel(
                top,
                text=t[1],
                font=("Segoe UI",16,"bold")
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=t[5],
                text_color="red"
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=f"{t[2]} • {t[3]}",
                text_color="gray"
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card,
                text=f"Assigned by : {t[4]}",
                text_color="#2563EB"
            ).pack(anchor="w", padx=15)

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=15, pady=10)

            status = ctk.CTkComboBox(
                bottom,
                values=[
                    "Assigned",
                    "In Progress",
                    "Completed",
                    "On Hold"
                ],
                width=150
            )

            status.set(t[7])
            status.pack(side="left")

            ctk.CTkButton(
                bottom,
                text="Update",
                width=90,
                fg_color="#16A34A",
                command=lambda task=t[0], s=status: (
                    update_task_status(task, s.get()),
                    self.show_tasks()
                )
            ).pack(side="right")
            
            
            ctk.CTkButton(
                bottom,
                text="Open",
                width=80,
                fg_color="#7C3AED",
                command=lambda task=t: self.open_task_candidate(task[0])
            ).pack(side="right", padx=8)
            
            
    def show_requirements(self):

        self.clear_main()
        self.highlight_menu("Requirements")

        # ================= HEADER =================
        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(
            top,
            text="Requirements Dashboard",
            font=("Segoe UI", 28, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="+ New Requirement",
            fg_color="#2563EB",
            command=self.create_requirement_popup
        ).pack(side="right")

        # ================= STATS =================
        total, open_req, candidates, closed = requirement_dashboard_stats(
            self.emp_id,
            self.role
        )

        stats = ctk.CTkFrame(self.main, fg_color="transparent")
        stats.pack(fill="x", padx=25, pady=(0,15))

        def metric(parent, title, value, color):
            box = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
            box.pack(side="left", expand=True, fill="x", padx=5)

            ctk.CTkLabel(
                box,
                text=title,
                text_color="gray"
            ).pack(anchor="w", padx=12, pady=(10,0))

            ctk.CTkLabel(
                box,
                text=str(value),
                font=("Segoe UI",22,"bold"),
                text_color=color
            ).pack(anchor="w", padx=12, pady=(0,10))

        metric(stats, "Requirements", total, "#2563EB")
        metric(stats, "Open", open_req, "#16A34A")
        metric(stats, "Candidates", candidates, "#7C3AED")
        metric(stats, "Closed", closed, "#EA580C")
        

        # Data
        if self.role == "Head":
            rows = view_all_requirements()
        else:
            rows = my_requirements(self.emp_id)

        if not rows:
            ctk.CTkLabel(
                self.main,
                text="No requirements assigned.",
                text_color="gray"
            ).pack(pady=40)
            return

        body = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25)

        for r in rows:

            card = ctk.CTkFrame(
                body,
                fg_color="white",
                corner_radius=12
            )
            card.pack(fill="x", pady=8)

            # Click whole card
            card.bind(
                "<Button-1>",
                lambda e, req=r: self.open_requirement(req)
            )

            # Left
            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=15, pady=12)

            title = ctk.CTkLabel(
                left,
                text=r[2],
                font=("Segoe UI",16,"bold")
            )
            title.pack(anchor="w")
            title.bind("<Button-1>", lambda e, req=r: self.open_requirement(req))

            client = ctk.CTkLabel(
                left,
                text=f"Client : {r[1]}",
                text_color="#2563EB"
            )
            client.pack(anchor="w")
            client.bind("<Button-1>", lambda e, req=r: self.open_requirement(req))

            # Assigned employee
            emp = employee_details(r[11])
            assigned_to = emp[1] if emp else "Unassigned"

            assigned = ctk.CTkLabel(
                left,
                text=f"Assigned To : {assigned_to}",
                text_color="#0F766E",
                font=("Segoe UI",11,"bold")
            )
            assigned.pack(anchor="w")
            assigned.bind("<Button-1>", lambda e, req=r: self.open_requirement(req))

            # JD indicator
            if r[10]:
                jd = ctk.CTkLabel(
                    left,
                    text="📄 JD Attached",
                    text_color="#2563EB",
                    font=("Segoe UI", 10, "bold")
                )
                jd.pack(anchor="w")
                jd.bind("<Button-1>", lambda e, req=r: self.open_requirement(req))

            skills = ctk.CTkLabel(
                left,
                text=f"Skills : {r[3]}",
                text_color="gray"
            )
            skills.pack(anchor="w")
            skills.bind("<Button-1>", lambda e, req=r: self.open_requirement(req))
            skills.pack(anchor="w")

            budget = ctk.CTkLabel(
                left,
                text=f"Budget : {r[6]} | Openings : {r[5]}",
                text_color="#7C3AED"
            )
            budget.pack(anchor="w")
            budget.bind("<Button-1>", lambda e, req=r: self.open_requirement(req))
            
            candidate_count = len(requirement_candidates(r[0]))

            # Right
            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=15, pady=12)

            ctk.CTkLabel(
                right,
                text=f"{candidate_count} Candidates",
                text_color="#2563EB",
                font=("Segoe UI",11,"bold")
            ).pack(anchor="e")

            ctk.CTkLabel(
                right,
                text=r[13],
                text_color="#16A34A",
                font=("Segoe UI",11,"bold")
            ).pack(anchor="e")

            ctk.CTkLabel(
                right,
                text=r[14],
                text_color="gray",
                font=("Segoe UI",10)
            ).pack(anchor="e")

            ctk.CTkButton(
                right,
                text="Open",
                width=80,
                fg_color="#2563EB",
                command=lambda req=r: self.open_requirement(req)
            ).pack(anchor="e", pady=(8,0))
    
    # def open_requirement(self, req):

    #     win = ctk.CTkToplevel(self.app)
    #     win.title("Requirement Details")
    #     win.geometry("650x600")
    #     win.grab_set()

    #     ctk.CTkLabel(
    #         win,
    #         text=req[2],
    #         font=("Segoe UI",24,"bold")
    #     ).pack(pady=15)

    #     body = ctk.CTkFrame(win, fg_color="white")
    #     body.pack(fill="both", expand=True, padx=20, pady=10)

    #     def row(title, value):
    #         r = ctk.CTkFrame(body, fg_color="transparent")
    #         r.pack(fill="x", padx=15, pady=6)

    #         ctk.CTkLabel(
    #             r,
    #             text=title,
    #             width=140,
    #             anchor="w",
    #             text_color="gray"
    #         ).pack(side="left")

    #         ctk.CTkLabel(
    #             r,
    #             text=str(value),
    #             font=("Segoe UI",12,"bold")
    #         ).pack(side="left")

    #     row("Client", req[1])
    #     row("Requirement", req[2])
    #     row("Skills", req[3])
    #     row("Experience", req[4])
    #     row("Openings", req[5])
    #     row("Budget", req[6])
    #     row("Location", req[7])
    #     row("Priority", req[8])
    #     row("Assigned To", req[11])
    #     row("Assigned On", req[14])

    #     ctk.CTkLabel(
    #         body,
    #         text="Description",
    #         font=("Segoe UI",13,"bold")
    #     ).pack(anchor="w", padx=15, pady=(12,4))

    #     box = ctk.CTkTextbox(body, height=110)
    #     box.pack(fill="x", padx=15)
    #     box.insert("1.0", req[9])
    #     box.configure(state="disabled")

    #     ctk.CTkButton(
    #         win,
    #         text="Assign Candidate",
    #         fg_color="#2563EB",
    #         height=42,
    #         command=lambda:[
    #             win.destroy(),
    #             self.open_requirement_candidates(req)
    #         ]
    #     ).pack(fill="x", padx=20, pady=15)
    
    
            
    def create_requirement_popup(self):

        team = get_assignable_employees(self.emp_id, self.role)

        if not team:
            messagebox.showwarning("Team", "No assignable employees found.")
            return

        win = ctk.CTkToplevel(self.app)
        win.title("Create Requirement")
        win.geometry("520x700")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="New Client Requirement",
            font=("Segoe UI",22,"bold")
        ).pack(pady=15)

        form = ctk.CTkScrollableFrame(win)
        form.pack(fill="both", expand=True, padx=20)

        def field(label):
            ctk.CTkLabel(form, text=label).pack(anchor="w", pady=(8,2))
            e = ctk.CTkEntry(form, height=35)
            e.pack(fill="x")
            return e

        client = field("Client Name")
        title = field("Requirement Title")
        skills = field("Required Skills")
        exp = field("Experience")
        openings = field("Openings")
        budget = field("Budget")
        location = field("Location")

        ctk.CTkLabel(form, text="Priority").pack(anchor="w", pady=(8,2))
        priority = ctk.CTkComboBox(
            form,
            values=["High","Medium","Low"]
        )
        priority.pack(fill="x")
        priority.set("Medium")

        ctk.CTkLabel(form, text="Requirement Description").pack(anchor="w", pady=(8,2))
        desc = ctk.CTkTextbox(form, height=90)
        desc.pack(fill="x")
        
        
        # ================= JD UPLOAD =================
        jd_path = ctk.StringVar(value="No JD selected")

        ctk.CTkLabel(
            form,
            text="Upload JD (Optional)"
        ).pack(anchor="w", padx=15, pady=(10,5))

        jd_frame = ctk.CTkFrame(form, fg_color="white")
        jd_frame.pack(fill="x", padx=15)

        ctk.CTkLabel(
            jd_frame,
            textvariable=jd_path,
            anchor="w",
            text_color="gray"
        ).pack(side="left", padx=10, pady=10, expand=True, fill="x")

        def browse_jd():
            file = filedialog.askopenfilename(
                title="Select Job Description",
                filetypes=[
                    ("Documents", "*.pdf *.doc *.docx"),
                    ("PDF", "*.pdf"),
                    ("Word", "*.doc *.docx")
                ]
            )
            if file:
                jd_path.set(file)

        ctk.CTkButton(
            jd_frame,
            text="Browse",
            width=90,
            fg_color="#2563EB",
            command=browse_jd
        ).pack(side="right", padx=8, pady=8)

        # Assign To
        ctk.CTkLabel(form, text="Assign To").pack(anchor="w", pady=(8,2))

        members = [f"{m[1]} ({m[2]})" for m in team]

        assign_box = ctk.CTkComboBox(form, values=members)
        assign_box.pack(fill="x")
        assign_box.set(members[0])

        def save():

            if client.get() == "" or title.get() == "":
                messagebox.showerror(
                    "Required",
                    "Client and Requirement Title are required."
                )
                return

            try:
                total_openings = int(openings.get())
            except:
                messagebox.showerror(
                    "Invalid",
                    "Openings must be a number."
                )
                return

            # Selected employee
            index = members.index(assign_box.get())
            employee = team[index]

            create_requirement(
                client.get(),
                title.get(),
                skills.get(),
                exp.get(),
                total_openings,
                budget.get(),
                location.get(),
                priority.get(),
                desc.get("1.0", "end").strip(),
                self.emp_id,      # Head
                employee[0],      # AM201
                employee[2],
                jd_path.get() # Account Manager
            )

            messagebox.showinfo(
                "Success",
                f"Requirement assigned to {employee[1]} successfully!"
            )

            win.destroy()
            self.show_requirements()   
            
        # Bottom Action Button
        ctk.CTkButton(
            win,
            text="Create Requirement",
            height=45,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=save
        ).pack(fill="x", padx=20, pady=15)
    
    def open_requirement(self, req):

        self.clear_main()
        self.highlight_menu("Requirements")

        # ================= HEADER =================
        header = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            header,
            text="← Back",
            width=80,
            fg_color="#64748B",
            command=self.show_requirements
        ).pack(anchor="nw", padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text=req[2],
            font=("Segoe UI",24,"bold")
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            header,
            text=f"Client : {req[1]}",
            text_color="#2563EB",
            font=("Segoe UI",12,"bold")
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            header,
            text=f"Skills : {req[3]}",
            text_color="gray"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            header,
            text=f"Experience : {req[4]}",
            text_color="gray"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            header,
            text=f"Budget : {req[6]}   |   Openings : {req[5]}",
            font=("Segoe UI",13,"bold")
        ).pack(anchor="w", padx=15, pady=(0,10))

        # ================= ASSIGNMENT INFO =================
        emp = employee_details(req[12])
        creator = employee_details(req[11])

        assigned_name = emp[1] if emp else req[12]
        created_name = creator[1] if creator else req[11]

        info = ctk.CTkFrame(header, fg_color="#F8FAFC", corner_radius=10)
        info.pack(fill="x", padx=15, pady=(0,15))

        ctk.CTkLabel(
            info,
            text=f"Assigned To : {assigned_name} ({req[13]})",
            text_color="#0F766E",
            font=("Segoe UI",12,"bold")
        ).pack(anchor="w", padx=12, pady=(10,2))

        ctk.CTkLabel(
            info,
            text=f"Assigned By : {created_name}",
            text_color="#64748B"
        ).pack(anchor="w", padx=12)

        ctk.CTkLabel(
            info,
            text=f"Assigned On : {req[15]}",
            text_color="#64748B"
        ).pack(anchor="w", padx=12)

        ctk.CTkLabel(
            info,
            text=f"Status : {req[14]}",
            text_color="#16A34A",
            font=("Segoe UI",12,"bold")
        ).pack(anchor="w", padx=12, pady=(2,10))
        
        
        assigned, openings = requirement_progress(req[0])

        ctk.CTkLabel(
            self.main,
            text="Hiring Progress",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=25)

        progress_box = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        progress_box.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            progress_box,
            text=f"{assigned} of {openings} positions filled",
            font=("Segoe UI",13,"bold")
        ).pack(anchor="w", padx=15, pady=(12,6))

        progress = ctk.CTkProgressBar(progress_box, progress_color="#16A34A")
        progress.pack(fill="x", padx=15, pady=(0,12))
        progress.set(assigned / openings if openings else 0)
        

        # ================= DESCRIPTION =================
        ctk.CTkLabel(
            self.main,
            text="Requirement Description",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=25)

        desc_box = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        desc_box.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            desc_box,
            text=req[9],
            wraplength=900,
            justify="left"
        ).pack(anchor="w", padx=15, pady=15)
        
        
        # ================= JD FILE =================
        ctk.CTkLabel(
            self.main,
            text="Job Description",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=25, pady=(5,0))

        jd_box = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        jd_box.pack(fill="x", padx=20, pady=(0,10))

        jd_file = req[10]

        if jd_file and os.path.exists(jd_file):

            ctk.CTkButton(
                jd_box,
                text="📄 Open JD",
                fg_color="#2563EB",
                width=140,
                command=lambda: subprocess.Popen(jd_file, shell=True)
            ).pack(anchor="w", padx=15, pady=15)

        else:

            ctk.CTkLabel(
                jd_box,
                text="No JD uploaded",
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=15)
        
        

        # ================= ASSIGNED CANDIDATES =================
        rows = requirement_candidates(req[0])

        ctk.CTkLabel(
            self.main,
            text=f"Assigned Candidates ({len(rows)})",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=20, pady=(10,5))

        table = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        table.pack(fill="both", expand=True, padx=20)

        if not rows:

            ctk.CTkLabel(
                table,
                text="No candidates assigned yet.",
                text_color="gray"
            ).pack(pady=30)

        else:

            for r in rows:

                item = ctk.CTkFrame(table, fg_color="transparent")
                item.pack(fill="x", padx=15, pady=8)

                # Left
                left = ctk.CTkFrame(item, fg_color="transparent")
                left.pack(side="left")

                ctk.CTkLabel(
                    left,
                    text=r[1],
                    font=("Segoe UI",13,"bold")
                ).pack(anchor="w")

                ctk.CTkLabel(
                    left,
                    text=f"{r[2]} • {r[3]} Years",
                    text_color="gray"
                ).pack(anchor="w")

                # Right
                right = ctk.CTkFrame(item, fg_color="transparent")
                right.pack(side="right")

                ctk.CTkLabel(
                    right,
                    text=r[4],
                    text_color="#2563EB",
                    font=("Segoe UI",11,"bold")
                ).pack(anchor="e")

                ctk.CTkLabel(
                    right,
                    text=r[5],
                    text_color="#16A34A"
                ).pack(anchor="e")

                ctk.CTkLabel(
                    right,
                    text=f"By : {r[6]}",
                    text_color="gray",
                    font=("Segoe UI",10)
                ).pack(anchor="e")

                ctk.CTkLabel(
                    right,
                    text=r[7],
                    text_color="#64748B",
                    font=("Segoe UI",10)
                ).pack(anchor="e")
                
        # ================= REQUIREMENT TIMELINE =================
        history = requirement_history(req[0])

        ctk.CTkLabel(
            self.main,
            text="Requirement Timeline",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=20, pady=(15,5))

        timeline = ctk.CTkFrame(
            self.main,
            fg_color="white",
            corner_radius=12
        )
        timeline.pack(fill="x", padx=20, pady=(0,10))

        if not history:

            ctk.CTkLabel(
                timeline,
                text="No assignment history available.",
                text_color="gray"
            ).pack(pady=20)

        else:

            for h in history:

                row = ctk.CTkFrame(
                    timeline,
                    fg_color="transparent"
                )
                row.pack(fill="x", padx=15, pady=8)

                # Blue Dot
                ctk.CTkLabel(
                    row,
                    text="●",
                    text_color="#2563EB",
                    font=("Segoe UI",16)
                ).pack(side="left", padx=(0,12))

                info = ctk.CTkFrame(
                    row,
                    fg_color="transparent"
                )
                info.pack(side="left")

                ctk.CTkLabel(
                    info,
                    text=f"{h[2]}  →  {h[3]}",
                    font=("Segoe UI",12,"bold")
                ).pack(anchor="w")

                ctk.CTkLabel(
                    info,
                    text=f"{h[4]}  →  {h[5]}",
                    text_color="#64748B",
                    font=("Segoe UI",10)
                ).pack(anchor="w")

                ctk.CTkLabel(
                    info,
                    text=h[7],
                    text_color="gray",
                    font=("Segoe UI",10)
                ).pack(anchor="w")        

        # ================= ACTION BUTTONS =================
        btn_row = ctk.CTkFrame(self.main, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=15)

        # Head / AM / Recruiter can reassign the requirement
        if self.role != "Intern" and req[14] == "Open":

            ctk.CTkButton(
                btn_row,
                text="Assign Requirement",
                width=170,
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                command=lambda: self.assign_requirement_popup(req)
            ).pack(side="left")

        # Candidate assignment
        if req[14] == "Open":

            ctk.CTkButton(
                btn_row,
                text="Assign Candidates",
                width=170,
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=lambda: self.open_requirement_candidates(req)
            ).pack(side="right")
            
    def assign_requirement_to_employee(self, emp_id, role):

        reqs = [
            r for r in view_all_requirements()
            if r[13] == "Open"
        ]

        if not reqs:
            messagebox.showinfo(
                "Requirements",
                "No open requirements available."
            )
            return

        win = ctk.CTkToplevel(self.app)
        win.title("Assign Requirement")
        win.geometry("820x550")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Select Requirement",
            font=("Segoe UI",22,"bold")
        ).pack(pady=15)

        tree = ttk.Treeview(
            win,
            columns=("Client","Requirement","Budget","Status"),
            show="headings",
            height=15
        )

        for col in ("Client","Requirement","Budget","Status"):
            tree.heading(col, text=col)

        tree.column("Client", width=150)
        tree.column("Requirement", width=280)
        tree.column("Budget", width=120)
        tree.column("Status", width=100)

        tree.pack(fill="both", expand=True, padx=20, pady=(5,0))

        req_map = {}

        for r in reqs:
            item = tree.insert(
                "",
                "end",
                values=(r[1], r[2], r[6], r[13])
            )
            req_map[item] = r

        def assign():

            if not tree.selection():
                messagebox.showwarning("Select", "Please select a requirement.")
                return

            req = req_map[tree.selection()[0]]

            update_requirement_assignment(
                req[0],
                emp_id,
                role
            )

            messagebox.showinfo(
                "Success",
                f"{req[2]} assigned successfully."
            )

            win.destroy()

            updated_emp = employee_details(emp_id)
            self.app.after(
                100,
                lambda: self.show_team_dashboard(updated_emp)
)
        # Bottom Action Bar
        bottom = ctk.CTkFrame(win, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(
            bottom,
            text="Cancel",
            width=100,
            fg_color="#64748B",
            hover_color="#475569",
            command=win.destroy
        ).pack(side="left")

        ctk.CTkButton(
            bottom,
            text="Assign Requirement",
            width=180,
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=assign
        ).pack(side="right")
    
    def open_requirement_candidates(self, req):

        candidates = view_candidates()

        win = ctk.CTkToplevel(self.app)
        win.title("Assign Candidate")
        win.geometry("850x620")
        win.grab_set()

        # Header
        ctk.CTkLabel(
            win,
            text=req[2],
            font=("Segoe UI",22,"bold")
        ).pack(pady=(15,2))

        ctk.CTkLabel(
            win,
            text=f"{req[1]} • Budget {req[6]} • {req[5]} Openings",
            text_color="gray"
        ).pack()

        search = ctk.CTkEntry(
            win,
            placeholder_text="Search candidate..."
        )
        search.pack(fill="x", padx=20, pady=12)

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=(0,15))

        cols = ("Name","Skill","Experience","Status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)

        tree.column("Name", width=180)
        tree.column("Skill", width=220)
        tree.column("Experience", width=120)
        tree.column("Status", width=120)

        tree.pack(fill="both", expand=True)

        candidate_map = {}

        def load(rows):

            tree.delete(*tree.get_children())
            candidate_map.clear()

            for cand in rows:

                item = tree.insert(
                    "",
                    "end",
                    values=(
                        cand[1],
                        cand[4],
                        cand[5],
                        cand[7]
                    )
                )

                candidate_map[item] = cand

        load(candidates)

        def filter_data(event=None):

            key = search.get().lower()

            if key == "":
                load(candidates)
                return

            load([
                c for c in candidates
                if key in c[1].lower()
                or key in c[4].lower()
            ])

        search.bind("<KeyRelease>", filter_data)

        def choose():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Candidate",
                    "Please select a candidate first."
                )
                return

            candidate = candidate_map[selected[0]]

            # Close requirement candidate window
            win.destroy()

            # Open assignment popup after window closes
            self.app.after(
                100,
                lambda: self.assign_candidate_to_requirement(req, candidate)
            )

        ctk.CTkButton(
            win,
            text="Continue",
            fg_color="#2563EB",
            command=choose
        ).pack(fill="x", padx=20, pady=(0,15))
        
            
    def assign_candidate_to_requirement(self, req, candidate):

        team = get_assignable_employees(self.emp_id, self.role)

        # Include yourself
        me = employee_details(self.emp_id)
        team.insert(0, (me[0], me[1], me[4]))

        win = ctk.CTkToplevel(self.app)
        win.title("Assign Candidate")
        win.geometry("420x360")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text=candidate[1],
            font=("Segoe UI",20,"bold")
        ).pack(pady=(18,5))

        ctk.CTkLabel(
            win,
            text=f"{candidate[4]} • {candidate[5]} Years",
            text_color="gray"
        ).pack()

        members = [f"{i[1]} ({i[2]})" for i in team]

        ctk.CTkLabel(win, text="Assign To").pack(anchor="w", padx=25, pady=(18,5))

        emp_box = ctk.CTkComboBox(win, values=members)
        emp_box.pack(fill="x", padx=25)
        emp_box.set(members[0])

        ctk.CTkLabel(win, text="Priority").pack(anchor="w", padx=25, pady=(15,5))

        priority = ctk.CTkComboBox(
            win,
            values=["High","Medium","Low"]
        )
        priority.pack(fill="x", padx=25)
        priority.set("Medium")

        def save():

            idx = members.index(emp_box.get())
            emp = team[idx]
            
            assigned = assigned_candidate_count(req[0])

            if assigned >= req[5]:
                messagebox.showwarning(
                    "Requirement Full",
                    f"All {req[5]} openings have already been filled."
                )
                return
            
            
            # Requirement history
            assign_candidate_requirement(
                req[0],
                candidate[0],
                self.emp_id,
                emp[0],
                priority.get()
            )


            close_requirement_if_filled(req[0])


            # My Tasks
            assign_task(
                candidate[0],
                self.emp_id,
                emp[0],
                emp[2],
                priority.get(),
                datetime.now().strftime("%Y-%m-%d"),
                f"Requirement : {req[2]}"
            )

            messagebox.showinfo(
                "Success",
                f"{candidate[1]} assigned to {emp[1]}"
            )

            win.destroy()
            self.open_requirement(req)

        ctk.CTkButton(
            win,
            text="Assign Candidate",
            fg_color="#2563EB",
            command=save
        ).pack(fill="x", padx=25, pady=25)
    
     
    def show_employees(self):

        self.clear_main()
        self.highlight_menu("Employees")

        ctk.CTkLabel(
            self.main,
            text="Employee Hierarchy",
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        # ---------------- HEAD ----------------
        if self.role == "Head":
            employees = view_employees()
            data = [e for e in employees if e[4] != "Head"]

        # -------- ACCOUNT MANAGER --------
        elif self.role == "Account Manager":
            me = employee_details(self.emp_id)
            team = get_team(self.emp_id)
            data = [me] + team

        # ---------- RECRUITER ----------
        elif self.role == "Recruiter":
            me = employee_details(self.emp_id)
            team = get_team(self.emp_id)
            data = [me] + team

        # ------------ INTERN ------------
        else:
            data = [employee_details(self.emp_id)]

        body = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20)

        for emp in data:

            card = ctk.CTkFrame(body, fg_color="white", corner_radius=12)
            card.pack(fill="x", pady=6)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=15, pady=12)

            ctk.CTkLabel(
                left,
                text=emp[1],
                font=("Segoe UI", 16, "bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                left,
                text=emp[4],
                text_color="gray"
            ).pack(anchor="w")

            client = emp[6] if emp[6] else "Internal"

            ctk.CTkLabel(
                left,
                text=f"Client : {client}",
                text_color="#2563EB"
            ).pack(anchor="w")

            ctk.CTkButton(
                card,
                text="Open Dashboard",
                width=130,
                fg_color="#2563EB",
                command=lambda e=emp: self.show_team_dashboard(e)
            ).pack(side="right", padx=15)
        
    def open_employee_dashboard(self, event):

        tree = event.widget
        selected = tree.selection()

        if not selected:
            return

        emp_id = selected[0]
        emp = employee_details(emp_id)

        if emp:
            self.show_team_dashboard(emp)


    def show_team_dashboard(self, employee, acting_as=False):
        """Employee dashboard with hierarchy navigation"""

        if not employee:
            return
        
        # -------- Authorization --------
        if self.role != "Head":

            # Can always view yourself
            if employee[0] != self.emp_id:

                allowed = [
                    e[0] for e in get_assignable_employees(
                        self.emp_id,
                        self.role
                    )
                ]

                if employee[0] not in allowed:
                    messagebox.showerror(
                        "Access Denied",
                        "You are not authorized to view this team."
                    )
                    return

        print("Opening:", employee)

        # Current viewed employee
        self.view_emp_id = employee[0]
        self.view_role = employee[4]

        self.clear_main()

        # ================= HEADER =================
        header = ctk.CTkFrame(self.main, fg_color="white", corner_radius=15)
        header.pack(fill="x", padx=25, pady=(20,15))

        top = ctk.CTkFrame(header, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=15)

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(
            left,
            text=employee[1],
            font=("Segoe UI", 28, "bold")
        ).pack(anchor="w")

        client = employee[6] if employee[6] else "Internal"

        ctk.CTkLabel(
            left,
            text=f"{employee[4]} • {client}",
            text_color="#64748B"
        ).pack(anchor="w")

        ctk.CTkButton(
            top,
            text="← Back to Organization",
            fg_color="#64748B",
            hover_color="#475569",
            command=self.show_employees
        ).pack(side="right")

        # ================= ASSIGN BUTTON =================
        action = ctk.CTkFrame(self.main, fg_color="transparent")
        action.pack(fill="x", padx=25, pady=(0,10))

        ctk.CTkButton(
            action,
            text="📋 Assign Requirement",
            fg_color="#2563EB",
            command=lambda: self.assign_requirement_to_employee(employee[0], employee[4])
        ).pack(side="right")

        # ================= KPI =================
        total, assigned, progress, completed = employee_task_stats(employee[0])

        requirements = employee_requirement_count(employee[0])

        cards = ctk.CTkFrame(self.main, fg_color="transparent")
        cards.pack(fill="x", padx=25, pady=(0,15))

        def kpi(title, value, color):
            box = ctk.CTkFrame(cards, fg_color=color, corner_radius=12)
            box.pack(side="left", expand=True, fill="x", padx=5)

            ctk.CTkLabel(
                box,
                text=title,
                text_color="white"
            ).pack(anchor="w", padx=15, pady=(10,0))

            ctk.CTkLabel(
                box,
                text=str(value),
                font=("Segoe UI",24,"bold"),
                text_color="white"
            ).pack(anchor="w", padx=15, pady=(0,10))

        kpi("Requirements", requirements, "#2563EB")
        kpi("Assigned", assigned, "#F59E0B")
        kpi("Progress", progress, "#0EA5E9")
        kpi("Completed", completed, "#16A34A")

        # ================= TEAM =================
        ctk.CTkLabel(
            self.main,
            text="Team Members",
            font=("Segoe UI",20,"bold")
        ).pack(anchor="w", padx=25)

        team_box = ctk.CTkScrollableFrame(self.main, fg_color="transparent", height=220)
        team_box.pack(fill="x", padx=25, pady=10)

        members = team_workload(employee[0])

        if not members:
            ctk.CTkLabel(
                team_box,
                text="No team members",
                text_color="gray"
            ).pack(pady=30)

        for m in members:

            row = ctk.CTkFrame(team_box, fg_color="white", corner_radius=10)
            row.pack(fill="x", pady=5)

            def open_member(emp_id=m[0]):
                member_data = employee_details(emp_id)
                if member_data:
                    self.show_team_dashboard(member_data, acting_as=True)

            row.bind("<Button-1>", lambda e, emp_id=m[0]: open_member(emp_id))

            avatar = ctk.CTkLabel(
                row,
                text=m[1][0],
                width=40,
                height=40,
                corner_radius=20,
                fg_color="#DBEAFE",
                text_color="#1D4ED8",
                font=("Segoe UI",16,"bold")
            )
            avatar.pack(side="left", padx=12, pady=8)
            avatar.bind("<Button-1>", lambda e, emp_id=m[0]: open_member(emp_id))

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left")

            name = ctk.CTkLabel(
                info,
                text=m[1],
                font=("Segoe UI",14,"bold")
            )
            name.pack(anchor="w")
            name.bind("<Button-1>", lambda e, emp_id=m[0]: open_member(emp_id))

            role = ctk.CTkLabel(
                info,
                text=m[2],
                text_color="gray"
            )
            role.pack(anchor="w")
            role.bind("<Button-1>", lambda e, emp_id=m[0]: open_member(emp_id))

            stats = ctk.CTkFrame(row, fg_color="transparent")
            stats.pack(side="right", padx=15)

            ctk.CTkLabel(
                stats,
                text=f"{m[3]} Profiles",
                text_color="#2563EB"
            ).pack(anchor="e")

            ctk.CTkLabel(
                stats,
                text=f"{m[4]} Pending",
                text_color="#EA580C"
            ).pack(anchor="e")

            ctk.CTkButton(
            row,
            text="Open",
            width=70,
            fg_color="#2563EB",
            command=lambda m=m: self.show_team_dashboard(
                employee_details(m[0]),
                acting_as=True
            )
        ).pack(side="right", padx=10)

        # ================= ASSIGNED REQUIREMENTS =================
        ctk.CTkLabel(
            self.main,
            text="Assigned Requirements",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=25, pady=(10,5))

        req_box = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        req_box.pack(fill="x", padx=25, pady=(0,15))

        requirements = my_requirements(employee[0])

        if not requirements:
            ctk.CTkLabel(
                req_box,
                text="No requirements assigned.",
                text_color="gray"
            ).pack(pady=25)

        else:
            for req in requirements:

                row = ctk.CTkFrame(
                    req_box,
                    fg_color="#F8FAFC",
                    corner_radius=8
                )
                row.pack(fill="x", padx=15, pady=6)

                # Click entire row
                row.bind("<Button-1>", lambda e, r=req: self.open_requirement(r))

                # Left
                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left", padx=10, pady=8)

                title = ctk.CTkLabel(
                    left,
                    text=req[2],
                    font=("Segoe UI",13,"bold")
                )
                title.pack(anchor="w")
                title.bind("<Button-1>", lambda e, r=req: self.open_requirement(r))

                client = ctk.CTkLabel(
                    left,
                    text=f"{req[1]} • {req[3]}",
                    text_color="gray"
                )
                client.pack(anchor="w")
                client.bind("<Button-1>", lambda e, r=req: self.open_requirement(r))

                # Right
                right = ctk.CTkFrame(row, fg_color="transparent")
                right.pack(side="right", padx=10)

                status = ctk.CTkLabel(
                    right,
                    text=req[13],
                    text_color="#16A34A",
                    font=("Segoe UI",11,"bold")
                )
                status.pack(anchor="e")
                status.bind("<Button-1>", lambda e, r=req: self.open_requirement(r))

                ctk.CTkLabel(
                    right,
                    text=req[14],
                    text_color="gray",
                    font=("Segoe UI",10)
                ).pack(anchor="e")

                # Open Button
                ctk.CTkButton(
                    right,
                    text="Open",
                    width=75,
                    fg_color="#2563EB",
                    hover_color="#1D4ED8",
                    command=lambda r=req: self.open_requirement(r)
                ).pack(anchor="e", pady=(6,0))




        # ================= RECENT PROFILES =================
        ctk.CTkLabel(
            self.main,
            text="Recent Assigned Profiles",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=25, pady=(10,5))

        recent = employee_recent_tasks(employee[0])

        recent_box = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        recent_box.pack(fill="both", expand=True, padx=25, pady=(0,10))

        if recent:
            for r in recent:

                row = ctk.CTkFrame(recent_box, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=6)

                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left")

                ctk.CTkLabel(
                    left,
                    text=r[0],
                    font=("Segoe UI",13,"bold")
                ).pack(anchor="w")

                ctk.CTkLabel(
                    left,
                    text=f"{r[1]} • {r[2]}",
                    text_color="gray"
                ).pack(anchor="w")

                right = ctk.CTkFrame(row, fg_color="transparent")
                right.pack(side="right")

                ctk.CTkLabel(
                    right,
                    text=r[3],
                    text_color="#7C3AED"
                ).pack()

                ctk.CTkLabel(
                    right,
                    text=r[4],
                    text_color="#2563EB"
                ).pack()
        else:
            ctk.CTkLabel(
                recent_box,
                text="No profiles assigned.",
                text_color="gray"
            ).pack(pady=25)

        # ================= ACTIVITY =================
        ctk.CTkLabel(
            self.main,
            text="Recent Activity",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=25)

        act_box = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        act_box.pack(fill="x", padx=25, pady=(5,15))

        activities = employee_activity(employee[0])

        if activities:
            for a in activities:
                r = ctk.CTkFrame(act_box, fg_color="transparent")
                r.pack(fill="x", padx=15, pady=6)

                ctk.CTkLabel(
                    r,
                    text="●",
                    text_color="#2563EB"
                ).pack(side="left", padx=(0,10))

                txt = ctk.CTkFrame(r, fg_color="transparent")
                txt.pack(side="left")

                ctk.CTkLabel(
                    txt,
                    text=f"{a[0]} • {a[1]}",
                    font=("Segoe UI",12,"bold")
                ).pack(anchor="w")

                ctk.CTkLabel(
                    txt,
                    text=f"{a[2]} | {a[3]}",
                    text_color="gray",
                    font=("Segoe UI",10)
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                act_box,
                text="No activity available",
                text_color="gray"
            ).pack(pady=20)
                   


    def build_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self.app,
            width=220,
            fg_color=SIDEBAR,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assests",
            "ibotix_logo.png"
        )

        if os.path.exists(logo_path):
            logo = ctk.CTkImage(
                Image.open(logo_path),
                size=(170,55)
            )

            ctk.CTkLabel(
                self.sidebar,
                image=logo,
                text=""
            ).pack(pady=(20,5))

        ctk.CTkLabel(
            self.sidebar,
            text="Staffing Operations CRM",
            font=("Segoe UI",12),
            text_color="#CBD5E1"
        ).pack(pady=(0,20))

        self.buttons = {}

        menu = [
            ("🏠","Dashboard", self.show_dashboard),
            ("💼","Requirements", self.show_requirements),
            ("👥","Candidates", self.show_candidates),
            ("📋","My Tasks", self.show_tasks),
            ("➕","Add Candidate", self.add_candidate),
            ("📎","Resume", self.show_candidates)
        ]

        # Visible for everyone
        menu.append(("👨‍💼", "Employees", self.show_employees))

        # Reports only for Head
        if self.role.lower() == "head":
            menu.append(("📊", "Reports", self.show_reports))

        # Everyone
        menu.append(("⚙","Settings",self.show_settings))
        menu.append(("🚪","Logout",self.logout))

        for icon,text,command in menu:

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}   {text}",
                anchor="w",
                width=185,
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=PRIMARY_DARK,
                font=("Segoe UI",14),
                command=command
            )

            btn.pack(fill="x", padx=12, pady=4)
            self.buttons[text] = btn

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        profile = ctk.CTkFrame(
            self.sidebar,
            fg_color="#172554",
            corner_radius=14
        )
        profile.pack(fill="x", padx=12, pady=12)

        avatar = ctk.CTkLabel(
            profile,
            text=self.user_name[0].upper(),
            width=46,
            height=46,
            corner_radius=23,
            fg_color=PRIMARY,
            text_color="white",
            font=("Segoe UI",20,"bold")
        )
        avatar.pack(anchor="w", padx=15, pady=(12,8))

        ctk.CTkLabel(
            profile,
            text=self.user_name,
            font=("Segoe UI",15,"bold"),
            text_color="white"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            profile,
            text=self.role,
            font=("Segoe UI",12),
            text_color="#BFDBFE"
        ).pack(anchor="w", padx=15)

        ctk.CTkLabel(
            profile,
            text="● Online",
            font=("Segoe UI",11),
            text_color="#22C55E"
        ).pack(anchor="w", padx=15, pady=(5,0))

        self.time_label = ctk.CTkLabel(
            profile,
            text="",
            font=("Segoe UI",10),
            text_color="#CBD5E1"
        )
        self.time_label.pack(anchor="w", padx=15, pady=(2,12))

        def update_time():
            try:
                if self.app.winfo_exists():
                    self.time_label.configure(
                        text=datetime.now().strftime("%d %b %Y • %I:%M:%S %p")
                    )
                    self.app.after(1000, update_time)
            except:
                return
            
        update_time()        

    # =====================================================
    # COMMON
    # =====================================================

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def logout(self):
        try:
            self.app.quit()
            self.app.destroy()
        except:
            pass

        login_path = os.path.join(os.path.dirname(__file__), "login.py")
        subprocess.Popen([sys.executable, login_path])
        
        
    def highlight_menu(self, active):

        for name,btn in self.buttons.items():

            if name == active:
                btn.configure(fg_color=PRIMARY)
            else:
                btn.configure(fg_color="transparent")

    # =====================================================
    # DASHBOARD HOME
    # =====================================================
    def show_dashboard(self):
        self.clear_main()
        self.highlight_menu("Dashboard")

        self.build_header()
        self.build_cards()

        self.build_assigned_requirements()  
        self.build_toolbar()
        self.build_table()

        self.load_candidates()
        self.build_assigned_candidates()

    # =====================================================
    # HERO HEADER
    # =====================================================

    def build_header(self):

        hero = ctk.CTkFrame(
            self.main,
            fg_color=PRIMARY,
            corner_radius=18,
            height=135
        )

        hero.pack(fill="x", padx=22, pady=(22,15))
        hero.pack_propagate(False)

        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.pack(side="left", padx=25, pady=18)

        hour = datetime.now().hour

        if hour < 12:
            greet = "Good Morning"
        elif hour < 17:
            greet = "Good Afternoon"
        else:
            greet = "Good Evening"

        ctk.CTkLabel(
            left,
            text=greet,
            font=("Segoe UI",16),
            text_color="#DBEAFE"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{self.user_name} 👋",
            font=("Segoe UI",34,"bold"),
            text_color="white"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"{self.role} • IBOTIX Staffing Operations",
            font=("Segoe UI",13),
            text_color="#DBEAFE"
        ).pack(anchor="w", pady=(5,0))

        if self.role.lower() == "head":
            total = len(view_candidates())
        else:
            total = len(my_candidates(self.emp_id))

        right = ctk.CTkFrame(
            hero,
            fg_color="#4F7EF0",
            corner_radius=16,
            width=170,
            height=92
        )

        right.pack(side="right", padx=25)
        right.pack_propagate(False)

        ctk.CTkLabel(
            right,
            text="Active Pipeline",
            font=("Segoe UI",12),
            text_color="#DBEAFE"
        ).pack(pady=(12,0))

        ctk.CTkLabel(
            right,
            text=str(total),
            font=("Segoe UI",30,"bold"),
            text_color="white"
        ).pack()

        ctk.CTkLabel(
            right,
            text="Candidates",
            font=("Segoe UI",11),
            text_color="#DBEAFE"
        ).pack()

    # =====================================================
    # KPI CARDS
    # =====================================================

    def build_cards(self):

        if self.role.lower() == "head":
            data = view_candidates()
        else:
            data = my_candidates(self.emp_id)

        total = len(data)
        clients = len(set(c[6] for c in data)) if data else 0
        interview = sum(1 for c in data if c[7].lower()=="interview")
        final = sum(1 for c in data if c[7].lower()=="final")

        row = ctk.CTkFrame(self.main, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(0,18))

        self.create_card(row,"Candidates",total,PRIMARY)
        self.create_card(row,"Clients",clients,PURPLE)
        self.create_card(row,"Interview",interview,TEAL)
        self.create_card(row,"Final",final,ORANGE)
        
        
    def build_assigned_candidates(self):

        rows = my_requirement_candidates(self.emp_id)

        if not rows:
            return

        card = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        card.pack(fill="x", padx=22, pady=(0,15))

        ctk.CTkLabel(
            card,
            text="My Assigned Candidates",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=15, pady=12)

        for r in rows[:5]:

            row = ctk.CTkFrame(
                card,
                fg_color="#F8FAFC",
                corner_radius=8
            )
                
            row.bind(
                "<Button-1>",
                lambda e, cid=r[0]: self.open_candidate_by_id(cid)
                        )  
            row.pack(fill="x", padx=15, pady=5)

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left")

            ctk.CTkLabel(
                left,
                text=r[2],
                font=("Segoe UI",13,"bold")
            ).pack(anchor="w")
            
            name.pack(anchor="w")

            name.bind(
                "<Button-1>",
                lambda e, cid=r[0]: self.open_candidate_by_id(cid)
            )

            ctk.CTkLabel(
                left,
                text=f"{r[1]} • {r[3]}",
                text_color="gray"
            ).pack(anchor="w")

            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right")

            ctk.CTkLabel(
                right,
                text=r[4],
                text_color="#2563EB"
            ).pack(anchor="e")

            ctk.CTkLabel(
                right,
                text=r[6],
                text_color="gray",
                font=("Segoe UI",10)
            ).pack(anchor="e")    
        
        
    def open_candidate_by_id(self, candidate_id):

        if self.role == "Head":
            data = view_candidates()
        else:
            data = my_candidates(self.emp_id)

        candidate = next(
            (c for c in data if c[0] == candidate_id),
            None
        )

        if not candidate:
            messagebox.showerror(
                "Error",
                "Candidate not found."
            )
            return

        self.open_profile_data(candidate)    

    def create_card(self,parent,title,value,color):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
            width=220,
            height=105
        )

        card.pack(side="left", padx=8)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI",12),
            text_color=SUB
        ).pack(anchor="w", padx=16, pady=(14,4))

        ctk.CTkLabel(
            card,
            text=str(value),
            font=("Segoe UI",28,"bold"),
            text_color=color
        ).pack(anchor="w", padx=16)

        ctk.CTkLabel(
            card,
            text="Live Database",
            font=("Segoe UI",10),
            text_color=GREEN
        ).pack(anchor="w", padx=16)

    # =====================================================
    # TOOLBAR
    # =====================================================

    def build_toolbar(self):

        toolbar = ctk.CTkFrame(
            self.main,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )
        toolbar.pack(fill="x", padx=22, pady=(0,12))

        ctk.CTkLabel(
            toolbar,
            text="Candidate Pipeline",
            font=("Segoe UI",20,"bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=18, pady=(15,10))

        row = ctk.CTkFrame(toolbar, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0,15))

        self.search_entry = ctk.CTkEntry(
            row,
            width=360,
            height=38,
            corner_radius=10,
            placeholder_text="Search by Name, Skill or Client..."
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.live_search)

        ctk.CTkButton(
            row,
            text="Search",
            width=95,
            height=38,
            fg_color=PRIMARY,
            hover_color=PRIMARY_DARK,
            command=self.search
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            row,
            text="Refresh",
            width=90,
            height=38,
            fg_color="#64748B",
            command=self.load_candidates
        ).pack(side="right")

        ctk.CTkButton(
            row,
            text="+ Add Candidate",
            width=155,
            height=38,
            fg_color=GREEN,
            hover_color="#15803D",
            command=self.add_candidate
        ).pack(side="right", padx=8)

    # =====================================================
    # CANDIDATE TABLE
    # =====================================================

    def build_table(self):

        table_frame = ctk.CTkFrame(
            self.main,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(0,20)
        )

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="white",
            foreground="#111827",
            fieldbackground="white",
            rowheight=38,
            font=("Segoe UI",10),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#EFF6FF",
            foreground="#1D4ED8",
            font=("Segoe UI",10,"bold")
        )

        columns = ("ID","Candidate","Skill","Client","Status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        widths = {
            "ID":70,
            "Candidate":220,
            "Skill":180,
            "Client":160,
            "Status":150
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], anchor="center")

        scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(12,0),
            pady=12
        )

        scroll.pack(
            side="right",
            fill="y",
            padx=(0,12),
            pady=12
        )

        self.tree.bind("<Double-1>", self.open_profile)

    # =====================================================
    # LOAD CANDIDATES
    # =====================================================

    def load_candidates(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.role.lower() == "head":
            data = view_candidates()
        else:
            data = my_candidates(self.emp_id)

        badge = {
            "submitted":"🔵 Submitted",
            "interview":"🟡 Interview",
            "screening":"⚪ Screening",
            "final":"🟣 Final",
            "on":"🟢 Active"
        }

        for i, c in enumerate(data):

            status = badge.get(c[7].lower(), c[7])
            tag = "even" if i % 2 == 0 else "odd"

            self.tree.insert(
                "",
                "end",
                values=(
                    c[0],
                    c[1],
                    c[4],
                    c[6],
                    status
                ),
                tags=(tag,)
            )

        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background="#F8FAFC")

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self):

        keyword = self.search_entry.get().strip()

        if keyword == "":
            self.load_candidates()
            return

        if self.role.lower() == "head":
            rows = search_candidate(keyword)
        else:
            rows = search_candidate(keyword, self.emp_id)

        self.populate_table(rows)

    # =====================================================
    # LIVE SEARCH
    # =====================================================

    def live_search(self, event):
        self.search()

    # =====================================================
    # POPULATE TABLE
    # =====================================================

    def populate_table(self, rows):

        for row in self.tree.get_children():
            self.tree.delete(row)

        badge = {
            "submitted":"🔵 Submitted",
            "interview":"🟡 Interview",
            "screening":"⚪ Screening",
            "final":"🟣 Final",
            "on":"🟢 Active"
        }

        for i, r in enumerate(rows):

            status = badge.get(r[7].lower(), r[7])
            tag = "even" if i % 2 == 0 else "odd"

            self.tree.insert(
                "",
                "end",
                values=(
                    r[0],
                    r[1],
                    r[4],
                    r[6],
                    status
                ),
                tags=(tag,)
            )

        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background="#F8FAFC")   
        
    # =====================================================
    # CANDIDATE PROFILE
    # =====================================================

    def open_profile(self, event):

        selected = self.tree.focus()

        if not selected:
            return

        values = self.tree.item(selected)["values"]

        # Fetch complete candidate record
        if self.role.lower() == "head":
            data = view_candidates()
        else:
            data = my_candidates(self.emp_id)

        candidate = next((c for c in data if c[0] == values[0]), None)

        # Safety check
        if not candidate:
           messagebox.showerror("Error", "Candidate not found.")
           return

        remarks = candidate[8]

        profile = ctk.CTkToplevel(self.app)
        profile.title("Candidate Profile")
        profile.geometry("480x630")
        profile.resizable(False, False)
        profile.grab_set()

        ctk.CTkLabel(
            profile,
            text=values[1],
            font=("Segoe UI", 24, "bold")
        ).pack(pady=18)

        card = ctk.CTkFrame(profile, corner_radius=12)
        card.pack(fill="x", padx=20)

        def field(label, value):

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(
                row,
                text=label,
                width=95,
                anchor="w",
                text_color=SUB
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=str(value),
                font=("Segoe UI", 13, "bold")
            ).pack(side="left")

        field("ID", values[0])
        field("Skill", values[2])
        field("Client", values[3])
        field("Status", values[4])
        
        ctk.CTkLabel(
            profile,
            text="Update Status",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=22, pady=(15,5))

        status_box = ctk.CTkComboBox(
            profile,
            values=["Screening", "Submitted", "Interview", "Final"]
        )
        status_box.pack(fill="x", padx=20)
        status_box.set(candidate[7].title())

        ctk.CTkLabel(
            profile,
            text="Recruiter Remarks",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=22, pady=(20, 6))

        self.remarks_box = ctk.CTkTextbox(
            profile,
            height=120,
            corner_radius=10
        )
        self.remarks_box.pack(fill="x", padx=20)

        # Load previous remarks
        self.remarks_box.insert("1.0", remarks)

        # =========================
        # Button Row
        # =========================

        btn_row = ctk.CTkFrame(profile, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=20)

        if self.role in ["Head", "Account Manager", "Recruiter"]:
            ctk.CTkButton(
                btn_row,
                text="📤 Assign Task",
                fg_color="#7C3AED",
                width=120,
                command=lambda: self.assign_task_popup(candidate)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_row,
                text="💾 Save",
                fg_color="#16A34A",
                width=80,
                command=lambda: (
                    update_candidate_status(candidate[0], status_box.get()),
                    self.save_remarks(candidate[0]),
                    profile.destroy(),
                    self.load_candidates()
                )
            ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row,
            text="📄 Resume",
            fg_color="#2563EB",
            width=80,
            command=lambda: self.view_resume(candidate[0])
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row,
            text="🗑 Delete",
            fg_color="#DC2626",
            width=80,
            command=lambda: self.delete_profile(candidate[0], profile)
        ).pack(side="right")  
        
        
    def open_task_candidate(self, task_id):

        from database import task_candidate

        candidate = task_candidate(task_id)

        if not candidate:
            messagebox.showerror("Error", "Candidate not found.")
            return

        self.open_profile_data(candidate)    
        

    def assign_task_popup(self, candidate, assigner_id, assigner_role):
        team = get_assignable_employees(assigner_id, assigner_role)


        if not team:
            messagebox.showwarning(
                "Hierarchy",
                "No employees available under your hierarchy."
            )
            return

        win = ctk.CTkToplevel(self.app)
        win.title("Assign Task")
        win.geometry("430x520")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Assign Task",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=15)

        # Candidate Card
        card = ctk.CTkFrame(win, fg_color="#F8FAFC", corner_radius=12)
        card.pack(fill="x", padx=20)

        ctk.CTkLabel(
            card,
            text=candidate[1],
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=(12,2))

        ctk.CTkLabel(
            card,
            text=f"{candidate[6]} • {candidate[4]} • {candidate[5]} Years",
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(0,12))

        # Employee list
        members = [f"{x[1]} ({x[2]})" for x in team]

        ctk.CTkLabel(win, text="Assign To").pack(anchor="w", padx=20, pady=(15,5))
        emp_box = ctk.CTkComboBox(win, values=members)
        emp_box.pack(fill="x", padx=20)
        emp_box.set(members[0])

        ctk.CTkLabel(win, text="Priority").pack(anchor="w", padx=20, pady=(12,5))
        priority = ctk.CTkComboBox(
            win,
            values=["High","Medium","Low"]
        )
        priority.pack(fill="x", padx=20)
        priority.set("Medium")

        ctk.CTkLabel(win, text="Due Date").pack(anchor="w", padx=20, pady=(12,5))
        due = DateEntry(
            win,
            date_pattern="yyyy-mm-dd",
            width=25
        )
        due.pack(fill="x", padx=20)

        ctk.CTkLabel(win, text="Instructions").pack(anchor="w", padx=20, pady=(12,5))
        notes = ctk.CTkTextbox(win, height=80)
        notes.pack(fill="x", padx=20)

        def submit():

            idx = members.index(emp_box.get())
            employee = team[idx]

            ok = assign_task(
                candidate[0],
                assigner_id,
                employee[0],
                employee[2],
                priority.get(),
                due.get(),
                notes.get("1.0", "end").strip()
            )

            if ok:
                messagebox.showinfo(
                    "Success",
                    f"{candidate[1]} assigned successfully!"
                )

                win.destroy()

                # Refresh dashboard
                self.show_team_dashboard(
                    employee_details(assigner_id)
                )

            else:
                messagebox.showerror(
                    "Error",
                    "Task could not be assigned."
                )
        
        # Buttons
        bottom = ctk.CTkFrame(win, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            bottom,
            text="Cancel",
            width=100,
            fg_color="#64748B",
            command=win.destroy
        ).pack(side="left")

        ctk.CTkButton(
            bottom,
            text="Assign Task",
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=submit
        ).pack(side="right", fill="x", expand=True, padx=(10,0))

    # =====================================================
    # SAVE REMARKS
    # =====================================================

    def save_remarks(self, candidate_id):

        text = self.remarks_box.get("1.0", "end").strip()

        update_remarks(candidate_id, text)

        messagebox.showinfo(
            "Success",
            "Remarks updated successfully."
        )


    # =====================================================
    # VIEW RESUME
    # =====================================================

    def view_resume(self, candidate_id):

        result = get_resume(candidate_id)

        if not result:
            messagebox.showerror(
                "Error",
                "Resume not found."
            )
            return

        path = result[0]

        if path and os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning(
                "Missing",
                "Resume file does not exist."
            )


    # =====================================================
    # ADD CANDIDATE
    # =====================================================

    def add_candidate(self):

        self.selected_resume = ""

        win = ctk.CTkToplevel(self.app)
        win.title("Add Candidate")
        win.geometry("640x760")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Add New Candidate",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=18)

        form = ctk.CTkScrollableFrame(win)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        def field(label):

            ctk.CTkLabel(
                form,
                text=label,
                font=("Segoe UI", 12, "bold")
            ).pack(anchor="w", pady=(8, 2))

            entry = ctk.CTkEntry(form, height=38)
            entry.pack(fill="x")
            return entry

        candidate_id = field("Candidate ID")
        name = field("Candidate Name")
        mobile = field("Mobile Number")
        email = field("Email Address")
        skill = field("Primary Skill")
        experience = field("Experience")

        # Client

        ctk.CTkLabel(
            form,
            text="Client",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(8, 2))

        client = ctk.CTkComboBox(
            form,
            values=[
                "TCS",
                "Infosys",
                "Wipro",
                "HCL",
                "Accenture",
                "IBOTIX"
            ]
        )
        client.pack(fill="x")
        client.set("IBOTIX")

        # Status

        ctk.CTkLabel(
            form,
            text="Current Status",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(8, 2))

        status = ctk.CTkComboBox(
            form,
            values=[
                "Screening",
                "Submitted",
                "Interview",
                "Final"
            ]
        )
        status.pack(fill="x")
        status.set("Screening")

        # Remarks

        ctk.CTkLabel(
            form,
            text="Recruiter Remarks",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(8, 2))

        remarks = ctk.CTkTextbox(form, height=90)
        remarks.pack(fill="x")

        # Resume

        resume_name = ctk.CTkLabel(
            form,
            text="No Resume Selected",
            text_color=SUB
        )
        resume_name.pack(anchor="w", pady=8)

        def browse():

            file = filedialog.askopenfilename(
                filetypes=[("PDF Files", "*.pdf")]
            )

            if file:
                self.selected_resume = file
                resume_name.configure(
                    text=os.path.basename(file)
                )

        ctk.CTkButton(
            form,
            text="Browse Resume",
            fg_color="#64748B",
            command=browse
        ).pack(anchor="w")

        # Save Candidate

        def save():

            if candidate_id.get() == "" or name.get() == "":
                messagebox.showerror(
                    "Required",
                    "Candidate ID and Name are mandatory."
                )
                return

            try:
                cid = int(candidate_id.get())
            except ValueError:
                messagebox.showerror(
                    "Invalid",
                    "Candidate ID must be numeric."
                )
                return

            ok = insert_candidate(
                cid,
                name.get(),
                mobile.get(),
                email.get(),
                skill.get(),
                experience.get(),
                client.get(),
                status.get(),
                remarks.get("1.0", "end").strip(),
                self.selected_resume,
                self.emp_id,
                self.emp_id
            )

            if ok:

                messagebox.showinfo(
                    "Success",
                    "Candidate added successfully."
                )

                win.destroy()
                self.show_candidates()

            else:

                messagebox.showerror(
                    "Duplicate",
                    "Candidate ID already exists."
                )

        ctk.CTkButton(
            form,
            text="Save Candidate",
            height=44,
            fg_color=GREEN,
            hover_color="#15803D",
            command=save
        ).pack(fill="x", pady=20)
        
    def open_assign_candidate(self, manager_id, role):

        # DON'T use logged-in user
        self.view_emp_id = manager_id
        self.view_role = role

        candidates = view_candidates()

        win = ctk.CTkToplevel(self.app)
        win.title("Assign Candidate")
        win.geometry("760x600")
        win.resizable(False, False)
        win.grab_set()

        # ================= Header =================
        ctk.CTkLabel(
            win,
            text="Assign Candidate",
            font=("Segoe UI", 26, "bold")
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            win,
            text="Search and assign a candidate to your team",
            text_color="gray"
        ).pack()

        # ================= Search =================
        search = ctk.CTkEntry(
            win,
            placeholder_text="🔍 Search by Candidate, Client or Skill",
            height=36
        )
        search.pack(fill="x", padx=20, pady=15)

        # ================= Table =================
        table_frame = ctk.CTkFrame(
            win,
            fg_color="white",
            corner_radius=10
        )
        table_frame.pack(fill="both", expand=True, padx=20)

        columns = ("Name", "Client", "Skill", "Exp", "Status")

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=14,
            selectmode="browse"
        )

        widths = {
            "Name": 180,
            "Client": 130,
            "Skill": 180,
            "Exp": 70,
            "Status": 120
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0),
            pady=8
        )
        scrollbar.pack(side="right", fill="y", pady=8)

        # ---------------- Candidate Map ----------------
        candidate_map = {}

        def load(rows):
            tree.delete(*tree.get_children())
            candidate_map.clear()

            for c in rows:
                item = tree.insert(
                    "",
                    "end",
                    values=(
                        c[1],      # Name
                        c[6],      # Client
                        c[4],      # Skill
                        c[5],      # Experience
                        c[7]       # Status
                    )
                )
                candidate_map[item] = c

        load(candidates)

        # ---------------- Search ----------------
        def filter_data(event=None):
            key = search.get().lower().strip()

            if key == "":
                load(candidates)
                return

            filtered = [
                c for c in candidates
                if key in str(c[1]).lower()
                or key in str(c[6]).lower()
                or key in str(c[4]).lower()
            ]

            load(filtered)

        search.bind("<KeyRelease>", filter_data)
    

        # ---------------- Row Selection ----------------
        def select_and_assign(event):
            item = tree.identify_row(event.y)

            if not item:
                return

            tree.selection_set(item)
            tree.focus(item)

            candidate = candidate_map[item]

            # Close candidate window first
            win.destroy()

            # Open assignment popup after destroy
            self.app.after(
                150,
                lambda c=candidate: self.assign_task_popup(
                    c,
                    manager_id,
                    role
                )
            )

        # ---------------- Assign ----------------
        def assign():
            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Candidate",
                    "Please select a candidate."
                )
                return

            candidate = candidate_map[selected[0]]

            win.destroy()

            self.app.after(
                150,
                lambda c=candidate: self.assign_task_popup(
                    c,
                    manager_id,
                    role
                )
            )
      
      
    def open_assign_requirement(self, manager_id, role):

        self.view_emp_id = manager_id
        self.view_role = role

        requirements = my_requirements(manager_id)

        if not requirements:
            messagebox.showinfo(
                "No Requirements",
                "No requirements assigned to this employee."
            )
            return

        win = ctk.CTkToplevel(self.app)
        win.title("Select Requirement")
        win.geometry("760x550")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Select Requirement",
            font=("Segoe UI",24,"bold")
        ).pack(pady=15)

        frame = ctk.CTkScrollableFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        for req in requirements:

            card = ctk.CTkFrame(frame, fg_color="white", corner_radius=10)
            card.pack(fill="x", pady=6)

            ctk.CTkLabel(
                card,
                text=req[2],
                font=("Segoe UI",15,"bold")
            ).pack(anchor="w", padx=15, pady=(10,2))

            ctk.CTkLabel(
                card,
                text=f"Client : {req[1]}",
                text_color="#2563EB"
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card,
                text=f"Budget : {req[6]} | Openings : {req[5]}",
                text_color="gray"
            ).pack(anchor="w", padx=15)

            ctk.CTkButton(
                card,
                text="Select",
                width=90,
                fg_color="#2563EB",
                command=lambda r=req: (
                setattr(self, "view_emp_id", manager_id),
                setattr(self, "view_role", role),
                win.destroy(),
                self.open_requirement_candidates(r)
            )
            ).pack(anchor="e", padx=15, pady=(0,10))  
            
            
    def assign_requirement_popup(self, manager_id, role):

        reqs = view_all_requirements()

        win = ctk.CTkToplevel(self.app)
        win.title("Assign Requirement")
        win.geometry("820x520")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Select Requirement",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=15)

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        columns = ("Client", "Requirement", "Skills", "Openings")

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=14
        )

        tree.heading("Client", text="Client")
        tree.heading("Requirement", text="Requirement")
        tree.heading("Skills", text="Skills")
        tree.heading("Openings", text="Openings")

        tree.column("Client", width=140)
        tree.column("Requirement", width=220)
        tree.column("Skills", width=220)
        tree.column("Openings", width=80, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)

        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        req_map = {}

        for r in reqs:
            item = tree.insert(
                "",
                "end",
                values=(r[1], r[2], r[3], r[5])
            )
            req_map[item] = r

        def assign():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning("Select", "Please select a requirement.")
                return

            req = req_map[selected[0]]

            assign_requirement(
                req[0],
                manager_id,
                role
            )

            messagebox.showinfo(
                "Success",
                "Requirement assigned successfully."
            )

            win.destroy()
            self.show_team_dashboard(employee_details(manager_id))

        ctk.CTkButton(
            win,
            text="Assign Requirement",
            height=42,
            fg_color="#2563EB",
            command=assign
        ).pack(fill="x", padx=20, pady=15)   
            
    # =====================================================
    # REPORTS (HEAD ONLY)
    # =====================================================

    def show_reports(self):

        if self.role != "Head":
            return

        self.clear_main()

        self.highlight_menu("Reports")
        
        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20,10))


        ctk.CTkButton(
            top,
            text="⬇ Download Data",
            fg_color=GREEN,
            hover_color="#15803D",
            command=self.download_report
        ).pack(side="right")

        ctk.CTkLabel(
            self.main,
            text="Executive Reports",
            font=("Segoe UI",28,"bold")
        ).pack(anchor="w", padx=25, pady=(25,5))

        ctk.CTkLabel(
            self.main,
            text="Visible only to Head / Admin",
            text_color=SUB
        ).pack(anchor="w", padx=25)

        body = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )
        body.pack(fill="both", expand=True, padx=25, pady=20)

        # -------- Recruiter Report --------

        left = ctk.CTkFrame(body, corner_radius=14)
        left.pack(side="left", fill="both", expand=True, padx=(0,10))

        ctk.CTkLabel(
            left,
            text="Recruiter Productivity",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=18, pady=15)

        for name,count in recruiter_report():

            row = ctk.CTkFrame(left, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(
                row,
                text=name
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=f"{count} Candidates",
                font=("Segoe UI",12,"bold"),
                text_color=PRIMARY
            ).pack(side="right")

        # -------- Client Report --------

        right = ctk.CTkFrame(body, corner_radius=14)
        right.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            right,
            text="Client Distribution",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=18, pady=15)

        for client_name,count in client_report():

            row = ctk.CTkFrame(right, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(
                row,
                text=client_name
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=str(count),
                font=("Segoe UI",12,"bold"),
                text_color=PURPLE
            ).pack(side="right")


    # =====================================================
    # SETTINGS
    # =====================================================

    def show_settings(self):

        self.clear_main()

        self.highlight_menu("Settings")

        ctk.CTkLabel(
            self.main,
            text="Settings",
            font=("Segoe UI",28,"bold")
        ).pack(anchor="w", padx=25, pady=(25,10))

        card = ctk.CTkFrame(
            self.main,
            corner_radius=14
        )
        card.pack(fill="x", padx=25, pady=10)

        def item(title,value):

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=10)

            ctk.CTkLabel(
                row,
                text=title,
                width=120,
                anchor="w",
                text_color=SUB
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=("Segoe UI",13,"bold")
            ).pack(side="left")

        item("Employee", self.user_name)
        item("Role", self.role)
        item("Employee ID", str(self.emp_id))
        item("Application", "IBOTIX CRM v1.0")

        ctk.CTkButton(
            card,
            text="Logout",
            fg_color="#DC2626",
            hover_color="#991B1B",
            command=self.logout
        ).pack(padx=18, pady=18, fill="x")         
        
    
    def build_assigned_requirements(self):

        rows = my_requirements(self.emp_id)

        if not rows:
            return

        card = ctk.CTkFrame(self.main, fg_color="white", corner_radius=12)
        card.pack(fill="x", padx=22, pady=(0,15))

        ctk.CTkLabel(
            card,
            text="My Assigned Requirements",
            font=("Segoe UI",18,"bold")
        ).pack(anchor="w", padx=15, pady=12)

        for req in rows[:3]:

            row = ctk.CTkFrame(card, fg_color="#F8FAFC", corner_radius=8)
            row.pack(fill="x", padx=15, pady=6)

            row.bind("<Button-1>", lambda e, r=req: self.open_requirement(r))

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", padx=10, pady=8)

            title = ctk.CTkLabel(
                left,
                text=req[2],
                font=("Segoe UI",13,"bold")
            )
            title.pack(anchor="w")
            title.bind("<Button-1>", lambda e, r=req: self.open_requirement(r))

            ctk.CTkLabel(
                left,
                text=f"{req[1]} • {req[3]}",
                text_color="gray"
            ).pack(anchor="w")

            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=10)

            ctk.CTkLabel(
                right,
                text=req[13],
                text_color="#16A34A",
                font=("Segoe UI",11,"bold")
            ).pack(anchor="e")
        
                
            
def show_settings(self):

    self.clear_main()
    self.highlight_menu("Settings")

    ctk.CTkLabel(
        self.main,
        text="Settings",
        font=("Segoe UI",28,"bold")
    ).pack(anchor="w", padx=25, pady=(20,10))

    card = ctk.CTkFrame(self.main, fg_color=CARD, corner_radius=14)
    card.pack(fill="x", padx=25)

    def item(label,value):

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=8)

        ctk.CTkLabel(
            row,
            text=label,
            width=130,
            anchor="w",
            text_color=SUB
        ).pack(side="left")

        ctk.CTkLabel(
            row,
            text=value,
            font=("Segoe UI",13,"bold")
        ).pack(side="left")

    item("Employee",self.user_name)
    item("Role",self.role)
    item("Employee ID",str(self.emp_id))
    item("Company","IBOTIX Pvt. Ltd.")
    item("Version","CRM v1.0")

    if self.role.lower()=="head":

        ctk.CTkButton(
            card,
            text="➕ Create Recruiter",
            fg_color=PRIMARY,
            height=42,
            command=self.create_recruiter
        ).pack(fill="x", padx=18, pady=(12,8))

    ctk.CTkButton(
        card,
        text="Logout",
        fg_color="#DC2626",
        hover_color="#991B1B",
        height=42,
        command=self.logout
    ).pack(fill="x", padx=18, pady=18)                
                








# import customtkinter as ctk
# from tkinter import ttk
# from PIL import Image
# from datetime import datetime
# import os
# import sys

# # ---------------- SRC ----------------

# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
# from database import view_candidates

# # ---------------- THEME ----------------

# PRIMARY = "#2563EB"
# BG = "#F4F7FB"
# CARD = "#FFFFFF"
# TEXT = "#111827"
# SUBTEXT = "#64748B"
# BORDER = "#E5E7EB"

# GREEN = "#16A34A"
# PURPLE = "#7C3AED"
# ORANGE = "#EA580C"
# TEAL = "#0F766E"

# ctk.set_appearance_mode("light")
# ctk.set_default_color_theme("blue")


# class Dashboard:

#     def __init__(self, user):

#         self.user = user

#         self.app = ctk.CTk()
#         self.app.title("IBOTIX Staffing Operations CRM")
#         self.app.geometry("1500x850")
#         self.app.configure(fg_color=BG)

#         self.create_topbar()
#         self.create_body()

#         self.load_candidates()

#         self.app.mainloop()

#     # ==================================================
#     # TOP NAVIGATION
#     # ==================================================

#     def create_topbar(self):

#         top = ctk.CTkFrame(
#             self.app,
#             height=70,
#             fg_color="white",
#             corner_radius=0
#         )

#         top.pack(fill="x")

#         logo_path = os.path.join(
#             os.path.dirname(__file__),
#             "..",
#             "assets",
#             "ibotix_logo.png"
#         )

#         if os.path.exists(logo_path):

#             logo = ctk.CTkImage(
#                 Image.open(logo_path),
#                 size=(150, 45)
#             )

#             ctk.CTkLabel(
#                 top,
#                 image=logo,
#                 text=""
#             ).pack(side="left", padx=20)

#         self.global_search = ctk.CTkEntry(
#             top,
#             width=300,
#             height=38,
#             corner_radius=20,
#             placeholder_text="Search candidate..."
#         )

#         self.global_search.pack(side="left", padx=30)

#         ctk.CTkButton(
#             top,
#             text="+ New Candidate",
#             width=150,
#             fg_color=GREEN,
#             hover_color="#15803D"
#         ).pack(side="right", padx=20)

#         profile = ctk.CTkFrame(
#             top,
#             fg_color="#EFF6FF",
#             corner_radius=20
#         )

#         profile.pack(side="right")

#         ctk.CTkLabel(
#             profile,
#             text=self.user[1][0],
#             width=36,
#             height=36,
#             corner_radius=18,
#             fg_color=PRIMARY,
#             text_color="white",
#             font=("Segoe UI", 16, "bold")
#         ).pack(side="left", padx=4, pady=4)

#         ctk.CTkLabel(
#             profile,
#             text=self.user[1],
#             font=("Segoe UI", 13, "bold")
#         ).pack(side="left", padx=(0, 10))

#     # ==================================================
#     # BODY
#     # ==================================================

#     def create_body(self):

#         self.body = ctk.CTkFrame(
#             self.app,
#             fg_color=BG
#         )

#         self.body.pack(fill="both", expand=True)

#         self.create_header()
#         self.create_cards()
#         self.create_table()

#     # ==================================================
#     # HEADER
#     # ==================================================

#     def create_header(self):

#         frame = ctk.CTkFrame(
#             self.body,
#             fg_color=PRIMARY,
#             corner_radius=18
#         )

#         frame.pack(fill="x", padx=25, pady=20)

#         today = datetime.now().strftime("%d %b %Y")

#         ctk.CTkLabel(
#             frame,
#             text=f"Welcome back, {self.user[1]}",
#             font=("Segoe UI", 30, "bold"),
#             text_color="white"
#         ).pack(anchor="w", padx=25, pady=(20, 0))

#         ctk.CTkLabel(
#             frame,
#             text=f"{self.user[2]}  •  {today}",
#             font=("Segoe UI", 13),
#             text_color="#DBEAFE"
#         ).pack(anchor="w", padx=25, pady=(0, 18))

#     # ==================================================
#     # KPI CARDS
#     # ==================================================

#     def create_cards(self):

#         data = view_candidates()

#         total = len(data)
#         clients = len(set(c[3] for c in data))
#         interview = sum(1 for c in data if c[4].lower() == "interview")
#         final = sum(1 for c in data if c[4].lower() == "final")

#         row = ctk.CTkFrame(self.body, fg_color="transparent")
#         row.pack(fill="x", padx=25)

#         self.card(row, "Candidates", total, PRIMARY)
#         self.card(row, "Clients", clients, PURPLE)
#         self.card(row, "Interview", interview, TEAL)
#         self.card(row, "Final", final, ORANGE)

#     def card(self, parent, title, value, color):

#         box = ctk.CTkFrame(
#             parent,
#             width=240,
#             height=115,
#             fg_color=CARD,
#             corner_radius=16,
#             border_width=1,
#             border_color=BORDER
#         )

#         box.pack(side="left", padx=8)
#         box.pack_propagate(False)

#         ctk.CTkLabel(
#             box,
#             text=title,
#             font=("Segoe UI", 13),
#             text_color=SUBTEXT
#         ).pack(anchor="w", padx=18, pady=(14, 0))

#         ctk.CTkLabel(
#             box,
#             text=str(value),
#             font=("Segoe UI", 32, "bold"),
#             text_color=color
#         ).pack(anchor="w", padx=18)

#         ctk.CTkLabel(
#             box,
#             text="▲ Live Data",
#             font=("Segoe UI", 11),
#             text_color=GREEN
#         ).pack(anchor="w", padx=18)

#     # ==================================================
#     # TABLE
#     # ==================================================

#     def create_table(self):

#         outer = ctk.CTkFrame(
#             self.body,
#             fg_color=CARD,
#             corner_radius=16,
#             border_width=1,
#             border_color=BORDER
#         )

#         outer.pack(fill="both", expand=True, padx=25, pady=20)

#         top = ctk.CTkFrame(outer, fg_color="transparent")
#         top.pack(fill="x", padx=15, pady=15)

#         ctk.CTkLabel(
#             top,
#             text="Candidate Pipeline",
#             font=("Segoe UI", 20, "bold")
#         ).pack(side="left")

#         ctk.CTkButton(
#             top,
#             text="Refresh",
#             width=90
#         ).pack(side="right")

#         style = ttk.Style()
#         style.theme_use("clam")

#         style.configure(
#             "Treeview",
#             font=("Segoe UI", 11),
#             rowheight=42,
#             background="white",
#             fieldbackground="white",
#             borderwidth=0
#         )

#         style.configure(
#             "Treeview.Heading",
#             font=("Segoe UI", 11, "bold"),
#             background="#F8FAFC",
#             foreground="#334155"
#         )

#         table_frame = ctk.CTkFrame(outer, fg_color="transparent")
#         table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

#         columns = (
#             "ID",
#             "Candidate",
#             "Skill",
#             "Client",
#             "Status"
#         )

#         self.tree = ttk.Treeview(
#             table_frame,
#             columns=columns,
#             show="headings"
#         )

#         widths = {
#             "ID": 90,
#             "Candidate": 260,
#             "Skill": 300,
#             "Client": 200,
#             "Status": 180
#         }

#         for col in columns:

#             self.tree.heading(col, text=col)
#             self.tree.column(
#                 col,
#                 width=widths[col],
#                 anchor="center"
#             )

#         self.tree.tag_configure("even", background="#FFFFFF")
#         self.tree.tag_configure("odd", background="#F8FAFC")

#         scroll = ttk.Scrollbar(
#             table_frame,
#             orient="vertical",
#             command=self.tree.yview
#         )

#         self.tree.configure(yscrollcommand=scroll.set)

#         self.tree.pack(side="left", fill="both", expand=True)
#         scroll.pack(side="right", fill="y")

#     # ==================================================
#     # LOAD DATA
#     # ==================================================

#     def load_candidates(self):

#         for row in self.tree.get_children():
#             self.tree.delete(row)

#         status_map = {
#             "submitted": "🔵 Submitted",
#             "interview": "🟡 Interview",
#             "screening": "⚪ Screening",
#             "final": "🟣 Final",
#             "on": "🟢 Active"
#         }

#         data = view_candidates()

#         for i, c in enumerate(data):

#             status = status_map.get(c[4].lower(), c[4])

#             tag = "even" if i % 2 == 0 else "odd"

#             self.tree.insert(
#                 "",
#                 "end",
#                 values=(
#                     c[0],
#                     c[1],
#                     c[2],
#                     c[3],
#                     status
#                 ),
#                 tags=(tag,)
#             )