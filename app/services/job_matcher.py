# backend/app/services/job_matcher.py
from typing import List, Dict, Any


def calculate_job_match(candidate_skills: List[str], job_description_skills: List[str]) -> Dict[str, Any]:
    """
    Compares candidate skills against job requirements and returns
    a match percentage with breakdown.
    """
    if not job_description_skills:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": []
        }

    # Normalize strings for case-insensitive comparison
    candidate_skills_lower = {skill.strip().lower() for skill in candidate_skills}
    job_skills_lower = {skill.strip().lower(): skill for skill in job_description_skills}

    matched = []
    missing = []

    for lower_skill, original_skill in job_skills_lower.items():
        if lower_skill in candidate_skills_lower:
            matched.append(original_skill)
        else:
            missing.append(original_skill)

    # Calculate match percentage
    total_required = len(job_skills_lower)
    match_percentage = round((len(matched) / total_required) * 100) if total_required > 0 else 0

    return {
        "match_score": match_percentage,
        "matched_skills": matched,
        "missing_skills": missing
    }