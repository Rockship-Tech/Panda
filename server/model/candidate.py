import uuid, random, string
from datetime import datetime

from system.model_base import Base

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property


class Candidate(Base):
    __tablename__ = "candidate"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    date_of_birth = Column(String(255))
    submitted_datetime = Column(DateTime)
    email = Column(String(255), unique=True)  # Add unique constraint
    phone = Column(String(255))
    cv_score = Column(Float)
    job_uuid = Column(UUID(as_uuid=True), ForeignKey("job.uuid"))
    status = Column(String(255))
    interview_feedback = Column(JSON)
    cv_json = Column(JSON)
    createdAt = Column(DateTime, default=datetime.utcnow())
    updatedAt = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())

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

    # Establish the relationship between Candidate and Job tables
    job = relationship("Job", back_populates="candidates")

    def display(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "date_of_birth": self.date_of_birth,
            "submitted_datetime": self.submitted_datetime,
            "email": self.email,
            "phone": self.phone,
            "cv_score": self.cv_score,
            "job_uuid": self.job_uuid,
            "status": self.status,
            "interview_feedback": self.interview_feedback,
            "cv_json": self.cv_json,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
