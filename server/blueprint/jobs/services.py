from typing import List, Optional
from ...model import Job 


def create_job(request, database) -> Job:
    job = Job(
        title = request.title,
        description = request.description,
        responsibilities = request.responsibilities,
        qualifications = request.qualifications,
        work_mode = request.work_mode
    )
    database.add(job)
    database.commit()
    database.refresh(job)
    return job

def get_all_job(database) -> List[Job]:
    jobs = database.query(Job).all()
    return jobs