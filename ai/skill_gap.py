from ai.skill_extractor import extract_skills


def analyze_skill_gap(cv_text, job_text):
    cv_skills = set(extract_skills(cv_text))
    job_skills = set(extract_skills(job_text))

    matched_skills = sorted(cv_skills & job_skills)
    missing_skills = sorted(job_skills - cv_skills)

    return {
        "cv_skills": sorted(cv_skills),
        "job_skills": sorted(job_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }