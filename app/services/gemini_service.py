import json
import os
from groq import Groq
from app.config import GROQ_API_KEY

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment variables")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"


def analyze_resume(resume_text: str) -> dict:
    """
    Sends resume text to Groq LLM and returns a structured JSON object containing
    detailed ATS sub-scores and job matching cards.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    prompt = f"""
You are an AI HR Recruitment Assistant and Advanced ATS engine. Analyze the provided resume text thoroughly and extract/generate structured information.

RESUME TEXT:
{resume_text}

Requirements:
Return ONLY a valid JSON object matching this exact structure with no extra conversational text or commentary:

{{
    "candidate_name": "string - full name of candidate if found, else 'Unknown Candidate'",
    "email": "string - candidate email address if found, else ''",
    "candidate_summary": "string - concise professional summary",
    "education": [
        {{
            "degree": "string",
            "institution": "string",
            "duration": "string",
            "performance": "string"
        }}
    ],
    "technical_skills": ["string"],
    "soft_skills": ["string"],
    "projects": [
        {{
            "name": "string",
            "description": "string",
            "technologies": ["string"]
        }}
    ],
    "experience": [
        {{
            "role": "string",
            "organization": "string",
            "description": "string"
        }}
    ],
    "strengths": ["string"],
    "missing_skills": ["string"],
    "ats_score": 78,
    "keyword_match": 82,
    "skill_match": 75,
    "education_match": 90,
    "experience_match": 70,
    "job_matches": [
        {{
            "job_title": "Python Developer Intern",
            "match_percentage": 82,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["AsyncIO"]
        }},
        {{
            "job_title": "Software Developer Intern",
            "match_percentage": 76,
            "matched_skills": ["SQL", "Docker"],
            "missing_skills": ["System Design"]
        }}
    ],
    "ats_suggestions": ["string"],
    "interview_questions": ["string"]
}}
"""

    # Call Groq API
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a recruitment AI assistant that outputs strictly valid JSON objects.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    response_text = response.choices[0].message.content.strip()

    # Clean potential markdown formatting (```json ... ```)
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Parse JSON
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM JSON response: {e}\nRaw output: {response_text}")

    # Ensure all required keys exist with default fallbacks
    default_structure = {
        "candidate_name": "Unknown Candidate",
        "email": "",
        "candidate_summary": "Summary not available",
        "education": [],
        "technical_skills": [],
        "soft_skills": [],
        "projects": [],
        "experience": [],
        "strengths": [],
        "missing_skills": [],
        "ats_score": 0,
        "keyword_match": 0,
        "skill_match": 0,
        "education_match": 0,
        "experience_match": 0,
        "job_matches": [],
        "ats_suggestions": [],
        "interview_questions": [],
    }

    for key, value in default_structure.items():
        if key not in result or result[key] is None:
            result[key] = value

    return result


def generate_interview_questions(
    candidate_name: str,
    skills: list,
    missing_skills: list,
    target_role: str = "Software Engineer",
    difficulty: str = "Medium"
) -> list:
    """
    Generates dynamic interview questions tailored to candidate strengths and missing skill gaps.
    """
    prompt = f"""
You are an expert technical interviewer evaluating a candidate for a role.

Candidate Name: {candidate_name}
Target Role: {target_role}
Difficulty Level: {difficulty}
Known Technical Skills: {', '.join(skills) if skills else 'General Software Engineering'}
Identified Skill Gaps / Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

Requirements:
Generate exactly 5 targeted interview questions tailored to evaluate this candidate.
Specifically probe their missing skills to assess how they bridge knowledge gaps.

Return ONLY a valid JSON object matching this exact structure:
{{
    "questions": [
        {{
            "category": "Skill Gap Probe",
            "question": "string - targeted question",
            "rationale": "string - why this question is being asked based on their profile",
            "sample_answer_key": "string - key concepts expected in a strong answer"
        }}
    ]
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a senior technical interviewer returning strictly valid JSON objects.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    response_text = response.choices[0].message.content.strip()

    # Clean potential markdown formatting
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        data = json.loads(response_text)
        if isinstance(data, dict):
            return data.get("questions", [])
        elif isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Interview Questions JSON response: {e}\nRaw output: {response_text}")