import logging

from sqlalchemy import create_engine, Column, String, DateTime, Float, ForeignKey, JSON, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
# Create the database engine
db_url = os.environ["SQLALCHEMY_DATABASE_URI"]
engine = create_engine(db_url)

# Create a session factory
Session = sessionmaker(bind=engine)

# Create a base class for declarative models
Base = declarative_base()


class Candidate(Base):
    __tablename__ = "candidate"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    date_of_birth = Column(String(255))
    submitted_datetime = Column(DateTime)
    email = Column(String(255), unique=True)  # Add unique constraint
    phone = Column(String(255))
    cv_score = Column(Float)
    status = Column(String(255))
    interview_feedback = Column(JSON)
    cv_json = Column(JSON)
    cv_file = Column(String(255), unique=True)
    createdAt = Column(DateTime, default=datetime.utcnow())
    updatedAt = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())


Base.metadata.create_all(engine)


def list_cv_files():
    session = Session()
    candidates = session.query(Candidate).all()
    return [str(candidate.cv_file) for candidate in candidates]


def create_candidate(name, email, phone, cv_json, cv_file):
    session = Session()
    candidate = Candidate(
        cv_file=cv_file,
        name=name,
        email=email,
        phone=phone,
        cv_json=cv_json
    )
    try:
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
    except IntegrityError as e:
        session.rollback()
        candidate = None
    finally:
        session.close()
    return candidate
