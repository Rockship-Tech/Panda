import uuid, random, string
from datetime import datetime

from system.model_base import Base

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event
from model import candidate as Candidate


class Job(Base):
    __tablename__ = "job"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    description = Column(Text)
    responsibilities = Column(Text)
    qualifications = Column(Text)
    work_mode = Column(String(255))
    createdAt = Column(DateTime, default=datetime.utcnow())
    updatedAt = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())

    candidates = relationship(
        "Candidate", back_populates="job", cascade="all, delete-orphan"
    )

    @hybrid_property
    def created_at(self):
        return self.createdAt

    @created_at.setter
    def created_at(self, value):
        self.createdAt = value

    @hybrid_property
    def updated_at(self):
        return self.updatedAt

    @updated_at.setter
    def updated_at(self, value):
        self.updatedAt = value

    def display(self, with_candidates=False):
        job_data = {
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "qualifications": self.qualifications,
            "work_mode": self.work_mode,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
        if with_candidates:
            job_data["candidates"] = [
                candidate.display() for candidate in self.candidates
            ]
        return job_data


@event.listens_for(Job, "before_delete")
def set_candidates_job_id_to_default(mapper, connection, target):
    """Event listener to set jobId of candidates to a default value when a job is deleted."""
    default_job_id = "0"

    # Update jobId of associated candidates to the default value
    connection.execute(
        Candidate.__table__.update()
        .where(Candidate.job_id == target.uuid)
        .values(job_id=default_job_id)
    )
