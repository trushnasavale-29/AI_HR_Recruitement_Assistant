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
    """
    Endpoint: POST /api/upload/resume
    Extracts text from PDF, parses via AI, and maps data directly 
    to the actual PostgreSQL database schema.
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

        # 2. Analyze text with AI Service (Extracts Skills & Interview Questions)
        parsed_data = analyze_resume(extracted_text)

        if not parsed_data or not isinstance(parsed_data, dict):
            raise HTTPException(status_code=500, detail="Failed to parse resume data from AI service.")

        # 3. Get list of valid columns from Candidate SQLAlchemy Model
        model_cols = [col.key for col in Candidate.__table__.columns]

        # Extract values from AI response
        c_name = parsed_data.get("candidate_name") or parsed_data.get("name") or "Unknown Candidate"
        c_email = parsed_data.get("email") or ""
        c_summary = parsed_data.get("candidate_summary") or parsed_data.get("summary") or ""
        
        skills_list = parsed_data.get("technical_skills", []) + parsed_data.get("soft_skills", [])
        missing_list = parsed_data.get("missing_skills", [])

        # Build dictionary matching only existing columns
        cand_dict = {}

        # Column: candidate_name vs name
        if "candidate_name" in model_cols:
            cand_dict["candidate_name"] = c_name
        elif "name" in model_cols:
            cand_dict["name"] = c_name

        # Column: email
        if "email" in model_cols:
            cand_dict["email"] = c_email

        # Column: summary / summary_feedback / candidate_summary
        if "candidate_summary" in model_cols:
            cand_dict["candidate_summary"] = c_summary
        elif "summary_feedback" in model_cols:
            cand_dict["summary_feedback"] = c_summary
        elif "summary" in model_cols:
            cand_dict["summary"] = c_summary

        # Column: extracted_skills / technical_skills
        if "extracted_skills" in model_cols:
            cand_dict["extracted_skills"] = json.dumps(skills_list) if isinstance(skills_list, list) else str(skills_list)
        elif "technical_skills" in model_cols:
            cand_dict["technical_skills"] = skills_list

        # Column: missing_keywords / missing_skills
        if "missing_keywords" in model_cols:
            cand_dict["missing_keywords"] = json.dumps(missing_list) if isinstance(missing_list, list) else str(missing_list)
        elif "missing_skills" in model_cols:
            cand_dict["missing_skills"] = missing_list

        # Scores & Matches
        if "ats_score" in model_cols:
            cand_dict["ats_score"] = parsed_data.get("ats_score", 0)
        if "keyword_match" in model_cols:
            cand_dict["keyword_match"] = parsed_data.get("keyword_match", 0)
        if "skill_match" in model_cols:
            cand_dict["skill_match"] = parsed_data.get("skill_match", 0)
        if "education_match" in model_cols:
            cand_dict["education_match"] = parsed_data.get("education_match", 0)
        if "experience_match" in model_cols:
            cand_dict["experience_match"] = parsed_data.get("experience_match", 0)
        if "job_matches" in model_cols:
            cand_dict["job_matches"] = parsed_data.get("job_matches", [])

        # Interview Questions & JSON Fields
        if "interview_questions" in model_cols:
            cand_dict["interview_questions"] = parsed_data.get("interview_questions", [])

        # Catch any other matching direct column names
        for col in model_cols:
            if col not in cand_dict and col in parsed_data:
                cand_dict[col] = parsed_data[col]

        # 4. Save Candidate to DB
        candidate = Candidate(**cand_dict)

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