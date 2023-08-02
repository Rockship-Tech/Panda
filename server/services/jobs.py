from typing import List, Optional
from model import Job
from sqlalchemy.orm import joinedload
import uuid


class Jobs:
    def __init__(self, database):
        self.database = database

    def create_job(self, request) -> Job:
        job = Job(
            title=request.title,
            description=request.description,
            responsibilities=request.responsibilities,
            qualifications=request.qualifications,
            work_mode=request.work_mode,
        )
        self.database.add(job)
        self.database.commit()
        self.database.refresh(job)
        return job

    # request_args: Dict
    # example: page=3&per_page=15&search=engineer&sort_by=-updated_at
    def get_all_jobs(self, request_args) -> List[Job]:
        # Initialize the base query for the Job model
        query = self.database.query(Job)

        # Parse the request_args to extract the filtering and sorting parameters
        page = int(request_args.get("page", 1))
        per_page = int(request_args.get("per_page", 10))
        search_term = request_args.get("search_query", None)
        sort_by = request_args.get("sort_by", None)
        # Apply filtering based on the search term

        if search_term:
            query = query.filter(
                Job.title.ilike(f"%{search_term}%")
                | Job.description.ilike(f"%{search_term}%")
            )

        # Apply sorting based on the sort_by parameter
        if not sort_by:
            pass
        elif sort_by.startswith("-"):
            sort_column = sort_by[1:]
            query = query.order_by(getattr(Job, sort_column).desc())
        else:
            sort_column = sort_by
            query = query.order_by(getattr(Job, sort_column))

        # Apply pagination
        jobs = query.offset((page - 1) * per_page).limit(per_page).all()

        jobs = query.all()
        return jobs

    def get_job_by_id(self, jobId: uuid.UUID) -> Optional[Job]:
        job = self.database.query(Job).filter_by(uuid=jobId).first()
        return job

    def get_job_with_candidates(self, jobId: uuid.UUID) -> Optional[Job]:
        # Use class-bound attribute directly for joinedload
        job = (
            self.database.query(Job)
            .options(joinedload(Job.candidates))
            .filter_by(uuid=jobId)
            .first()
        )
        return job

    def delete_job(self, jobId: uuid.UUID):
        pass

    def update_job(self, jobId: uuid.UUID, request) -> Optional[Job]:
        # Retrieve the job from the database
        job = self.get_job_by_id(jobId)

        if job:
            # Update the job attributes with the new values from the request
            job.title = request["title"]
            job.description = request["description"]
            job.responsibilities = request["responsibilities"]
            job.qualifications = request["qualifications"]
            job.work_mode = request["work_mode"]

            # Save the changes to the database
            self.database.commit()
            self.database.refresh(job)

            return job
        else:
            # Job with the given jobId not found
            return None
