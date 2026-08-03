# backend/app/schemas/job_match.py
from pydantic import BaseModel
from typing import List


class JobMatchRequest(BaseModel):
    candidate_id: int
    required_skills: List[str]
    job_title: str = "Target Position"


class JobMatchResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    job_title: str
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]