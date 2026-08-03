import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import Base, engine, get_db
from app.models.candidate import Candidate, User 
from app.routers import upload, job_match, interview, auth 

# Initialize database tables safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(
    title="AI HR Recruitment Assistant",
    description="AI-powered resume analysis and recruitment assistant"
)

# Robust path discovery: Check both backend/templates and backend/app/templates
APP_DIR = Path(__file__).resolve().parent

# Check potential template locations dynamically
if (APP_DIR.parent / "templates").exists():
    templates_dir = APP_DIR.parent / "templates"
elif (APP_DIR / "templates").exists():
    templates_dir = APP_DIR / "templates"
else:
    templates_dir = APP_DIR.parent / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

# Check potential static locations dynamically
if (APP_DIR / "static").exists():
    static_dir = APP_DIR / "static"
elif (APP_DIR.parent / "static").exists():
    static_dir = APP_DIR.parent / "static"
else:
    static_dir = APP_DIR / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Register Routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(job_match.router)
app.include_router(interview.router)

# --- Candidate Data APIs (Supports all frontend fetch path variations) ---

@app.get("/api/candidates", tags=["Candidates"])
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.id.desc()).all()
    return candidates

# Catch all common endpoint variations used by dashboard JS:
@app.get("/candidates/{candidate_id}", tags=["Candidates"])
@app.get("/api/candidates/{candidate_id}", tags=["Candidates"])
@app.get("/api/candidate/{candidate_id}", tags=["Candidates"])
def get_candidate_by_id(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Clean output formatting for JSON response
    return candidate

# --- Frontend Template Views (FIXED) ---

@app.get("/", include_in_schema=False)
def read_root(request: Request):
    """Render main upload homepage"""
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@app.get("/candidates-view", include_in_schema=False)
def candidate_list_view(request: Request):
    """Render candidates directory page"""
    return templates.TemplateResponse(
        request=request, 
        name="candidates.html"
    )

@app.get("/candidate-view/{candidate_id}", include_in_schema=False)
def candidate_dashboard(candidate_id: int, request: Request):
    """Render candidate analysis dashboard"""
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"candidate_id": candidate_id}
    )