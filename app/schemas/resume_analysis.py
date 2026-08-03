from pydantic import BaseModel
from typing import List, Optional

class JobMatchItem(BaseModel):
    job_title: str
    match_percentage: int
    matched_skills: List[str]
    missing_skills: List[str]

class ResumeAnalysisResponse(BaseModel):
    overall_ats_score: int
    keyword_match: int
    skill_match: int
    education_match: int
    experience_match: int
    extracted_skills: List[str]
    missing_keywords: List[str]
    job_matches: List[JobMatchItem]
    summary_feedback: str