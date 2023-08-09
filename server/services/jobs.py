from typing import List, Optional
from model import Job
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, aliased
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
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    Job.title.ilike(search_pattern),
                    Job.description.ilike(search_pattern),
                )
            )

        # Apply sorting based on the sort_by parameter
        if sort_by:
            sort_column = sort_by[1:] if sort_by.startswith("-") else sort_by
            order_by_func = (
                getattr(Job, sort_column).desc()
                if sort_by.startswith("-")
                else getattr(Job, sort_column)
            )
            query = query.order_by(order_by_func)

        offset = (page - 1) * per_page

        jobs = query.limit(per_page).offset(offset).all()

        total_jobs = query.count()

        return jobs, total_jobs

    def get_job_by_id(self, jobId: uuid.UUID) -> Optional[Job]:
        job = self.database.query(Job).filter_by(uuid=jobId).first()
        return job

    def get_job_by_name(self, job_name: str) -> Optional[Job]:
        job = self.database.query(Job).filter_by(title=job_name).first()
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
