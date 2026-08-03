# backend/app/models/candidate.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from app.database.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    
    # Extracted Contact Info
    candidate_name = Column(String, default="Unknown Candidate")
    email = Column(String, nullable=True)

    # Core Analysis Data
    candidate_summary = Column(Text, nullable=True)
    education = Column(JSON, nullable=True)
    technical_skills = Column(JSON, nullable=True)
    soft_skills = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    experience = Column(JSON, nullable=True)
    strengths = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    recommended_roles = Column(JSON, nullable=True)

    # Scoring & Interview
    ats_score = Column(Integer, default=0)
    ats_suggestions = Column(JSON, nullable=True)
    interview_questions = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)