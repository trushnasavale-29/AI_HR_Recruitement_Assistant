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

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI HR Recruitment Assistant",
    description="AI-powered resume analysis and recruitment assistant"
)

# APP_DIR is backend/app
APP_DIR = Path(__file__).resolve().parent

# static is in backend/app/static
static_path = APP_DIR / "static"
# templates is in backend/templates (one level up from app)
templates_path = APP_DIR.parent / "templates"

static_path.mkdir(parents=True, exist_ok=True)
templates_path.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path))

# Register Routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(job_match.router)
app.include_router(interview.router)

# --- Candidate Data APIs ---

@app.get("/api/candidates", tags=["Candidates"])
def get_all_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.id.desc()).all()
    return candidates

@app.get("/api/candidates/{candidate_id}", tags=["Candidates"])
def get_candidate_by_id(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

# --- Frontend Template Views ---

@app.get("/", include_in_schema=False)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/candidates-view", include_in_schema=False)
def candidate_list_view(request: Request):
    return templates.TemplateResponse("candidates.html", {"request": request})

@app.get("/candidate-view/{candidate_id}", include_in_schema=False)
def candidate_dashboard(candidate_id: int, request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "candidate_id": candidate_id}
    )

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "online", "message": "Backend API is running smoothly"}