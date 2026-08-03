# backend/app/schemas/candidate.py
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class CandidateResponse(BaseModel):
    id: int
    filename: str
    candidate_name: Optional[str] = "Unknown Candidate"
    email: Optional[str] = None
    candidate_summary: Optional[str] = "No summary available"
    education: Optional[List[Any]] = []
    technical_skills: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    projects: Optional[List[Any]] = []
    experience: Optional[List[Any]] = []
    strengths: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []
    recommended_roles: Optional[List[str]] = []
    ats_score: Optional[int] = 0
    ats_suggestions: Optional[List[str]] = []
    interview_questions: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True