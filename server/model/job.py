import uuid, random, string
from datetime import datetime

from .db import Base

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property


class Job(Base):
    __tablename__ = "job"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(Text)
    responsibilities = Column(Text)
    qualifications = Column(Text)
    work_mode = Column(String(255))
    
    candidate = relationship("Candidate", back_populates="job")