from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, index=True, nullable=True)
    name = Column(String, index=True, nullable=True)  # Fallback for existing DB schemas
    email = Column(String, nullable=True)
    ats_score = Column(Integer, default=0)
    candidate_summary = Column(Text, nullable=True)
    extracted_skills = Column(Text, nullable=True)
    missing_keywords = Column(Text, nullable=True)
    interview_questions = Column(JSON, nullable=True)  # Restored Interview Questions
    created_at = Column(DateTime, default=datetime.utcnow)