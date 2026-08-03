from pydantic import BaseModel
from typing import List, Optional

class InterviewGenerateRequest(BaseModel):
    candidate_id: int
    target_role: Optional[str] = "Software Engineer"
    difficulty: Optional[str] = "Medium"  # Easy, Medium, Hard

class InterviewQuestionItem(BaseModel):
    category: str  # Technical, Behavioral, System Design, Skill Gap
    question: str
    rationale: str
    sample_answer_key: str

class InterviewGenerateResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    target_role: str
    difficulty: str
    questions: List[InterviewQuestionItem]