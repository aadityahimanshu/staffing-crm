import os


class Candidate:

    def __init__(
        self,
        candidate_id,
        name,
        skill,
        client,
        status,
        resume,
        uploaded_by,
        mobile="",
        email="",
        experience="",
        remarks=""
    ):
        self.candidate_id = candidate_id
        self.name = name
        self.mobile = mobile
        self.email = email
        self.skill = skill
        self.experience = experience
        self.client = client
        self.status = status
        self.remarks = remarks
        self.resume = resume
        self.uploaded_by = uploaded_by

    def display(self):
        print(f"\nCandidate ID : {self.candidate_id}")
        print(f"Name         : {self.name}")
        print(f"Mobile       : {self.mobile}")
        print(f"Email        : {self.email}")
        print(f"Skill        : {self.skill}")
        print(f"Experience   : {self.experience}")
        print(f"Client       : {self.client}")
        print(f"Status       : {self.status}")
        print(f"Remarks      : {self.remarks}")

        if self.resume and os.path.exists(self.resume):
            print("Resume       : Available")
        else:
            print("Resume       : Missing")

        print(f"Uploaded By  : {self.uploaded_by}")