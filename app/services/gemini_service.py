import json
import os
import json
from groq import Groq
from app.config import GROQ_API_KEY

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment variables")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"




def analyze_resume(resume_text: str) -> dict:
    """
    Sends resume text to Groq LLM and returns a structured JSON object.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    prompt = f"""
You are an AI HR Recruitment Assistant. Analyze the provided resume text thoroughly and extract/generate the structured information.

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
    "recommended_roles": ["string"],
    "ats_score": 75,
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
        "recommended_roles": [],
        "ats_score": 0,
        "ats_suggestions": [],
        "interview_questions": [],
    }

    for key, value in default_structure.items():
        if key not in result or result[key] is None:
            result[key] = value

    return result