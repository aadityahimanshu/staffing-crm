from employee import Employee

class Intern(Employee):

    def __init__(self, emp_id, name, email, password):
        super().__init__(emp_id, name, email, password, "Intern")