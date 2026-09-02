class Employee:

    def __init__(self, emp_id, name, email, password, role):
        self.emp_id = emp_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def display(self):
        print(f"ID       : {self.emp_id}")
        print(f"Name     : {self.name}")
        print(f"Email    : {self.email}")
        print(f"Role     : {self.role}")


if __name__ == "__main__":
    emp1 = Employee(
        101,
        "Himanshu",
        "himanshu@company.com",
        "him123",
        "Recruiter"
    )

    emp1.display()