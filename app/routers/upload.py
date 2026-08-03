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

        # 2. Extract analysis and interview questions via AI
        parsed_data = analyze_resume(extracted_text)
        if not isinstance(parsed_data, dict):
            parsed_data = {}

        # 3. Construct Candidate using exact Model fields
        candidate = Candidate(
            candidate_name=parsed_data.get("candidate_name") or parsed_data.get("name") or "Unknown Candidate",
            email=parsed_data.get("email", ""),
            ats_score=int(parsed_data.get("ats_score", 0)),
            candidate_summary=parsed_data.get("candidate_summary") or parsed_data.get("summary") or "",
            extracted_skills=json.dumps(parsed_data.get("technical_skills", []) + parsed_data.get("soft_skills", [])),
            missing_keywords=json.dumps(parsed_data.get("missing_skills", [])),
            interview_questions=parsed_data.get("interview_questions", [])
        )

        # 4. Save to Database
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
        raise HTTPException(status_code=500, detail=f"Server error processing PDF: {str(e)}")