import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate

router = APIRouter(tags=["Candidate Profile"])

# Set correct path to templates folder (backend/templates)
APP_DIR = Path(__file__).resolve().parent.parent
templates_dir = APP_DIR.parent / "templates" if (APP_DIR.parent / "templates").exists() else APP_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# 1. HTML Dashboard Route (Fixed TemplateResponse parameters)
@router.get("/candidate-view/{candidate_id}", response_class=HTMLResponse)
async def serve_candidate_page(candidate_id: int, request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"candidate_id": candidate_id}
    )

# 2. Candidate Data API Endpoint
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