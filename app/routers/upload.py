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
    # 1. Validate File Type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # 2. Extract PDF text using PyPDF
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

        # 3. Analyze text with AI Service
        parsed_data = analyze_resume(extracted_text)

        if not parsed_data or not isinstance(parsed_data, dict):
            raise HTTPException(status_code=500, detail="Failed to parse resume data from AI service.")

        # 4. Save Candidate to DB
        candidate = Candidate(
            candidate_name=parsed_data.get("candidate_name", "Unknown Candidate"),
            email=parsed_data.get("email", ""),
            candidate_summary=parsed_data.get("candidate_summary", ""),
            education=parsed_data.get("education", []),
            technical_skills=parsed_data.get("technical_skills", []),
            soft_skills=parsed_data.get("soft_skills", []),
            projects=parsed_data.get("projects", []),
            experience=parsed_data.get("experience", []),
            strengths=parsed_data.get("strengths", []),
            missing_skills=parsed_data.get("missing_skills", []),
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