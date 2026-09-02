import sqlite3

conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

while True:
    print("\n========== STAFFING CRM DATABASE ==========")
    print("1. View Employees")
    print("2. View Candidates")
    print("3. Exit")

    choice = input("\nSelect option: ")

    if choice == "1":
        cursor.execute("""
        SELECT emp_id, name, email, role
        FROM employees
        ORDER BY emp_id
        """)

        print("\n--- EMPLOYEES ---")
        for row in cursor.fetchall():
            print(row)

    elif choice == "2":
        cursor.execute("""
        SELECT candidate_id, name, mobile, email,
               skill, client, status
        FROM candidates
        ORDER BY candidate_id DESC
        """)

        rows = cursor.fetchall()

        print("\n--- CANDIDATES ---")
        if rows:
            for row in rows:
                print(row)
        else:
            print("No candidates found.")

    elif choice == "3":
        break

conn.close()