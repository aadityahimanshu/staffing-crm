import sqlite3
import os
import re
from datetime import datetime
import smtplib
import random
from email.mime.text import MIMEText
import time
import shutil
import uuid


otp_store = {}
OTP_VALIDITY = 60      # 60 seconds

# =====================================================
# DATABASE CONNECTION
# =====================================================


DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "crm.db")
)

print("Using DB:", DB_PATH)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

JD_FOLDER = os.path.join(os.path.dirname(DB_PATH), "JD_Files")
os.makedirs(JD_FOLDER, exist_ok=True)
# =====================================================
# EMAIL CONFIGURATION
# =====================================================

SENDER_EMAIL = "himanshu.raj@ibotix.ai"

# Use your SMTP App Password here
APP_PASSWORD = "YOUR_APP_PASSWORD"
# =====================================================
# TABLES
# =====================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
    emp_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    manager_id TEXT,
    client_name TEXT,
    FOREIGN KEY(manager_id) REFERENCES employees(emp_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates(
    candidate_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    mobile TEXT,
    email TEXT,
    skill TEXT,
    experience TEXT,
    client TEXT,
    status TEXT,
    remarks TEXT,
    resume TEXT,
    uploaded_by TEXT,
    owner_id TEXT,
    created_at TEXT,
    FOREIGN KEY(uploaded_by) REFERENCES employees(emp_id),
    FOREIGN KEY(owner_id) REFERENCES employees(emp_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id INTEGER,
    candidate_id INTEGER,
    assigned_by TEXT,
    assigned_to TEXT,
    assigned_role TEXT,
    priority TEXT,
    due_date TEXT,
    task_status TEXT DEFAULT 'Assigned',
    notes TEXT,
    assigned_at TEXT,

    FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY(assigned_by) REFERENCES employees(emp_id),
    FOREIGN KEY(assigned_to) REFERENCES employees(emp_id)
)
""")

# Create requirements table only if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS requirements(
    req_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    job_title TEXT,
    skills TEXT,
    experience TEXT,
    openings INTEGER,
    budget TEXT,
    location TEXT,
    priority TEXT,
    description TEXT,
    jd_file TEXT,
    created_by TEXT,
    assigned_to TEXT,
    assigned_role TEXT,
    status TEXT DEFAULT 'Open',
    assigned_at TEXT,
    created_at TEXT,
    FOREIGN KEY(created_by) REFERENCES employees(emp_id),
    FOREIGN KEY(assigned_to) REFERENCES employees(emp_id)
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS requirements(
    req_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    job_title TEXT,
    skills TEXT,
    experience TEXT,
    openings INTEGER,
    budget TEXT,
    location TEXT,
    priority TEXT,
    description TEXT,
    created_by TEXT,
    assigned_to TEXT,
    assigned_role TEXT,
    status TEXT DEFAULT 'Open',
    assigned_at TEXT,
    created_at TEXT,
    FOREIGN KEY(created_by) REFERENCES employees(emp_id),
    FOREIGN KEY(assigned_to) REFERENCES employees(emp_id)
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS requirement_candidates(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    req_id INTEGER,
    candidate_id INTEGER,

    assigned_by TEXT,
    assigned_to TEXT,

    priority TEXT,
    status TEXT DEFAULT 'Assigned',

    assigned_at TEXT,

    FOREIGN KEY(req_id) REFERENCES requirements(req_id),
    FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS requirement_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id INTEGER,
    from_emp TEXT,
    to_emp TEXT,
    from_role TEXT,
    to_role TEXT,
    action TEXT,
    action_time TEXT
)
""")
conn.commit()

conn.commit()

try:
    cursor.execute("ALTER TABLE tasks ADD COLUMN req_id INTEGER")
    conn.commit()
except sqlite3.OperationalError:
    pass

# Add manager_id column if database already exists
try:
    cursor.execute(
        "ALTER TABLE employees ADD COLUMN manager_id TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass

# Add client_name column if database already exists
try:
    cursor.execute(
        "ALTER TABLE employees ADD COLUMN client_name TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("""
        ALTER TABLE tasks
        ADD COLUMN req_id INTEGER
    """)
    conn.commit()
except sqlite3.OperationalError:
    pass


try:
    cursor.execute(
        "ALTER TABLE requirements ADD COLUMN jd_file TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass


# =====================================================
# DEFAULT USERS
# =====================================================

cursor.execute("SELECT COUNT(*) FROM employees")
if cursor.fetchone()[0] == 0:

    users = [
    ("HEAD101","Shivali","head@ibotix.ai","Head@123","Head",None,None),

    ("AM201","Saif","saif@ibotix.ai","Saif@123","Account Manager","HEAD101","Wipro"),

    ("AM202","Harsh","harsh@ibotix.ai","Harsh@123","Account Manager","HEAD101","TCS"),

    ("AM203","Anjali","anjali@ibotix.ai","Anjali@123","Account Manager","HEAD101","Infosys"),

    ("AM204","Aishwarya","aish@ibotix.ai","Aish@123","Account Manager","HEAD101","Individual"),

    ("AM205","Manvi","manvi@ibotix.ai","Manvi@123","Account Manager","HEAD101","Persistent"),

    ("AM206","Janvi","janvi@ibotix.ai","Janvi@123","Account Manager","HEAD101","Jaipti")
    ]

    cursor.executemany(
        "INSERT INTO employees VALUES(?,?,?,?,?,?,?)",
        users
    )

    conn.commit()

# =====================================================
# LOGIN
# =====================================================

def login(email, password):

    cursor.execute("""
        SELECT emp_id, name, role
        FROM employees
        WHERE LOWER(email)=LOWER(?) AND password=?
    """, (email.strip(), password))

    return cursor.fetchone()


def view_employees():

    cursor.execute("""
    SELECT *
    FROM employees
    ORDER BY role,name
    """)

    return cursor.fetchall()

def employee_details(emp_id):

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE emp_id=?
    """,(emp_id,))

    return cursor.fetchone()


def get_team(manager_id):

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE manager_id=?
        ORDER BY role, name
    """, (manager_id,))

    return cursor.fetchall()


def get_assignable_employees(emp_id, role):
    cur = conn.cursor()

    if role == "Head":
        cursor.execute("""
            SELECT emp_id, name, role
            FROM employees
            WHERE role IN ('Account Manager','Recruiter','Intern')
            ORDER BY role, name
        """)

    elif role == "Account Manager":
        cursor.execute("""
            SELECT emp_id, name, role
            FROM employees
            WHERE emp_id = ?
               OR (manager_id = ? AND role='Recruiter')
            ORDER BY role, name
        """, (emp_id, emp_id))

    elif role == "Recruiter":
        cursor.execute("""
            SELECT emp_id, name, role
            FROM employees
            WHERE emp_id = ?
               OR (manager_id = ? AND role='Intern')
            ORDER BY role, name
        """, (emp_id, emp_id))

    elif role == "Intern":
        cursor.execute("""
            SELECT emp_id, name, role
            FROM employees
            WHERE emp_id = ?
        """, (emp_id,))

    else:
        return []

    return cursor.fetchall()


def my_requirements(emp_id):
    cursor.execute("""
        SELECT *
        FROM requirements
        WHERE assigned_to = ?
        ORDER BY req_id DESC
    """, (emp_id,))
    return cursor.fetchall()

def employee_requirement_count(emp_id):

    cursor.execute("""
    SELECT COUNT(*)
    FROM requirements
    WHERE assigned_to=?
    """, (emp_id,))

    return cursor.fetchone()[0]

def update_requirement_assignment(req_id, assigned_to, assigned_role):

    print("\n========== ASSIGN DEBUG ==========")
    print("Requirement ID :", req_id)
    print("Assigned To    :", assigned_to)
    print("Role           :", assigned_role)

    cursor.execute("""
        UPDATE requirements
        SET assigned_to = ?,
            assigned_role = ?,
            assigned_at = ?,
            status = 'Open'
        WHERE req_id = ?
    """, (
        assigned_to,
        assigned_role,
        datetime.now().strftime("%d %b %Y %I:%M %p"),
        req_id
    ))

    print("Rows Updated   :", cursor.rowcount)

    conn.commit()

    # Verify data after commit
    cursor.execute("""
        SELECT req_id, job_title, assigned_to, assigned_role, status
        FROM requirements
        WHERE req_id = ?
    """, (req_id,))

    print("Saved Record   :", cursor.fetchone())
    print("=================================\n")

    return cursor.rowcount > 0

def create_requirement(
    client_name,
    job_title,
    skills,
    experience,
    openings,
    budget,
    location,
    priority,
    description,
    created_by,
    assigned_to,
    assigned_role,
    jd_file
):
    import shutil
    import uuid

    saved_jd = None

    if jd_file and os.path.exists(jd_file):
        ext = os.path.splitext(jd_file)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        destination = os.path.join(JD_FOLDER, filename)

        shutil.copy2(jd_file, destination)
        saved_jd = destination

    cursor.execute("""
        INSERT INTO requirements(
            client_name,
            job_title,
            skills,
            experience,
            openings,
            budget,
            location,
            priority,
            description,
            jd_file,
            created_by,
            assigned_to,
            assigned_role,
            status,
            assigned_at,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client_name,
        job_title,
        skills,
        experience,
        openings,
        budget,
        location,
        priority,
        description,
        saved_jd,
        created_by,
        assigned_to,
        assigned_role,
        "Open",
        datetime.now().strftime("%d %b %Y %I:%M %p"),
        datetime.now().strftime("%d %b %Y %I:%M %p")
    ))

    conn.commit()
    return cursor.lastrowid

# Add assigned_to column
try:
    cursor.execute(
        "ALTER TABLE requirements ADD COLUMN assigned_to TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass

# Add assigned_role column
try:
    cursor.execute(
        "ALTER TABLE requirements ADD COLUMN assigned_role TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass

# Add status column
try:
    cursor.execute(
        "ALTER TABLE requirements ADD COLUMN status TEXT DEFAULT 'Open'"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass

# Add created_at column
try:
    cursor.execute(
        "ALTER TABLE requirements ADD COLUMN created_at TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass


def assign_candidate_requirement(
    req_id,
    candidate_id,
    assigned_by,
    assigned_to,
    priority
):

    cursor.execute("""
    INSERT INTO requirement_candidates(
        req_id,
        candidate_id,
        assigned_by,
        assigned_to,
        priority,
        assigned_at
    )
    VALUES(?,?,?,?,?,?)
    """,(
        req_id,
        candidate_id,
        assigned_by,
        assigned_to,
        priority,
        datetime.now().strftime("%d %b %Y %I:%M %p")
    ))

    conn.commit()
    return True




def assign_requirement(req_id, assigned_to, assigned_role):

    cursor.execute("""
        UPDATE requirements
        SET assigned_to=?,
            assigned_role=?
        WHERE req_id=?
    """, (
        assigned_to,
        assigned_role,
        req_id
    ))

    conn.commit()

def view_all_requirements():

    cursor.execute("""
                   
        SELECT *
        FROM requirements
        ORDER BY req_id DESC
    """)

    return cursor.fetchall()


def requirement_details(req_id):

    cursor.execute("""
    SELECT *
    FROM requirements
    WHERE req_id=?
    """, (req_id,))

    return cursor.fetchone()


def assign_task(req_id, candidate_id, assigned_by,
                assigned_to, assigned_role,
                priority, due_date, notes):

    cursor.execute("""
        INSERT INTO tasks (
            req_id,
            candidate_id,
            assigned_by,
            assigned_to,
            assigned_role,
            priority,
            due_date,
            task_status,
            notes,
            assigned_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req_id,
        candidate_id,
        assigned_by,
        assigned_to,
        assigned_role,
        priority,
        due_date,
        "Assigned",
        notes,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    return True
    
    
def my_tasks(emp_id):

    cursor.execute("""
        SELECT
            t.task_id,
            c.name,
            c.skill,
            c.client,
            e.name,
            t.priority,
            t.due_date,
            t.task_status
        FROM tasks t
        JOIN candidates c
            ON t.candidate_id=c.candidate_id
        JOIN employees e
            ON t.assigned_by=e.emp_id
        WHERE t.assigned_to=?
        ORDER BY t.task_id DESC
    """,(emp_id,))

    return cursor.fetchall()   


def update_task_status(task_id,status):

    cursor.execute("""
        UPDATE tasks
        SET task_status=?
        WHERE task_id=?
    """,(status,task_id))

    conn.commit() 


def employee_task_stats(emp_id):

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN task_status='Assigned' THEN 1 ELSE 0 END),
            SUM(CASE WHEN task_status='In Progress' THEN 1 ELSE 0 END),
            SUM(CASE WHEN task_status='Completed' THEN 1 ELSE 0 END)
        FROM tasks
        WHERE assigned_to=?
    """,(emp_id,))

    row = cursor.fetchone()

    return (
        row[0] or 0,
        row[1] or 0,
        row[2] or 0,
        row[3] or 0
    )
    
def team_workload(manager_id):

    cursor.execute("""
        SELECT
            e.emp_id,
            e.name,
            e.role,
            COUNT(t.task_id) as total,
            SUM(CASE WHEN t.task_status!='Completed' THEN 1 ELSE 0 END) as pending
        FROM employees e

        LEFT JOIN tasks t
        ON e.emp_id=t.assigned_to

        WHERE e.manager_id=?

        GROUP BY e.emp_id,e.name,e.role
        ORDER BY total DESC
    """,(manager_id,))

    return cursor.fetchall()



def employee_recent_tasks(emp_id):

    cursor.execute("""
        SELECT
            c.name,
            c.skill,
            c.client,
            t.priority,
            t.task_status
        FROM tasks t

        JOIN candidates c
        ON c.candidate_id=t.candidate_id

        WHERE t.assigned_to=?

        ORDER BY t.task_id DESC
        LIMIT 8
    """,(emp_id,))

    return cursor.fetchall()    

def requirement_candidates(req_id):

    cursor.execute("""
    SELECT

        c.candidate_id,
        c.name,
        c.skill,
        c.experience,

        rc.priority,
        rc.status,

        e.name,
        rc.assigned_at

    FROM requirement_candidates rc

    JOIN candidates c
        ON rc.candidate_id=c.candidate_id

    LEFT JOIN employees e
        ON rc.assigned_by=e.emp_id

    WHERE rc.req_id=?

    ORDER BY rc.id DESC
    """,(req_id,))

    return cursor.fetchall()


def my_requirement_candidates(emp_id):

    cursor.execute("""
    SELECT
        rc.candidate_id,
        r.job_title,
        c.name,
        c.skill,
        rc.priority,
        rc.status,
        rc.assigned_at
    FROM requirement_candidates rc

    JOIN requirements r
        ON rc.req_id = r.req_id

    JOIN candidates c
        ON rc.candidate_id = c.candidate_id

    WHERE rc.assigned_to = ?

    ORDER BY rc.id DESC
    """, (emp_id,))

    return cursor.fetchall()


def employee_activity(emp_id):

    cursor.execute("""
        SELECT
            c.name,
            c.client,
            t.task_status,
            t.assigned_at
        FROM tasks t

        JOIN candidates c
        ON c.candidate_id=t.candidate_id

        WHERE t.assigned_to=?

        ORDER BY t.task_id DESC
        LIMIT 10
    """,(emp_id,))

    return cursor.fetchall()


# =====================================================
# HIERARCHY MANAGEMENT
# =====================================================

def assign_manager(emp_id, manager_id):

    cursor.execute("""
        UPDATE employees
        SET manager_id=?
        WHERE emp_id=?
    """, (manager_id, emp_id))

    conn.commit()


def assign_client(emp_id, client_name):

    cursor.execute("""
        UPDATE employees
        SET client_name=?
        WHERE emp_id=?
    """, (client_name, emp_id))

    conn.commit()



# =====================================================
# PASSWORD
# =====================================================

def validate_password(password):

    if len(password)<8:
        return False

    if not re.search(r"[A-Z]",password):
        return False

    if not re.search(r"[a-z]",password):
        return False

    if not re.search(r"\d",password):
        return False

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|`~]",password):
        return False

    return True


def register_user(
    emp_id,
    name,
    email,
    password,
    role,
    manager_id=None,
    client_name=None
):

    emp_id = emp_id.strip().upper()
    email = email.strip().lower()

    if not validate_password(password):
        return "weak"

    try:
        cursor.execute("""
            INSERT INTO employees(
                emp_id,
                name,
                email,
                password,
                role,
                manager_id,
                client_name
            )
            VALUES (?,?,?,?,?,?,?)
        """, (
            emp_id,
            name.strip(),
            email,
            password,
            role,
            manager_id,
            client_name
        ))

        conn.commit()
        return "success"

    except sqlite3.IntegrityError as e:
        if "email" in str(e).lower():
            return "email_exists"
        return "duplicate"


# =====================================================
# CANDIDATES
# =====================================================

def insert_candidate(
    candidate_id,
    name,
    mobile,
    email,
    skill,
    experience,
    client,
    status,
    remarks,
    resume,
    uploaded_by,
    owner_id
):

    try:

        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO candidates(
        candidate_id,name,mobile,email,skill,
        experience,client,status,remarks,resume,
        uploaded_by,owner_id,created_at
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
            candidate_id,
            name,
            mobile,
            email,
            skill,
            experience,
            client,
            status,
            remarks,
            resume,
            uploaded_by,
            owner_id,
            created
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False


def view_candidates():

    cursor.execute("""
    SELECT *
    FROM candidates
    ORDER BY candidate_id DESC
    """)

    return cursor.fetchall()


def my_candidates(owner_id):

    cursor.execute("""
    SELECT *
    FROM candidates
    WHERE owner_id=?
    ORDER BY candidate_id DESC
    """,(owner_id,))

    return cursor.fetchall()


def search_candidate(keyword,owner_id=None):

    sql = """
    SELECT *
    FROM candidates
    WHERE (
        name LIKE ?
        OR skill LIKE ?
        OR client LIKE ?
        OR CAST(candidate_id AS TEXT) LIKE ?
    )
    """

    values = [
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ]

    if owner_id is not None:
        sql += " AND owner_id=?"
        values.append(owner_id)

    sql += " ORDER BY candidate_id DESC"

    cursor.execute(sql,values)

    return cursor.fetchall()


def update_candidate_status(candidate_id,new_status):

    cursor.execute("""
    UPDATE candidates
    SET status=?
    WHERE candidate_id=?
    """,(new_status,candidate_id))

    conn.commit()


def update_remarks(candidate_id,remarks):

    cursor.execute("""
    UPDATE candidates
    SET remarks=?
    WHERE candidate_id=?
    """,(remarks,candidate_id))

    conn.commit()


def delete_candidate(candidate_id):

    cursor.execute("""
    DELETE FROM candidates
    WHERE candidate_id=?
    """,(candidate_id,))

    conn.commit()


def get_resume(candidate_id):

    cursor.execute("""
    SELECT resume
    FROM candidates
    WHERE candidate_id=?
    """,(candidate_id,))

    return cursor.fetchone()


# =====================================================
# REPORTS
# =====================================================

def recruiter_report():

    cursor.execute("""
    SELECT e.name,
           COUNT(c.candidate_id)
    FROM employees e
    LEFT JOIN candidates c
    ON e.emp_id=c.owner_id
    WHERE e.role IN ('Recruiter','Account Manager')
    GROUP BY e.emp_id,e.name
    ORDER BY COUNT(c.candidate_id) DESC
    """)

    return cursor.fetchall()


def client_report():

    cursor.execute("""
    SELECT client,
           COUNT(*)
    FROM candidates
    GROUP BY client
    ORDER BY COUNT(*) DESC
    """)

    return cursor.fetchall()


def status_report():

    cursor.execute("""
    SELECT status,
           COUNT(*)
    FROM candidates
    GROUP BY status
    ORDER BY COUNT(*) DESC
    """)

    return cursor.fetchall()


def candidate_report():

    cursor.execute("""
    SELECT c.candidate_id,
           c.name,
           c.skill,
           c.client,
           e.name
    FROM candidates c
    LEFT JOIN employees e
    ON c.uploaded_by=e.emp_id
    ORDER BY c.candidate_id DESC
    """)

    return cursor.fetchall()


# Forget Password

def reset_password(email, old_password, new_password):

    if not validate_password(new_password):
        return "weak"

    cursor.execute("""
        SELECT * FROM employees
        WHERE email=? AND password=?
    """, (email, old_password))

    user = cursor.fetchone()

    if not user:
        return "invalid"

    cursor.execute("""
        UPDATE employees
        SET password=?
        WHERE email=?
    """, (new_password, email))

    conn.commit()
    return "success"

# =====================================================
# DATE WISE DOWNLOAD
# =====================================================

def candidates_by_date(start_date,end_date):

    cursor.execute("""
    SELECT
        candidate_id,
        name,
        mobile,
        email,
        skill,
        experience,
        client,
        status,
        remarks,
        created_at
    FROM candidates
    WHERE DATE(created_at)
          BETWEEN DATE(?) AND DATE(?)
    ORDER BY created_at DESC
    """,(start_date,end_date))

    return cursor.fetchall()



# =====================================================
# EMAIL OTP
# =====================================================


def send_otp(email):

    email = email.strip().lower()

    cursor.execute(
        "SELECT * FROM employees WHERE LOWER(email)=?",
        (email,)
    )

    if not cursor.fetchone():
        return False

    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
    "otp": otp,
    "time": time.time()
    }

    msg = MIMEText(
        f"Your Staffing CRM OTP is: {otp}\n\nValid for password reset."
    )

    msg["Subject"] = "Staffing CRM Password Reset OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = email

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        return True

    except Exception as e:
        print("SMTP ERROR:", e)
        return f"SMTP ERROR: {e}"


def verify_otp_and_reset(email, otp, new_password):

    email = email.strip().lower()

    if not validate_password(new_password):
        return "weak"

    if email not in otp_store:
        return "expired"

    data = otp_store[email]

    if time.time() - data["time"] > OTP_VALIDITY:
        del otp_store[email]
        return "expired"

    if data["otp"] != otp:
        return "invalid"

    cursor.execute(
        "UPDATE employees SET password=? WHERE LOWER(email)=?",
        (new_password, email)
    )

    conn.commit()
    del otp_store[email]

    return "success"

def add_requirement_history(
    req_id,
    from_emp,
    to_emp,
    from_role,
    to_role,
    action
):

    cursor.execute("""
    INSERT INTO requirement_history(
        req_id,
        from_emp,
        to_emp,
        from_role,
        to_role,
        action,
        action_time
    )
    VALUES(?,?,?,?,?,?,?)
    """,(
        req_id,
        from_emp,
        to_emp,
        from_role,
        to_role,
        action,
        datetime.now().strftime("%d %b %Y  %I:%M %p")
    ))

    conn.commit()
    
    
def requirement_history(req_id):

    cursor.execute("""
    SELECT *
    FROM requirement_history
    WHERE req_id=?
    ORDER BY id DESC
    """,(req_id,))

    return cursor.fetchall()    


def assigned_candidate_count(req_id):
    cursor.execute("""
        SELECT COUNT(*)
        FROM requirement_candidates
        WHERE req_id=?
    """, (req_id,))
    return cursor.fetchone()[0]

def close_requirement_if_filled(req_id):
    cursor.execute("""
        SELECT openings
        FROM requirements
        WHERE req_id=?
    """, (req_id,))
    openings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM requirement_candidates
        WHERE req_id=?
    """, (req_id,))
    assigned = cursor.fetchone()[0]

    if assigned >= openings:
        cursor.execute("""
            UPDATE requirements
            SET status='Closed'
            WHERE req_id=?
        """, (req_id,))
        conn.commit()

def requirement_progress(req_id):
    cursor.execute("""
        SELECT openings
        FROM requirements
        WHERE req_id=?
    """,(req_id,))
    openings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM requirement_candidates
        WHERE req_id=?
    """,(req_id,))
    assigned = cursor.fetchone()[0]

    return assigned, openings

def all_active_requirements():
    cursor.execute("""
        SELECT *
        FROM requirements
        ORDER BY req_id DESC
    """)
    return cursor.fetchall()


def requirement_dashboard_stats(emp_id=None, role="Head"):

    if role == "Head":
        cursor.execute("SELECT COUNT(*) FROM requirements")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requirements WHERE status='Open'")
        open_req = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requirements WHERE status='Closed'")
        closed = cursor.fetchone()[0]

    else:
        cursor.execute(
            "SELECT COUNT(*) FROM requirements WHERE assigned_to=?",
            (emp_id,)
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM requirements WHERE assigned_to=? AND status='Open'",
            (emp_id,)
        )
        open_req = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM requirements WHERE assigned_to=? AND status='Closed'",
            (emp_id,)
        )
        closed = cursor.fetchone()[0]

    if role == "Head":
        cursor.execute("SELECT COUNT(*) FROM requirement_candidates")
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM requirement_candidates WHERE assigned_to=?",
            (emp_id,)
        )

    candidates = cursor.fetchone()[0]

    return total, open_req, candidates, closed


def debug_requirements():
    cursor.execute("PRAGMA table_info(requirements)")
    print("\n--- REQUIREMENTS COLUMNS ---")
    for col in cursor.fetchall():
        print(col)

    cursor.execute("SELECT * FROM requirements")
    print("\n--- REQUIREMENTS DATA ---")
    for row in cursor.fetchall():
        print(row)



# =====================================================
# TEST
# =====================================================

if __name__=="__main__":

    print("Employees:",len(view_employees()))
    print("Candidates:",len(view_candidates()))









# import sqlite3
# import os

# BASE_DIR = os.path.dirname(__file__)
# DB_PATH = os.path.join(BASE_DIR, "..", "database", "staffing.db")

# os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()

# # ---------------- Employees Table ----------------
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS employees (
#     emp_id INTEGER PRIMARY KEY,
#     name TEXT NOT NULL,
#     email TEXT UNIQUE,
#     password TEXT NOT NULL,
#     role TEXT NOT NULL
# )
# """)

# # ---------------- Candidates Table ----------------
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS candidates(
#     candidate_id INTEGER PRIMARY KEY,
#     name TEXT NOT NULL,
#     mobile TEXT,
#     email TEXT,
#     skill TEXT,
#     experience TEXT,
#     client TEXT,
#     status TEXT,
#     remarks TEXT,
#     resume TEXT,
#     uploaded_by INTEGER,
#     owner_id INTEGER
# )
# """)

# conn.commit()
# conn.close()

# print("Database created successfully!")

# # =================================================
# # EMPLOYEE FUNCTIONS
# # =================================================

# def insert_employee(emp_id, name, email, password, role):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     INSERT OR IGNORE INTO employees
#     (emp_id, name, email, password, role)
#     VALUES (?, ?, ?, ?, ?)
#     """, (emp_id, name, email, password, role))

#     conn.commit()
#     conn.close()


# def view_employees():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM employees")
#     rows = cursor.fetchall()

#     conn.close()
#     return rows


# # =================================================
# # CANDIDATE FUNCTIONS
# # =================================================

# def insert_candidate(candidate_id, name, skill,
#                      client, status, resume, uploaded_by):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     INSERT OR IGNORE INTO candidates
#     VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (
#         candidate_id,
#         name,
#         skill,
#         client,
#         status,
#         resume,
#         uploaded_by
#     ))

#     conn.commit()
#     conn.close()


# def view_candidates():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM candidates")
#     rows = cursor.fetchall()

#     conn.close()
#     return rows

# def candidate_report():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     SELECT
#         c.candidate_id,
#         c.name,
#         c.skill,
#         c.client,
#         e.name
#     FROM candidates c
#     JOIN employees e
#         ON c.uploaded_by = e.emp_id
#     """)

#     rows = cursor.fetchall()

#     conn.close()
#     return rows

# def login(email, password):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     SELECT emp_id, name, role
#     FROM employees
#     WHERE email = ?
#     AND password = ?
#     """, (email, password))

#     user = cursor.fetchone()

#     conn.close()
#     return user

# def search_candidate(keyword):

#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT candidate_id, name, skill, client, status
#         FROM candidates
#         WHERE CAST(candidate_id AS TEXT) LIKE ?
#            OR name LIKE ?
#            OR skill LIKE ?
#            OR client LIKE ?
#     """, (
#         f"%{keyword}%",
#         f"%{keyword}%",
#         f"%{keyword}%",
#         f"%{keyword}%"
#     ))

#     rows = cursor.fetchall()
#     conn.close()
#     return rows

# def update_candidate_status(candidate_id, new_status):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#     UPDATE candidates
#     SET status = ?
#     WHERE candidate_id = ?
#     """, (new_status, candidate_id))

#     conn.commit()
#     conn.close()


# def delete_candidate(candidate_id):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute(
#         "DELETE FROM candidates WHERE candidate_id = ?",
#         (candidate_id,)
#     )

#     conn.commit()
#     conn.close()

# def insert_candidate(candidate_id, name, skill, client, status, resume, uploaded_by):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         INSERT OR IGNORE INTO candidates
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (candidate_id, name, skill, client, status, resume, uploaded_by))

#     inserted = cursor.rowcount
#     conn.commit()
#     conn.close()

#     return inserted


# # =================================================
# # TEAM LEAD REPORTS
# # =================================================

# def recruiter_report():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT
#             e.name,
#             COUNT(c.candidate_id)
#         FROM employees e
#         LEFT JOIN candidates c
#             ON e.emp_id = c.uploaded_by
#         WHERE e.role = 'Intern'
#         GROUP BY e.emp_id, e.name
#     """)

#     rows = cursor.fetchall()
#     conn.close()
#     return rows


# def client_report():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT client, COUNT(*)
#         FROM candidates
#         GROUP BY client
#         ORDER BY COUNT(*) DESC
#     """)

#     rows = cursor.fetchall()
#     conn.close()
#     return rows


# def status_report():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT status, COUNT(*)
#         FROM candidates
#         GROUP BY status
#     """)

#     rows = cursor.fetchall()
#     conn.close()
#     return rows


# def total_candidates():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("SELECT COUNT(*) FROM candidates")
#     count = cursor.fetchone()[0]

#     conn.close()
#     return count


# def total_clients():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("SELECT COUNT(DISTINCT client) FROM candidates")
#     count = cursor.fetchone()[0]

#     conn.close()
#     return count


# def total_recruiters():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT COUNT(*)
#         FROM employees
#         WHERE role='Recruiter'
#     """)

#     count = cursor.fetchone()[0]

#     conn.close()
#     return count


# def total_interns():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT COUNT(*)
#         FROM employees
#         WHERE role='Intern'
#     """)

#     count = cursor.fetchone()[0]

#     conn.close()
#     return count


# def intern_candidates(emp_id):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT candidate_id, name, skill, client, status
#         FROM candidates
#         WHERE uploaded_by = ?
#     """, (emp_id,))

#     rows = cursor.fetchall()
#     conn.close()
#     return rows


# def upload_candidate(candidate_id, name, skill,
#                      client, status, resume, uploaded_by):

#     return insert_candidate(
#         candidate_id,
#         name,
#         skill,
#         client,
#         status,
#         resume,
#         uploaded_by
#     )


# def get_resume(candidate_id):

#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT resume
#         FROM candidates
#         WHERE candidate_id = ?
#     """, (candidate_id,))

#     row = cursor.fetchone()

#     conn.close()

#     if row:
#         return row[0]
#     return None