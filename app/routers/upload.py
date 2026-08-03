import io
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
    """
    Endpoint: POST /api/upload/resume
    Extracts text from PDF, sends it to the AI service, and saves the result to DB.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # 1. Extract PDF text using PyPDF
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)
        
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from this PDF. Please ensure it's not scanned or an image."
            )

        # 2. Analyze text with AI Service
        parsed_data = analyze_resume(extracted_text)

        if not parsed_data or not isinstance(parsed_data, dict):
            raise HTTPException(status_code=500, detail="Failed to parse resume data from AI service.")

        # 3. Flexible Field Mapping (supports both 'name'/'candidate_name' and 'summary'/'candidate_summary')
        cand_name = parsed_data.get("candidate_name") or parsed_data.get("name") or "Unknown Candidate"
        cand_summary = parsed_data.get("candidate_summary") or parsed_data.get("summary") or ""

        # Check model columns dynamically to avoid keyword argument errors
        candidate_kwargs = {}
        model_cols = [col.key for col in Candidate.__table__.columns]

        # Map Name
        if "candidate_name" in model_cols:
            candidate_kwargs["candidate_name"] = cand_name
        elif "name" in model_cols:
            candidate_kwargs["name"] = cand_name

        # Map Summary
        if "candidate_summary" in model_cols:
            candidate_kwargs["candidate_summary"] = cand_summary
        elif "summary" in model_cols:
            candidate_kwargs["summary"] = cand_summary

        # Map common attributes if present in model
        for field in [
            "email", "education", "technical_skills", "soft_skills", 
            "projects", "experience", "strengths", "missing_skills", 
            "ats_score", "keyword_match", "skill_match", "education_match", 
            "experience_match", "job_matches", "ats_suggestions", "interview_questions"
        ]:
            if field in model_cols and field in parsed_data:
                candidate_kwargs[field] = parsed_data[field]

        # Instatantiate candidate model safely
        candidate = Candidate(**candidate_kwargs)

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
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Server error processing PDF: {str(e)}"
        )