"""
Match Score - Legacy compatibility module
Provides backward compatibility for match score calculations.
"""

import logging
from typing import List, Dict, Any, Optional

from ai.skill_extractor import extract_skills
from ai.skill_matcher import match_skills_hybrid
from ai.skill_gap import analyze_skill_gap

logger = logging.getLogger(__name__)


def calculate_match_score(cv_text: str, job_description: str) -> float:
    """
    Calculate match score between CV and job description.

    Args:
        cv_text: Raw CV text
        job_description: Job description text

    Returns:
        Match score (0-100)
    """
    cv_skills = extract_skills(cv_text)
    job_skills = extract_skills(job_description)

    if not job_skills:
        return 0.0

    match_result = match_skills_hybrid(cv_skills, job_skills)
    matched_count = len(match_result.get("matched_skills", []))

    score = (matched_count / len(job_skills)) * 100
    return round(score, 2)


def calculate_skill_match_percentage(cv_skills: List[str], job_skills: List[str]) -> float:
    """
    Calculate skill match percentage.

    Args:
        cv_skills: List of skills from CV
        job_skills: List of skills required by job

    Returns:
        Match percentage (0-100)
    """
    if not job_skills:
        return 0.0

    match_result = match_skills_hybrid(cv_skills, job_skills)
    matched_count = len(match_result.get("matched_skills", []))

    percentage = (matched_count / len(job_skills)) * 100
    return round(percentage, 1)


def get_skill_gap_analysis(cv_text: str, job_text: str) -> Dict:
    """
    Get detailed skill gap analysis.

    Args:
        cv_text: Raw CV text
        job_text: Job description text

    Returns:
        Dictionary with gap analysis
    """
    return analyze_skill_gap(cv_text, job_text)


def get_missing_skills(cv_text: str, job_text: str) -> List[str]:
    """
    Get list of missing skills.

    Args:
        cv_text: Raw CV text
        job_text: Job description text

    Returns:
        List of missing skill names
    """
    gap = analyze_skill_gap(cv_text, job_text)
    return gap.get("missing_skills", [])


def get_matched_skills(cv_text: str, job_text: str) -> List[str]:
    """
    Get list of matched skills.

    Args:
        cv_text: Raw CV text
        job_text: Job description text

    Returns:
        List of matched skill names
    """
    gap = analyze_skill_gap(cv_text, job_text)
    return gap.get("matched_skills", [])


# Legacy functions for backward compatibility
def compute_tfidf_similarity(cv_text: str, job_text: str) -> float:
    """Legacy TF-IDF similarity function."""
    from ai.recommender import vectorize_cv, vectorize_job, calculate_similarity
    cv_vector = vectorize_cv(cv_text)
    job_vector = vectorize_job("", job_text)
    return calculate_similarity(cv_vector, job_vector)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # Test
    cv = "Python developer with Django, PostgreSQL, Docker, AWS"
    job = "Backend developer: Python, Django, PostgreSQL, Kubernetes, AWS"

    print(f"CV: {cv}")
    print(f"Job: {job}")
    print(f"Match Score: {calculate_match_score(cv, job)}")
    print(f"Skill Match %: {calculate_skill_match_percentage(['python', 'django', 'postgresql', 'docker', 'aws'], ['python', 'django', 'postgresql', 'kubernetes', 'aws'])}")
    print(f"Matched: {get_matched_skills(cv, job)}")
    print(f"Missing: {get_missing_skills(cv, job)}")