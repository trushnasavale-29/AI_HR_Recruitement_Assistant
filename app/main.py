# backend/app/main.py
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

# Absolute path to the directory containing main.py (app/)
APP_DIR = Path(__file__).resolve().parent

# Mount static & template directories directly
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")

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