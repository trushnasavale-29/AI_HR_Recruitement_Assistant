import io
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.database.database import get_db
from app.models.candidate import Candidate
from app.services.gemini_service import analyze_resume

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("/resume")
async def upload_and_process_resume(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # 1. Read PDF text
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)
        
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        # 2. Extract structured analysis & interview questions from AI
        parsed_data = analyze_resume(extracted_text)
        if not isinstance(parsed_data, dict):
            parsed_data = {}

        # 3. Create Candidate and set attributes dynamically based on DB columns
        candidate = Candidate()
        model_cols = [col.key for col in Candidate.__table__.columns]

        # Name
        name_val = parsed_data.get("candidate_name") or parsed_data.get("name") or "Unknown Candidate"
        if "candidate_name" in model_cols:
            setattr(candidate, "candidate_name", name_val)
        elif "name" in model_cols:
            setattr(candidate, "name", name_val)

        # Email
        if "email" in model_cols:
            setattr(candidate, "email", parsed_data.get("email", ""))

        # Summary
        summary_val = parsed_data.get("candidate_summary") or parsed_data.get("summary") or ""
        if "candidate_summary" in model_cols:
            setattr(candidate, "candidate_summary", summary_val)
        elif "summary_feedback" in model_cols:
            setattr(candidate, "summary_feedback", summary_val)

        # ATS Score
        if "ats_score" in model_cols:
            setattr(candidate, "ats_score", int(parsed_data.get("ats_score", 0)))

        # RESTORED: Interview Questions
        interview_qs = parsed_data.get("interview_questions", [])
        if "interview_questions" in model_cols:
            setattr(candidate, "interview_questions", interview_qs)

        # 4. Commit to PostgreSQL Database
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        return {
            "status": "success",
            "id": candidate.id,
            "candidate_id": candidate.id,
            "data": parsed_data
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")