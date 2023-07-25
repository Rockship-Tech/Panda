import uuid, random, string
from datetime import datetime

from ..system.model_base import Base

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property


class Job(Base):
    __tablename__ = "job"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    description = Column(Text)
    responsibilities = Column(Text)
    qualifications = Column(Text)
    work_mode = Column(String(255))
    createdAt = Column(DateTime, default=datetime.utcnow())
    updatedAt = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())

    candidate = relationship("Candidate", back_populates="job")

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

    def display(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "qualifications": self.qualifications,
            "work_mode": self.work_mode,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }
