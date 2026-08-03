import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate

router = APIRouter(tags=["Candidate Profile"])

# Initialize Jinja2 templates (looking in static or templates directory)
templates = Jinja2Templates(directory="templates")

# 1. HTML Page Route (Renders the candidate dashboard template)
@router.get("/candidate-view/{candidate_id}", response_class=HTMLResponse)
async def serve_candidate_page(candidate_id: int, request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "candidate_id": candidate_id})

# 2. API Endpoint (Fetches structured data for JS fetch)
@router.get("/api/candidate/{candidate_id}")
def get_candidate_data(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    def parse_json_field(field_val):
        if not field_val:
            return []
        if isinstance(field_val, (list, dict)):
            return field_val
        try:
            return json.loads(field_val)
        except Exception:
            return [field_val]

    return {
        "id": candidate.id,
        "candidate_name": candidate.candidate_name or "Unknown Candidate",
        "email": candidate.email or "",
        "ats_score": candidate.ats_score or 0,
        "candidate_summary": candidate.candidate_summary or "No summary available.",
        "extracted_skills": parse_json_field(candidate.extracted_skills),
        "missing_keywords": parse_json_field(candidate.missing_keywords),
        "interview_questions": parse_json_field(candidate.interview_questions)
    }