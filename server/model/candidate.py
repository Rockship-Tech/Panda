import uuid, random, string
from datetime import datetime

from .db import Base

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property


class Candidate(Base):
    __tablename__ = "candidate"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    date_of_birth = Column(String(255))
    submited_datetime = Column(DateTime)
    email = Column(String(255), unique=True)  # Add unique constraint
    phone = Column(String(255))
    cv_score = Column(Integer)
    job_id = Column(Integer, ForeignKey("job.id"))
    status = Column(String(255)) #VARCHAR(255) values can be: cv_received | interview_request_sent | interviewed | offered |accepted
    interview_feedback = Column(JSON)
                    #     JSONB
                    # {
                    # "skill": 8,
                    # "communication": 7
                    # "attitude": 6
                    # }
                    
    job = relationship("Job", back_populates="candidate")