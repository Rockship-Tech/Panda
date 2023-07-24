from typing import List, Optional
from ..model import Job


def create_job(request, database) -> Job:
    job = Job(
        title=request.title,
        description=request.description,
        responsibilities=request.responsibilities,
        qualifications=request.qualifications,
        work_mode=request.work_mode,
    )
    database.add(job)
    database.commit()
    database.refresh(job)
    return job


def get_job_by_id(database, jobId: int) -> Optional[Job]:
    job = database.query(Job).filter_by(id=jobId).first()
    return job


def get_all_job(database) -> List[Job]:
    jobs = database.query(Job).all()
    return jobs


def display_job(Job):
    return {
        "id": Job.id,
        "title": Job.title,
        "description": Job.description,
        "responsibilities": Job.responsibilities,
        "qualifications": Job.qualifications,
        "work_mode": Job.work_mode,
    }
