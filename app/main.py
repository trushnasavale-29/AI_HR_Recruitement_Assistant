# backend/app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database.database import Base, engine
from app.routers import upload
from app.routers import upload, job_match
from pathlib import Path
# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI HR Recruitment Assistant",
    description="AI-powered resume analysis and recruitment assistant"
)
# Resolve base paths dynamically
APP_DIR = Path(__file__).resolve().parent

# Check if 'static' is next to main.py or one level up
static_path = APP_DIR / "static"
if not static_path.exists():
    static_path = APP_DIR.parent / "static"

# Check if 'templates' is next to main.py or one level up
templates_path = APP_DIR / "templates"
if not templates_path.exists():
    templates_path = APP_DIR.parent / "templates"

# Mount static & template directories safely
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path))

# Include Routers

app.include_router(upload.router)
app.include_router(job_match.router)

@app.get("/", include_in_schema=False)
def read_root(request: Request):
    """Render main upload homepage"""
    return templates.TemplateResponse(
        request,
        "index.html"
    )
@app.get("/candidates-view", include_in_schema=False)
def candidate_list_view(request: Request):
    """Render candidates directory page"""
    return templates.TemplateResponse(
        request,
        "candidates.html"
    )

@app.get("/candidate-view/{candidate_id}", include_in_schema=False)
def candidate_dashboard(candidate_id: int, request: Request):
    """Render candidate analysis dashboard"""
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"candidate_id": candidate_id}
    )


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint"""
    return {"status": "online", "message": "Backend API is running smoothly"}