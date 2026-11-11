"""
Job Recommender - Multi-signal ranking with TF-IDF, semantic skills, career matching
Uses connection pool for database access.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import joblib
from sklearn.metrics.pairwise import cosine_similarity

from ai.skill_gap import analyze_skill_gap
from ai.explanation import generate_explanation
from ai.text_preprocessing import preprocess_text
from ai.career_classifier import get_classifier
from ai.skill_matcher import get_skill_matcher
from ai.ranking import get_ranking_engine
from database.connection_pool import get_cursor
from database.database import create_recommendation

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"

# Global model cache (lazy loaded)
_tfidf = None
_career_classifier = None
_models_loaded = False


def _load_models() -> bool:
    """Lazy load TF-IDF vectorizer and career classifier on first use."""
    global _tfidf, _career_classifier, _models_loaded

    if _models_loaded:
        return _tfidf is not None and _career_classifier is not None

    try:
        tfidf_path = MODELS_DIR / "tfidf_vectorizer.joblib"
        if tfidf_path.exists():
            _tfidf = joblib.load(tfidf_path)
            logger.info("TF-IDF vectorizer loaded successfully")
        else:
            logger.warning(f"TF-IDF vectorizer not found at {tfidf_path}")
            _tfidf = None

        # Use CareerClassifier singleton for career predictions
        _career_classifier = get_classifier()
        if _career_classifier.is_fitted:
            logger.info("Career classifier loaded successfully")
        else:
            logger.warning("Career classifier not fitted")
            _career_classifier = None

        _models_loaded = True
        return _tfidf is not None

    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        _tfidf = None
        _career_classifier = None
        _models_loaded = True
        return False


def _get_tfidf():
    """Get TF-IDF vectorizer, loading if necessary."""
    if not _models_loaded:
        _load_models()
    return _tfidf


def _get_career_classifier():
    """Get career classifier, loading if necessary."""
    if not _models_loaded:
        _load_models()
    return _career_classifier


# =========================================================
# Core Vectorization Functions
# =========================================================

def vectorize_cv(cv_text: str):
    """Transform CV text to TF-IDF vector."""
    tfidf = _get_tfidf()
    if tfidf is None:
        logger.warning("TF-IDF not available, returning empty vector")
        from scipy.sparse import csr_matrix
        return csr_matrix((1, 2000))

    cleaned_text = preprocess_text(cv_text)
    cv_vector = tfidf.transform([cleaned_text])
    return cv_vector


def vectorize_job(job_title: str, job_description: str):
    """Transform job text to TF-IDF vector."""
    tfidf = _get_tfidf()
    if tfidf is None:
        from scipy.sparse import csr_matrix
        return csr_matrix((1, 2000))

    job_title = job_title or ""
    job_description = job_description or ""
    job_text = f"{job_title} {job_description}"
    cleaned_text = preprocess_text(job_text)
    job_vector = tfidf.transform([cleaned_text])
    return job_vector


def calculate_similarity(cv_vector, job_vector) -> float:
    """Calculate cosine similarity between CV and job vectors."""
    try:
        similarity = cosine_similarity(cv_vector, job_vector)[0][0]
        return float(similarity)
    except Exception as e:
        logger.error(f"Similarity calculation failed: {e}")
        return 0.0


def predict_career(cv_text: str) -> Optional[str]:
    """Predict career category from CV text."""
    classifier = _get_career_classifier()
    if classifier is None:
        logger.warning("Career classifier not available")
        return None
    if not classifier.is_fitted:
        logger.warning("Career classifier not fitted")
        return None
    return classifier.predict(cv_text)


def predict_career_top_k(cv_text: str, k: int = 3) -> List[Dict[str, Any]]:
    """Get top-k career predictions with probabilities."""
    classifier = _get_career_classifier()
    if classifier is None:
        return []
    return classifier.predict_top_k(cv_text, k)


# =========================================================
# Database Operations (using connection pool)
# =========================================================

def get_all_active_jobs() -> List[Dict]:
    """Get all active jobs from database."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT job_id, title, description, company, location,
                   job_type, category, level, salary_min, salary_max, created_at
            FROM jobs
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        return cur.fetchall()


def get_all_active_jobs_with_data() -> List[Dict]:
    """
    Get all active jobs with skills and pre-computed TF-IDF vectors.
    Batch vectorizes all jobs in a single pass for efficiency.
    """
    jobs = get_all_active_jobs()
    tfidf = _get_tfidf()

    # Fetch skills for all jobs in one query
    job_ids = [j["job_id"] for j in jobs]
    job_skills_map = {}
    if job_ids:
        with get_cursor() as cur:
            placeholders = ", ".join(["%s"] * len(job_ids))
            cur.execute(f"""
                SELECT js.job_id, s.skill_name
                FROM job_skills js
                JOIN skills s ON js.skill_id = s.skill_id
                WHERE js.job_id IN ({placeholders})
            """, job_ids)
            for row in cur.fetchall():
                job_skills_map.setdefault(row["job_id"], []).append(row["skill_name"])

    # Attach skills to jobs
    for job in jobs:
        job["skills"] = job_skills_map.get(job["job_id"], [])

    if tfidf is None:
        for job in jobs:
            job["_vector"] = None
        return jobs

    # Batch vectorize all job texts
    job_texts = []
    for job in jobs:
        title = job.get("title") or ""
        desc = job.get("description") or ""
        job_texts.append(f"{title} {desc}")

    cleaned_texts = [preprocess_text(text) for text in job_texts]
    job_vectors = tfidf.transform(cleaned_texts)

    for i, job in enumerate(jobs):
        job["_vector"] = job_vectors[i]

    return jobs


def get_user_skills(user_id: int) -> List[str]:
    """Get user's skills from profile and CVs."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.skill_name
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.skill_id
            WHERE ss.user_id = %s
        """, (user_id,))
        profile_skills = [row["skill_name"] for row in cur.fetchall()]

        cur.execute("""
            SELECT extracted_skills
            FROM cvs
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        cv_row = cur.fetchone()
        cv_skills = cv_row["extracted_skills"] if cv_row and cv_row["extracted_skills"] else []

        return list(set(profile_skills + cv_skills))


def get_user_latest_cv_text(user_id: int) -> str:
    """Get user's latest CV text for vectorization."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT raw_text
            FROM cvs
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        row = cur.fetchone()
        return row["raw_text"] if row else ""


def get_user_salary_preferences(user_id: int) -> tuple:
    """Get user's salary preferences if available."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT salary_min, salary_max FROM user_preferences WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        if row:
            return row.get("salary_min"), row.get("salary_max")
        return None, None


def save_recommendations(user_id: int, recommendations: List[Dict]):
    """Save recommendations to database."""
    for rec in recommendations:
        # Extract summary string from explanation dict for DB storage
        explanation = rec.get("explanation")
        reason = explanation.get("summary", "") if isinstance(explanation, dict) else str(explanation) if explanation else ""

        create_recommendation(
            user_id=user_id,
            job_id=rec["job_id"],
            match_score=rec["match_score"],
            skill_match=rec.get("skill_match", 0),
            career_match=rec.get("career_match", False),
            reason=reason,
        )


# =========================================================
# Public Recommendation Functions
# =========================================================

def recommend_jobs_for_user(user_id: int, top_k: int = 10) -> List[Dict]:
    """
    Main recommendation function for a user.
    Uses multi-signal ranking engine.
    """
    if not _models_loaded:
        _load_models()

    # Get user data
    cv_text = get_user_latest_cv_text(user_id)
    if not cv_text:
        skills = get_user_skills(user_id)
        cv_text = " ".join(skills) if skills else ""

    if not cv_text:
        return []

    cv_skills = get_user_skills(user_id)
    cv_vector = vectorize_cv(cv_text)
    predicted_career = predict_career(cv_text)
    salary_min, salary_max = get_user_salary_preferences(user_id)

    # Get jobs with vectors and skills
    jobs = get_all_active_jobs_with_data()

    # Extract job vectors and skills for ranking
    job_vectors = [job.get("_vector") for job in jobs]

    # Use ranking engine
    ranking_engine = get_ranking_engine()
    ranked_jobs = ranking_engine.rank_jobs(
        cv_text=cv_text,
        cv_skills=cv_skills,
        predicted_career=predicted_career,
        jobs=jobs,
        cv_vector=cv_vector,
        job_vectors=job_vectors,
        user_salary_min=salary_min,
        user_salary_max=salary_max
    )

    # Build final recommendations with additional info
    recommendations = []
    skill_matcher = get_skill_matcher()

    for job in ranked_jobs[:top_k]:
        # Skill gap analysis using hybrid matcher
        job_skills = [s["skill_name"] if isinstance(s, dict) else s for s in job.get("skills", [])]
        skill_gap = analyze_skill_gap(
            cv_text=cv_text,
            job_text=job_skills,
            job_category=job.get("category", ""),
            job_id=job["job_id"],
            include_resources=True,
            include_learning_path=True,
            cv_raw_text=cv_text
        )

        # Also get hybrid match details
        hybrid_match = skill_matcher.match_skills(cv_skills, job_skills)

        career_match = predicted_career and job["category"] and predicted_career == job["category"]

        # Generate detailed explanation with full skill_gap data
        ranking_explanation = ranking_engine.explain_ranking(job)
        explanation = generate_explanation(
            predicted_career=predicted_career,
            job_category=job["category"],
            skill_gap=skill_gap,
            ranking_explanation=ranking_explanation
        )

        recommendations.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "category": job["category"],
            "job_type": job["job_type"],
            "level": job["level"],
            "salary_min": job["salary_min"],
            "salary_max": job["salary_max"],
            "description": job["description"],
            "created_at": job.get("created_at"),
            "skills": job.get("skills", []),
            "similarity": job.get("ranking_signals", {}).get("tfidf_cosine", 0),
            "match_score": job["match_score"],
            "skill_match": skill_gap["match_ratio"],
            "career_match": career_match,
            "matched_skills": skill_gap["matched_skills"],
            "missing_skills": skill_gap["missing_skills"],
            "missing_skills_by_priority": skill_gap.get("missing_skills_by_priority", []),
            "hybrid_matched": hybrid_match.get("matched_skills", []),
            "semantic_matched": hybrid_match.get("semantic_matched", []),
            "extra_skills": skill_gap.get("extra_skills", []),
            "skill_details": skill_gap.get("skill_details", []),
            "required_skills": skill_gap.get("required_skills", []),
            "preferred_skills": skill_gap.get("preferred_skills", []),
            "market_demand": skill_gap.get("market_demand", {}),
            "priority_scores": skill_gap.get("priority_scores", {}),
            "resources": skill_gap.get("resources", {}),
            "learning_path": skill_gap.get("learning_path", {}),
            "explanation": explanation,
            "ranking_explanation": ranking_explanation,
            "predicted_career": predicted_career,
            "career_predictions": predict_career_top_k(cv_text, 3)
        })

    # Save to database
    save_recommendations(user_id, recommendations[:top_k])

    return recommendations[:top_k]


def recommend_jobs(cv_text: str, top_k: int = 5) -> List[Dict]:
    """Legacy function: Recommend jobs from raw CV text."""
    if not _models_loaded:
        _load_models()

    # Fallback to extract_skills for legacy
    from ai.skill_extractor import extract_skills
    cv_skills = extract_skills(cv_text)

    cv_vector = vectorize_cv(cv_text)
    predicted_career = predict_career(cv_text)
    jobs = get_all_active_jobs_with_data()
    job_vectors = [job.get("_vector") for job in jobs]

    ranking_engine = get_ranking_engine()
    ranked_jobs = ranking_engine.rank_jobs(
        cv_text=cv_text,
        cv_skills=cv_skills,
        predicted_career=predicted_career,
        jobs=jobs,
        cv_vector=cv_vector,
        job_vectors=job_vectors
    )

    recommendations = []
    for job in ranked_jobs[:top_k]:
        job_skills = [s["skill_name"] if isinstance(s, dict) else s for s in job.get("skills", [])]
        skill_gap = analyze_skill_gap(
            cv_text=cv_text,
            job_text=job_skills,
            job_category=job.get("category", ""),
            job_id=job["job_id"],
            include_resources=True,
            include_learning_path=True,
            cv_raw_text=cv_text
        )

        ranking_explanation = ranking_engine.explain_ranking(job)
        explanation = generate_explanation(
            predicted_career=predicted_career,
            job_category=job["category"],
            skill_gap=skill_gap,
            ranking_explanation=ranking_explanation
        )

        recommendations.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "company": job["company"],
            "category": job["category"],
            "similarity": job.get("ranking_signals", {}).get("tfidf_cosine", 0),
            "match_score": job["match_score"],
            "matched_skills": skill_gap["matched_skills"],
            "missing_skills": skill_gap["missing_skills"],
            "explanation": explanation,
            "ranking_explanation": ranking_explanation
        })

    return recommendations[:top_k]


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_cv = """
    Python developer with experience in machine learning,
    pandas, numpy, scikit-learn, TensorFlow,
    data analysis, SQL and predictive models.
    """

    recommendations = recommend_jobs(test_cv, top_k=5)
    predicted_career = predict_career(test_cv)

    print("===== TOP 5 RECOMMENDED JOBS =====")
    print("Career Prediction:", predicted_career)

    for rank, job in enumerate(recommendations, start=1):
        print(f"\n#{rank} - {job['title']}")
        print("Company:", job["company"])
        print("Category:", job["category"])
        print(f"Similarity: {job['similarity'] * 100:.2f}%")
        print(f"Match Score: {job['match_score']}/100")
        print(f"Explanation: {job['explanation'][:100]}...")