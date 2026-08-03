from pydantic import BaseModel
from typing import List


class Education(BaseModel):
    degree: str
    institution: str
    duration: str
    performance: str


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]


class Experience(BaseModel):
    role: str
    organization: str
    description: str


class ResumeAnalysis(BaseModel):
    candidate_summary: str

    education: List[Education]

    technical_skills: List[str]

    soft_skills: List[str]

    projects: List[Project]

    experience: List[Experience]

    strengths: List[str]

    missing_skills: List[str]

    recommended_roles: List[str]

    ats_score: int

    ats_suggestions: List[str]

    interview_questions: List[str]