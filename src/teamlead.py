from employee import Employee

class TeamLead(Employee):

    def __init__(self, emp_id, name, email, password):
        super().__init__(emp_id, name, email, password, "Team Lead")
        self.recruiters = []

    def add_recruiter(self, recruiter):
        self.recruiters.append(recruiter)

    def show_team(self):
        print(f"\nTeam Lead : {self.name}")
        print("=" * 45)

        for recruiter in self.recruiters:
            print(f"\nRecruiter : {recruiter.name}")

            if len(recruiter.candidates) == 0:
                print("  No candidates")
                continue

            for candidate in recruiter.candidates:
                print(f"  • {candidate.name} | {candidate.skill} | {candidate.client}")