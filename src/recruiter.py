from employee import Employee

class Recruiter(Employee):

    def __init__(self, emp_id, name, email, password):
        super().__init__(emp_id, name, email, password, "Recruiter")
        self.interns = []
        self.candidates = []

    def add_intern(self, intern):
        self.interns.append(intern)

    def show_interns(self):
        print(f"\nRecruiter : {self.name}")
        print("Interns:")
        for intern in self.interns:
            print(f"- {intern.name}")

    def add_candidate(self, candidate):
        self.candidates.append(candidate)

    def show_candidates(self):
        print(f"\nRecruiter Dashboard : {self.name}")
        print("-" * 40)
        for c in self.candidates:
            print(f"{c.name} | {c.skill} | {c.client}")