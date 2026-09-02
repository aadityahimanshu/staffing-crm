from employee import Employee
from database import view_employees, view_candidates


class Head(Employee):

    def __init__(self, emp_id, name, email, password):
        super().__init__(emp_id, name, email, password, "Head")
        self.team_leads = []

    def add_team_lead(self, tl):
        self.team_leads.append(tl)

    def dashboard(self):

        employees = view_employees()
        candidates = view_candidates()

        team_leads = sum(1 for e in employees if e[4] == "Team Lead")
        recruiters = sum(1 for e in employees if e[4] == "Recruiter")
        interns = sum(1 for e in employees if e[4] == "Intern")
        clients = len(set(c[3] for c in candidates))

        print("\nHEAD DASHBOARD")
        print("=" * 40)
        print(f"Team Leads       : {team_leads}")
        print(f"Recruiters       : {recruiters}")
        print(f"Interns          : {interns}")
        print(f"Candidates       : {len(candidates)}")
        print(f"Active Clients   : {clients}")