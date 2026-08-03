import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.candidate import Candidate

router = APIRouter(prefix="/api/candidate", tags=["Candidate"])

@router.get("/{candidate_id}")
def get_candidate_details(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Safely parse JSON strings stored in text columns
    try:
        extracted_skills = json.loads(candidate.extracted_skills) if candidate.extracted_skills else []
    except Exception:
        extracted_skills = candidate.extracted_skills

    try:
        missing_keywords = json.loads(candidate.missing_keywords) if candidate.missing_keywords else []
    except Exception:
        missing_keywords = candidate.missing_keywords

    return {
        "id": candidate.id,
        "candidate_name": candidate.candidate_name,
        "email": candidate.email,
        "ats_score": candidate.ats_score,
        "candidate_summary": candidate.candidate_summary,
        "extracted_skills": extracted_skills,
        "missing_keywords": missing_keywords,
        "interview_questions": candidate.interview_questions or []
    }