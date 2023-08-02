from typing import List, Optional
from model import Candidate
from sqlalchemy.orm import joinedload
import uuid


class Candidates:
    def __init__(self, database):
        self.database = database

    def create_candidate(self, request) -> Candidate:
        candidate = Candidate(
            name=request.name,
            date_of_birth=request.date_of_birth,
            submited_datetime=request.submited_datetime,
            email=request.email,
            phone=request.phone,
            cv_score=request.cv_score,
            job_uuid=request.job_uuid,
            status=request.status,
            interview_feedback=request.interview_feedback,
        )
        self.database.add(candidate)
        self.database.commit()
        self.database.refresh(candidate)
        return candidate

    def get_candidate_by_id(self, candidateId: uuid.UUID) -> Optional[Candidate]:
        candidate = self.database.query(Candidate).filter_by(uuid=candidateId).first()
        return candidate

    def update_candidate(self, candidateId: uuid.UUID, request) -> Optional[Candidate]:
        # Retrieve the candidate from the database
        candidate = self.get_candidate_by_id(candidateId)

        if candidate:
            # Update the candidate attributes with the new values from the request
            candidate.title = request["title"]
            candidate.description = request["description"]
            candidate.responsibilities = request["responsibilities"]
            candidate.qualifications = request["qualifications"]
            candidate.work_mode = request["work_mode"]

            # Save the changes to the database
            self.database.commit()
            self.database.refresh(candidate)

            return candidate
        else:
            # candidate with the given candidateId not found
            return None
