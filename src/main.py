import os
import shutil

from database import (
    insert_employee,
    view_employees,
    insert_candidate,
    view_candidates,
    candidate_report,
    login,
    search_candidate,
    update_candidate_status,
    delete_candidate,
    recruiter_report,
    client_report,
    status_report,
    intern_candidates,
    upload_candidate,
    get_resume
)

from recruiter import Recruiter
from intern import Intern
from candidate import Candidate
from teamlead import TeamLead
from head import Head

# ==================================================
# EMPLOYEES
# ==================================================

raj = Recruiter(201, "Raj", "raj@company.com", "raj123")
priya = TeamLead(301, "Priya", "priya@company.com", "priya123")

ravi = Intern(401, "Ravi", "ravi@company.com", "ravi123")
simran = Intern(402, "Simran", "simran@company.com", "sim123")

insert_employee(201, "Raj", "raj@company.com", "raj123", "Recruiter")
insert_employee(301, "Priya", "priya@company.com", "priya123", "Team Lead")
insert_employee(401, "Ravi", "ravi@company.com", "ravi123", "Intern")
insert_employee(402, "Simran", "simran@company.com", "sim123", "Intern")

# ==================================================
# RELATIONSHIPS
# ==================================================

raj.add_intern(ravi)
raj.add_intern(simran)
priya.add_recruiter(raj)

# ==================================================
# RESUME PATH
# ==================================================

BASE_DIR = os.path.dirname(__file__)
resume_path = os.path.join(BASE_DIR, "..", "uploads", "rahul_resume.pdf")

# ==================================================
# DEFAULT CANDIDATES
# ==================================================

insert_candidate(
    1001,
    "Rahul Verma",
    "9876543210",
    "rahul@email.com",
    "Python",
    "2 Years",
    "TCS",
    "Submitted",
    "Good communication",
    resume_path,
    401,      # uploaded by Ravi
    201       # owner Raj
)

insert_candidate(1002, "Anjali Singh", "SQL",
                 "Infosys", "Interview", resume_path, 401)

insert_candidate(1003, "Mohit Kumar", "Java",
                 "Wipro", "Screening", resume_path, 402)

candidate1 = Candidate(
    1001, "Rahul Verma", "Python",
    "TCS", "Submitted", resume_path, ravi
)

candidate2 = Candidate(
    1002, "Anjali Singh", "SQL",
    "Infosys", "Interview", resume_path, ravi
)

candidate3 = Candidate(
    1003, "Mohit Kumar", "Java",
    "Wipro", "Screening", resume_path, simran
)

raj.add_candidate(candidate1)
raj.add_candidate(candidate2)
raj.add_candidate(candidate3)

# ==================================================
# HEAD
# ==================================================

amit = Head(1, "Amit Sharma", "amit@company.com", "amit123")
amit.add_team_lead(priya)

# ==================================================
# INITIAL OUTPUT
# ==================================================

raj.show_interns()

print("\nCandidate Details")
print("-" * 40)
candidate1.display()

priya.show_team()
amit.dashboard()

print("\nEMPLOYEES IN SQLITE")
print("=" * 40)
for emp in view_employees():
    print(emp)

print("\nCANDIDATES IN SQLITE")
print("=" * 40)
for cand in view_candidates():
    print(cand)

print("\nSQL JOIN REPORT")
print("=" * 50)
for row in candidate_report():
    print(row)

# ==================================================
# LOGIN
# ==================================================

print("\nLOGIN")
print("=" * 40)

email = input("Email    : ")
password = input("Password : ")

user = login(email, password)

# ==================================================
# ROLE BASED ACCESS
# ==================================================

if user:

    print("\nLogin Successful!")
    print(f"Welcome {user[1]}")
    print(f"Role : {user[2]}")

    role = user[2]

    # ==================================================
    # RECRUITER MENU
    # ==================================================

    if role == "Recruiter":

        while True:

            print("\n========== RECRUITER MENU ==========")
            print("1. View Candidates")
            print("2. Add Candidate")
            print("3. Search Candidate")
            print("4. Update Status")
            print("5. Delete Candidate")
            print("6. View Resume")
            print("7. Logout")

            choice = input("\nChoose (1-7): ").strip()

            if choice not in ["1", "2", "3", "4", "5", "6", "7"]:
                print("Please choose a number between 1 and 7.")
                continue

            # 1 View
            if choice == "1":

                print("\nRecruiter Dashboard : Raj")
                print("-" * 50)

                candidates = view_candidates()

                if candidates:
                    for c in candidates:
                        print(f"{c[1]} | {c[2]} | {c[3]} | {c[4]}")
                else:
                    print("No candidates found.")

            # 2 Add
            elif choice == "2":

                print("\nADD NEW CANDIDATE")
                print("-" * 30)

                while True:
                    try:
                        candidate_id = int(input("Candidate ID : "))
                        break
                    except ValueError:
                        print("Please enter numeric ID.")

                name = input("Name         : ")
                skill = input("Skill        : ")
                client = input("Client       : ")
                status = input("Status       : ")

                result = insert_candidate(
                    candidate_id,
                    name,
                    skill,
                    client,
                    status,
                    resume_path,
                    401
                )

                if result:
                    print("\nCandidate Added Successfully!")
                else:
                    print("\nCandidate ID already exists!")

            # 3 Search
            elif choice == "3":

                keyword = input("\nEnter Name / Skill / Client : ")

                results = search_candidate(keyword)

                print("\nSEARCH RESULTS")
                print("-" * 45)

                if results:
                    for row in results:
                        print(
                            f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}"
                        )
                else:
                    print("No candidate found.")

            # 4 Update
            elif choice == "4":

                candidate_id = int(input("Candidate ID : "))
                new_status = input("New Status : ")

                update_candidate_status(candidate_id, new_status)

                print("\nStatus Updated Successfully!")

            # 5 Delete
            elif choice == "5":

                candidate_id = int(input("Candidate ID : "))

                delete_candidate(candidate_id)

                print("\nCandidate Deleted Successfully!")
                
                
            # 6 View Resume
            elif choice == "6":

                candidate_id = int(input("Candidate ID : "))

                resume = get_resume(candidate_id)

                if resume and os.path.exists(resume):

                   print("\nOpening Resume...")
                   os.startfile(resume)      # Windows only

                else:
                   print("Resume not found.") 
                   
            # 7 Logout
            elif choice == "7":

                print("\nLogged Out Successfully!")
                break

            else:
                print("Invalid Choice")

    # ==================================================
    # TEAM LEAD MENU
    # ==================================================

    elif role == "Team Lead":

        while True:

            print("\n========== TEAM LEAD MENU ==========")
            print("1. Recruiter Report")
            print("2. View All Candidates")
            print("3. Client Report")
            print("4. Status Report")
            print("5. Logout")

            choice = input("\nChoose (1-5): ").strip()

            if choice not in ["1", "2", "3", "4", "5"]:
               print("Please choose a number between 1 and 5.")
               continue

            if choice == "1":

                print("\nRECRUITER REPORT")
                print("-" * 35)

                for row in recruiter_report():
                    print(f"{row[0]} : {row[1]} candidates")

            elif choice == "2":

                print("\nALL CANDIDATES")
                print("-" * 50)

                for row in candidate_report():
                    print(
                        f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}"
                    )

            elif choice == "3":

                print("\nCLIENT REPORT")
                print("-" * 35)

                for row in client_report():
                    print(f"{row[0]} : {row[1]}")

            elif choice == "4":

                print("\nSTATUS REPORT")
                print("-" * 35)

                for row in status_report():
                    print(f"{row[0]} : {row[1]}")

            elif choice == "5":

                print("\nLogged Out Successfully!")
                break

            else:
                print("Invalid Choice")

    # ==================================================
    # HEAD MENU
    # ==================================================

    elif role == "Head":

        while True:

            print("\n========== HEAD MENU ==========")
            print("1. Dashboard")
            print("2. Recruiter Report")
            print("3. Client Report")
            print("4. Status Report")
            print("5. Logout")

            choice = input("\nChoose (1-5): ").strip()

            if choice not in ["1", "2", "3", "4", "5"]:
                print("Please choose a number between 1 and 5.")
                continue

            if choice == "1":

                amit.dashboard()

            elif choice == "2":

                print("\nRECRUITER REPORT")
                print("-" * 35)

                for row in recruiter_report():
                    print(f"{row[0]} : {row[1]} candidates")

            elif choice == "3":

                print("\nCLIENT REPORT")
                print("-" * 35)

                for row in client_report():
                    print(f"{row[0]} : {row[1]}")

            elif choice == "4":

                print("\nSTATUS REPORT")
                print("-" * 35)

                for row in status_report():
                    print(f"{row[0]} : {row[1]}")

            elif choice == "5":

                print("\nLogged Out Successfully!")
                break

            else:
                print("Invalid Choice")

    # ==================================================
    # INTERN MENU
    # ==================================================

    elif role == "Intern":

     while True:

        print("\n========== INTERN MENU ==========")
        print("1. Upload Candidate")
        print("2. My Uploaded Candidates")
        print("3. Search Candidate")
        print("4. Logout")

        choice = input("\nChoose (1-4): ").strip()

        if choice == "1":

            print("\nUPLOAD NEW CANDIDATE")
            print("-" * 35)

            while True:
                try:
                    candidate_id = int(input("Candidate ID : "))
                    break
                except ValueError:
                    print("Enter numeric ID.")

            name = input("Name         : ")
            skill = input("Skill        : ")
            client = input("Client       : ")
            status = input("Status       : ")

            pdf_path = input("Resume PDF Path : ")

            if not os.path.exists(pdf_path):
                print("Resume file not found!")
                continue

            if not pdf_path.lower().endswith(".pdf"):
                print("Only PDF files are allowed!")
                continue

            filename = os.path.basename(pdf_path)
            destination = os.path.join(BASE_DIR, "..", "uploads", filename)

            shutil.copy(pdf_path, destination)

            result = upload_candidate(
                candidate_id,
                name,
                skill,
                client,
                status,
                destination,
                user[0]
            )

            if result:
                print("\nCandidate Uploaded Successfully!")
            else:
                print("\nCandidate ID already exists!")

        elif choice == "2":

            print("\nMY UPLOADED CANDIDATES")
            print("-" * 45)

            rows = intern_candidates(user[0])

            if rows:
                for r in rows:
                    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
            else:
                print("No candidates uploaded.")

        elif choice == "3":

            keyword = input("\nEnter keyword : ")

            results = search_candidate(keyword)

            if results:
                print("\nSEARCH RESULTS")
                print("-" * 45)
                for r in results:
                    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
            else:
                print("No candidate found.")

        elif choice == "4":
            print("\nLogged Out Successfully!")
            break

        else:
            print("Invalid Choice")









# import os

# from database import (
#     insert_employee,
#     view_employees,
#     insert_candidate,
#     view_candidates,
#     candidate_report,
#     login,
#     search_candidate,
#     update_candidate_status,
#     delete_candidate,
#     recruiter_report,
#     client_report,
#     status_report
# )

# from recruiter import Recruiter
# from intern import Intern
# from candidate import Candidate
# from teamlead import TeamLead
# from head import Head

# # ==================================================
# # EMPLOYEES
# # ==================================================

# raj = Recruiter(201, "Raj", "raj@company.com", "raj123")
# priya = TeamLead(301, "Priya", "priya@company.com", "priya123")

# ravi = Intern(401, "Ravi", "ravi@company.com", "ravi123")
# simran = Intern(402, "Simran", "simran@company.com", "sim123")

# insert_employee(201, "Raj", "raj@company.com", "raj123", "Recruiter")
# insert_employee(301, "Priya", "priya@company.com", "priya123", "Team Lead")
# insert_employee(401, "Ravi", "ravi@company.com", "ravi123", "Intern")
# insert_employee(402, "Simran", "simran@company.com", "sim123", "Intern")

# # ==================================================
# # RELATIONSHIPS
# # ==================================================

# raj.add_intern(ravi)
# raj.add_intern(simran)
# priya.add_recruiter(raj)

# # ==================================================
# # RESUME PATH
# # ==================================================

# BASE_DIR = os.path.dirname(__file__)
# resume_path = os.path.join(BASE_DIR, "..", "uploads", "rahul_resume.pdf")

# # ==================================================
# # DEFAULT CANDIDATES
# # ==================================================

# insert_candidate(1001, "Rahul Verma", "Python",
#                  "TCS", "Submitted", resume_path, 401)

# insert_candidate(1002, "Anjali Singh", "SQL",
#                  "Infosys", "Interview", resume_path, 401)

# insert_candidate(1003, "Mohit Kumar", "Java",
#                  "Wipro", "Screening", resume_path, 402)

# candidate1 = Candidate(
#     1001, "Rahul Verma", "Python",
#     "TCS", "Submitted", resume_path, ravi
# )

# candidate2 = Candidate(
#     1002, "Anjali Singh", "SQL",
#     "Infosys", "Interview", resume_path, ravi
# )

# candidate3 = Candidate(
#     1003, "Mohit Kumar", "Java",
#     "Wipro", "Screening", resume_path, simran
# )

# raj.add_candidate(candidate1)
# raj.add_candidate(candidate2)
# raj.add_candidate(candidate3)

# # ==================================================
# # HEAD
# # ==================================================

# # ==================================================
# # HEAD MENU
# # ==================================================

# elif role == "Head":

# while True:

# print("\n========== HEAD MENU ==========")
# print("1. Dashboard")
# print("2. Recruiter Report")
# print("3. Client Report")
# print("4. Status Report")
# print("5. Logout")

# choice = input("\nChoose : ")

# if choice == "1":

#     amit.dashboard()

# elif choice == "2":

#     print("\nRECRUITER REPORT")
#     print("-" * 35)

#     for row in recruiter_report():
#         print(f"{row[0]} : {row[1]} candidates")

# elif choice == "3":

#     print("\nCLIENT REPORT")
#     print("-" * 35)

#     for row in client_report():
#         print(f"{row[0]} : {row[1]}")

# elif choice == "4":

#     print("\nSTATUS REPORT")
#     print("-" * 35)

#     for row in status_report():
#         print(f"{row[0]} : {row[1]}")

# elif choice == "5":

#     print("\nLogged Out Successfully!")

# else:
#     print("Invalid Choice")
# # ==================================================
# # INITIAL DASHBOARD
# # ==================================================

# raj.show_interns()

# print("\nCandidate Details")
# print("-" * 40)
# candidate1.display()

# priya.show_team()
# amit.dashboard()

# # ==================================================
# # SQLITE OUTPUT
# # ==================================================

# print("\nEMPLOYEES IN SQLITE")
# print("=" * 40)
# for emp in view_employees():
#     print(emp)

# print("\nCANDIDATES IN SQLITE")
# print("=" * 40)
# for cand in view_candidates():
#     print(cand)

# print("\nSQL JOIN REPORT")
# print("=" * 50)
# for row in candidate_report():
#     print(row)

# # ==================================================
# # LOGIN
# # ==================================================

# print("\nLOGIN")
# print("=" * 40)

# email = input("Email    : ")
# password = input("Password : ")

# user = login(email, password)

# if user:

#     print("\nLogin Successful!")
#     print(f"Welcome {user[1]}")
#     print(f"Role : {user[2]}")

#     role = user[2]

# # ==================================================
# # RECRUITER MENU
# # ==================================================

# if role == "Recruiter":

#     while True:

#         print("\n========== RECRUITER MENU ==========")
#         print("1. View Candidates")
#         print("2. Add Candidate")
#         print("3. Search Candidate")
#         print("4. Update Status")
#         print("5. Delete Candidate")
#         print("6. Logout")

#         choice = input("\nChoose : ")

#         if choice == "1":

#             print("\nRecruiter Dashboard : Raj")
#             print("-" * 50)

#             candidates = view_candidates()

#             if candidates:
#                 for c in candidates:
#                     print(f"{c[1]} | {c[2]} | {c[3]} | {c[4]}")
#             else:
#                 print("No candidates found.")

#         elif choice == "2":

#             print("\nADD NEW CANDIDATE")
#             print("-" * 30)

#             while True:
#                 try:
#                     candidate_id = int(input("Candidate ID : "))
#                     break
#                 except ValueError:
#                     print("Please enter numeric ID.")

#             name = input("Name         : ")
#             skill = input("Skill        : ")
#             client = input("Client       : ")
#             status = input("Status       : ")

#             result = insert_candidate(
#                 candidate_id,
#                 name,
#                 skill,
#                 client,
#                 status,
#                 resume_path,
#                 401
#             )

#             if result:
#                 print("\nCandidate Added Successfully!")
#             else:
#                 print("\nCandidate ID already exists!")

#         elif choice == "3":

#             keyword = input("\nEnter Name / Skill / Client : ")
#             results = search_candidate(keyword)

#             print("\nSEARCH RESULTS")
#             print("-" * 45)

#             if results:
#                 for row in results:
#                     print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
#             else:
#                 print("No candidate found.")

#         elif choice == "4":

#             candidate_id = int(input("Candidate ID : "))
#             new_status = input("New Status : ")

#             update_candidate_status(candidate_id, new_status)
#             print("\nStatus Updated Successfully!")

#         elif choice == "5":

#             candidate_id = int(input("Candidate ID : "))
#             delete_candidate(candidate_id)
#             print("\nCandidate Deleted Successfully!")

#         elif choice == "6":

#             print("\nLogged Out Successfully!")
#             break

#         else:
#             print("Invalid Choice")

# # ==================================================
# # TEAM LEAD MENU
# # ==================================================

# elif role == "Team Lead":

#     while True:

#         print("\n========== TEAM LEAD MENU ==========")
#         print("1. Recruiter Report")
#         print("2. View All Candidates")
#         print("3. Client Report")
#         print("4. Status Report")
#         print("5. Logout")

#         choice = input("\nChoose : ")

#         if choice == "1":

#             print("\nRECRUITER REPORT")
#             print("-" * 35)

#             for row in recruiter_report():
#                 print(f"{row[0]} : {row[1]} candidates")

#         elif choice == "2":

#             print("\nALL CANDIDATES")
#             print("-" * 50)

#             for row in candidate_report():
#                 print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")

#         elif choice == "3":

#             print("\nCLIENT REPORT")
#             print("-" * 35)

#             for row in client_report():
#                 print(f"{row[0]} : {row[1]}")

#         elif choice == "4":

#             print("\nSTATUS REPORT")
#             print("-" * 35)

#             for row in status_report():
#                 print(f"{row[0]} : {row[1]}")

#         elif choice == "5":

#             print("\nLogged Out Successfully!")
#             break

#         else:
#             print("Invalid Choice")

# # ==================================================
# # HEAD MENU
# # ==================================================

# elif role == "Head":

#     while True:

#         print("\n========== HEAD MENU ==========")
#         print("1. Dashboard")
#         print("2. Recruiter Report")
#         print("3. Client Report")
#         print("4. Status Report")
#         print("5. Logout")

#         choice = input("\nChoose : ")

#         if choice == "1":

#             amit.dashboard()

#         elif choice == "2":

#             print("\nRECRUITER REPORT")
#             print("-" * 35)

#             for row in recruiter_report():
#                 print(f"{row[0]} : {row[1]} candidates")

#         elif choice == "3":

#             print("\nCLIENT REPORT")
#             print("-" * 35)

#             for row in client_report():
#                 print(f"{row[0]} : {row[1]}")

#         elif choice == "4":

#             print("\nSTATUS REPORT")
#             print("-" * 35)

#             for row in status_report():
#                 print(f"{row[0]} : {row[1]}")

#         elif choice == "5":

#             print("\nLogged Out Successfully!")
#             break

#         else:
#             print("Invalid Choice")

# # ==================================================
# # INTERN MENU
# # ==================================================

# elif role == "Intern":

#     print("\n========== INTERN DASHBOARD ==========")
#     raj.show_interns()

# else:
#    print("\nInvalid Email or Password")