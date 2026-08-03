import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate

router = APIRouter(tags=["Job Match"])

# Pydantic schema for match request
class JobMatchRequest(BaseModel):
    candidate_id: int
    job_title: Optional[str] = "Target Role"
    required_skills: List[str]

@router.post("/match-job")
@router.post("/api/match-job")
@router.post("/api/job-match")
def calculate_job_match(req: JobMatchRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Safe parsing helper for extracted skills
    extracted_skills_list = []
    if candidate.extracted_skills:
        if isinstance(candidate.extracted_skills, list):
            extracted_skills_list = candidate.extracted_skills
        else:
            try:
                parsed = json.loads(candidate.extracted_skills)
                extracted_skills_list = parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                extracted_skills_list = [s.strip() for s in str(candidate.extracted_skills).split(",") if s.strip()]

    # Normalize candidate skills (lowercase for case-insensitive match)
    candidate_skills_lower = {s.lower(): s for s in extracted_skills_list}

    matched_skills = []
    missing_skills = []

    # Compare against required skills provided by user
    for req_skill in req.required_skills:
        req_clean = req_skill.strip()
        if not req_clean:
            continue
        
        # Check if skill exists in candidate's extracted skills
        if req_clean.lower() in candidate_skills_lower:
            matched_skills.append(candidate_skills_lower[req_clean.lower()])
        else:
            missing_skills.append(req_clean)

    total_req = len(req.required_skills)
    match_score = int((len(matched_skills) / total_req) * 100) if total_req > 0 else 0

    return {
        "job_title": req.job_title,
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }