import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import (
    view_candidates,
    search_candidate,
    delete_candidate,
    update_candidate_status
)


class RecruiterDashboard:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Staffing CRM - Recruiter")
        self.root.geometry("1100x620")
        self.root.configure(bg="#F4F6F8")

        self.build_sidebar()
        self.build_main()

        self.load_candidates()

        self.root.mainloop()

    # ---------------- Sidebar ---------------- #

    def build_sidebar(self):

        sidebar = tk.Frame(self.root, bg="#1E3A5F", width=180)
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar,
            text="STAFFING CRM",
            bg="#1E3A5F",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        buttons = [
            ("Refresh", self.load_candidates),
            ("Search", self.search_popup),
            ("Update", self.update_popup),
            ("Delete", self.delete_popup),
            ("Logout", self.root.destroy)
        ]

        for text, cmd in buttons:
            tk.Button(
                sidebar,
                text=text,
                command=cmd,
                bg="#274C77",
                fg="white",
                relief="flat",
                width=18,
                pady=8
            ).pack(pady=8)

    # ---------------- Main Area ---------------- #

    def build_main(self):

        main = tk.Frame(self.root, bg="#F4F6F8")
        main.pack(side="right", fill="both", expand=True)

        tk.Label(
            main,
            text="Recruiter Dashboard",
            bg="#F4F6F8",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        search_frame = tk.Frame(main, bg="#F4F6F8")
        search_frame.pack(fill="x", padx=20)

        self.search_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.search_entry.pack(side="left", fill="x", expand=True)

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_bar
        ).pack(side="left", padx=10)

        columns = ("ID", "Name", "Skill", "Client", "Status")

        self.tree = ttk.Treeview(
            main,
            columns=columns,
            show="headings",
            height=22
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160)

        self.tree.pack(fill="both", expand=True, padx=20, pady=15)

    # ---------------- Load ---------------- #

    def load_candidates(self):

        self.tree.delete(*self.tree.get_children())

        for c in view_candidates():
            self.tree.insert(
                "",
                "end",
                values=(c[0], c[1], c[2], c[3], c[4])
            )

    # ---------------- Search ---------------- #

    def search_bar(self):

        keyword = self.search_entry.get()

        self.tree.delete(*self.tree.get_children())

        for row in search_candidate(keyword):
            self.tree.insert("", "end", values=row)

    def search_popup(self):
        self.search_entry.focus()

    # ---------------- Delete ---------------- #

    def delete_popup(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a candidate")
            return

        values = self.tree.item(selected)["values"]
        candidate_id = values[0]

        delete_candidate(candidate_id)

        self.load_candidates()

        messagebox.showinfo("Success", "Candidate Deleted")

    # ---------------- Update ---------------- #

    def update_popup(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select a candidate")
            return

        values = self.tree.item(selected)["values"]

        win = tk.Toplevel(self.root)
        win.title("Update Status")
        win.geometry("300x180")

        tk.Label(win, text=f"Candidate : {values[1]}").pack(pady=10)

        status = tk.Entry(win)
        status.pack(pady=10)

        def save():

            update_candidate_status(values[0], status.get())

            self.load_candidates()

            win.destroy()

            messagebox.showinfo("Success", "Status Updated")

        tk.Button(win, text="Save", command=save).pack(pady=15)