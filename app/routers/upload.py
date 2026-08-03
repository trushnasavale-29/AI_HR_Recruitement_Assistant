# backend/app/routers/upload.py
import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy import String
from sqlalchemy.orm import Session

from app.utils.pdf_parser import extract_text
from app.services.gemini_service import analyze_resume
from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateResponse

router = APIRouter(tags=["Candidates"])

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload-resume", response_model=CandidateResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text(file_path)

    if not resume_text.strip():
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    try:
        analysis = analyze_resume(resume_text)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"AI Processing Error: {str(e)}")

    db_candidate = Candidate(
        filename=file.filename,
        candidate_name=analysis.get("candidate_name", "Unknown Candidate"),
        email=analysis.get("email", ""),
        candidate_summary=analysis.get("candidate_summary", "Summary unavailable"),
        education=analysis.get("education", []),
        technical_skills=analysis.get("technical_skills", []),
        soft_skills=analysis.get("soft_skills", []),
        projects=analysis.get("projects", []),
        experience=analysis.get("experience", []),
        strengths=analysis.get("strengths", []),
        missing_skills=analysis.get("missing_skills", []),
        recommended_roles=analysis.get("recommended_roles", []),
        ats_score=int(analysis.get("ats_score", 0)),
        ats_suggestions=analysis.get("ats_suggestions", []),
        interview_questions=analysis.get("interview_questions", []),
    )

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return db_candidate


@router.get("/candidates", response_model=List[CandidateResponse])
def get_all_candidates(
    search: Optional[str] = Query(None, description="Search candidate by name or skill"),
    db: Session = Depends(get_db)
):
    """Fetch all analyzed candidate resumes with optional search filtering"""
    query = db.query(Candidate)
    if search:
        query = query.filter(
            Candidate.candidate_name.ilike(f"%{search}%") | 
            Candidate.technical_skills.cast(String).ilike(f"%{search}%")
        )
    return query.order_by(Candidate.created_at.desc()).all()


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate_by_id(candidate_id: int, db: Session = Depends(get_db)):
    """Fetch a single candidate analysis by ID"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.delete("/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate record from database"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    return {"message": f"Candidate {candidate_id} successfully deleted."}