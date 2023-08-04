from typing import List, Optional
from model import Candidate
from sqlalchemy.orm import joinedload
from dateutil import parser  # Import the dateutil.parser module
import uuid
from datetime import datetime  # Import the datetime module

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class Candidates:
    def __init__(self, database):
        self.database = database

    def create_candidate(self, request) -> Candidate:
        candidate = Candidate(
            name=request.name,
            date_of_birth=request.date_of_birth,
            submitted_datetime=request.submitted_datetime,
            email=request.email,
            phone=request.phone,
            cv_score=request.cv_score,
            job_uuid=request.job_uuid,
            status=request.status,
            interview_feedback=request.interview_feedback,
            cv_json=request.cv_json,
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

    def get_all_candidates(self, request_args) -> List[Candidate]:
        query = self.database.query(Candidate)
        page = int(request_args.get("page", 1))
        per_page = request_args.get("per_page", 20)
        search_term = request_args.get("search_term", None)
        sort_by = request_args.get("sort_by", None)
        if search_term:
            query = query.filter(
                Candidate.name.ilike(f"%{search_term}%")
                | Candidate.email.ilike(f"%{search_term}%")
                | Candidate.status.ilike(f"%{search_term}%")
                | Candidate.interview_feedback.ilike(f"%{search_term}%")
                | Candidate.cv_score.ilike(f"%{search_term}%")
            )
        if sort_by:
            sort_column = sort_by[1:] if sort_by.startswith("-") else sort_by
            order_by_func = (
                getattr(Candidate, sort_column).desc()
                if sort_by.startswith("-")
                else getattr(Candidate, sort_column)
            )
            query = query.order_by(order_by_func)
        candidates = query.offset((page - 1) * per_page).limit(per_page).all()
        return candidates

    def delete_candidate(self, candidateId: uuid.UUID) -> bool:
        candidate = self.get_candidate_by_id(candidateId)
        if candidate:
            self.database.delete(candidate)
            self.database.commit()
            return True
        else:
            return False

    def make_appointment(self, candidateId: uuid.UUID):
        candidate = self.get_candidate_by_id(candidateId)

        if candidate:
            candidate_email = candidate.email
