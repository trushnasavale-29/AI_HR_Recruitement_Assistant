from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.interview import InterviewGenerateRequest, InterviewGenerateResponse
from app.services.gemini_service import generate_interview_questions

router = APIRouter(prefix="/api/interview", tags=["Interview Generator"])

@router.post("/generate", response_model=InterviewGenerateResponse)
def create_candidate_interview(request: InterviewGenerateRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    skills = candidate.technical_skills or []
    missing_skills = candidate.missing_skills or []

    questions = generate_interview_questions(
        candidate_name=candidate.candidate_name,
        skills=skills,
        missing_skills=missing_skills,
        target_role=request.target_role,
        difficulty=request.difficulty
    )

    # Persist dynamic questions to candidate record
    candidate.interview_questions = questions
    db.commit()

    return InterviewGenerateResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.candidate_name,
        target_role=request.target_role,
        difficulty=request.difficulty,
        questions=questions
    )