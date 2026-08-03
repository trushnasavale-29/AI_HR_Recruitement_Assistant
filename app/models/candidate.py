from sqlalchemy import Column, Integer, String, JSON, Text
from app.database.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    ats_score = Column(Integer, default=0)
    keyword_match = Column(Integer, default=0)
    skill_match = Column(Integer, default=0)
    education_match = Column(Integer, default=0)
    experience_match = Column(Integer, default=0)
    
    # Store dynamic lists and match cards directly in JSON
    extracted_skills = Column(JSON, default=[])
    missing_keywords = Column(JSON, default=[])
    job_matches = Column(JSON, default=[])
    summary_feedback = Column(Text, nullable=True)