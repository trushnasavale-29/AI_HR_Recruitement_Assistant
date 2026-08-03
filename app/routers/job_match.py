# backend/app/routers/job_match.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.job_match import JobMatchRequest, JobMatchResponse
from app.services.job_matcher import calculate_job_match

router = APIRouter(tags=["Job Matching"])


@router.post("/match-job", response_model=JobMatchResponse)
def match_candidate_to_job(request: JobMatchRequest, db: Session = Depends(get_db)):
    """Calculate match percentage between a candidate and required job skills"""
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate_skills = candidate.technical_skills or []
    match_result = calculate_job_match(candidate_skills, request.required_skills)

    return JobMatchResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.candidate_name,
        job_title=request.job_title,
        match_score=match_result["match_score"],
        matched_skills=match_result["matched_skills"],
        missing_skills=match_result["missing_skills"]
    )