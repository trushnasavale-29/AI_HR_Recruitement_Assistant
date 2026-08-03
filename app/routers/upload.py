from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.candidate import Candidate
from app.services.gemini_service import analyze_resume

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("")  # Or @router.post("/resume") depending on what JS calls
async def upload_and_process_resume(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # Extract file content
    content = await file.read()
    resume_text = content.decode("utf-8", errors="ignore")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not read text from uploaded file")

    # Analyze via Groq Engine
    parsed_data = analyze_resume(resume_text)

    # Save to PostgreSQL
    candidate = Candidate(
        candidate_name=parsed_data.get("candidate_name"),
        email=parsed_data.get("email"),
        candidate_summary=parsed_data.get("candidate_summary"),
        education=parsed_data.get("education"),
        technical_skills=parsed_data.get("technical_skills"),
        soft_skills=parsed_data.get("soft_skills"),
        projects=parsed_data.get("projects"),
        experience=parsed_data.get("experience"),
        strengths=parsed_data.get("strengths"),
        missing_skills=parsed_data.get("missing_skills"),
        ats_score=parsed_data.get("ats_score", 0),
        keyword_match=parsed_data.get("keyword_match", 0),
        skill_match=parsed_data.get("skill_match", 0),
        education_match=parsed_data.get("education_match", 0),
        experience_match=parsed_data.get("experience_match", 0),
        job_matches=parsed_data.get("job_matches", []),
        ats_suggestions=parsed_data.get("ats_suggestions", []),
        interview_questions=parsed_data.get("interview_questions", [])
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {"status": "success", "candidate_id": candidate.id, "data": parsed_data}