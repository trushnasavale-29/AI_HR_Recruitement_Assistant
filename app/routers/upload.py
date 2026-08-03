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

        # Safe extraction helper with key fallback support
        def get_list(keys):
            for k in keys:
                val = parsed_data.get(k)
                if isinstance(val, list) and len(val) > 0:
                    return val
            return []

        # Extract list fields dynamically
        tech_skills = get_list(["technical_skills", "extracted_skills", "skills"])
        soft_skills = get_list(["soft_skills"])
        missing_skills = get_list(["missing_skills", "missing_keywords"])
        roles = get_list(["recommended_roles", "suggested_roles", "roles"])
        questions = get_list(["interview_questions", "questions"])

        all_skills = tech_skills + soft_skills

        # 3. Create Candidate with existing DB fields
        candidate = Candidate(
            candidate_name=parsed_data.get("candidate_name") or parsed_data.get("name") or "Unknown Candidate",
            email=parsed_data.get("email", ""),
            ats_score=int(parsed_data.get("ats_score", 0)),
            candidate_summary=parsed_data.get("candidate_summary") or parsed_data.get("summary") or "",
            extracted_skills=json.dumps(all_skills),
            missing_keywords=json.dumps(missing_skills),
            interview_questions=json.dumps(questions)
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
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")