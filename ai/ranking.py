"""
Ranking Engine - Multi-signal job ranking for recommendations
Combines TF-IDF, skill matching, career classification, and other signals
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from functools import lru_cache

from ai.skill_matcher import get_skill_matcher, match_skills_hybrid

logger = logging.getLogger(__name__)


@dataclass
class RankingWeights:
    """Configurable weights for ranking signals."""
    tfidf_cosine: float = 0.30
    skill_jaccard: float = 0.25
    skill_semantic: float = 0.25
    career_match: float = 0.10
    recency: float = 0.05
    salary: float = 0.05

    def normalize(self) -> 'RankingWeights':
        """Return normalized weights that sum to 1.0."""
        total = (self.tfidf_cosine + self.skill_jaccard + self.skill_semantic +
                 self.career_match + self.recency + self.salary)
        if total == 0:
            return self
        return RankingWeights(
            tfidf_cosine=self.tfidf_cosine / total,
            skill_jaccard=self.skill_jaccard / total,
            skill_semantic=self.skill_semantic / total,
            career_match=self.career_match / total,
            recency=self.recency / total,
            salary=self.salary / total
        )


@dataclass
class RankingSignals:
    """Individual ranking signals for a job."""
    tfidf_cosine: float = 0.0
    skill_jaccard: float = 0.0
    skill_semantic: float = 0.0
    career_match: float = 0.0
    recency: float = 0.0
    salary: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "tfidf_cosine": self.tfidf_cosine,
            "skill_jaccard": self.skill_jaccard,
            "skill_semantic": self.skill_semantic,
            "career_match": self.career_match,
            "recency": self.recency,
            "salary": self.salary
        }


class RankingEngine:
    """
    Multi-signal ranking engine for job recommendations.

    Combines multiple signals with configurable weights:
    - TF-IDF Cosine Similarity: Content-based similarity
    - Skill Jaccard: Exact skill overlap ratio
    - Skill Semantic: Semantic skill similarity via embeddings
    - Career Match: Career category alignment
    - Recency: Job posting freshness
    - Salary: Salary preference alignment (future)
    """

    def __init__(
        self,
        weights: Optional[RankingWeights] = None,
        semantic_threshold: float = 0.75
    ):
        self.weights = (weights or RankingWeights()).normalize()
        self.semantic_threshold = semantic_threshold
        self._skill_matcher = get_skill_matcher()

    def compute_signals(
        self,
        cv_text: str,
        cv_skills: List[str],
        predicted_career: Optional[str],
        job: Dict,
        job_vector: Any,
        cv_vector: Any,
        user_salary_min: Optional[int] = None,
        user_salary_max: Optional[int] = None
    ) -> RankingSignals:
        """
        Compute all ranking signals for a job.

        Args:
            cv_text: Raw CV text
            cv_skills: Extracted CV skills
            predicted_career: Predicted career category
            job: Job dictionary
            job_vector: Pre-computed job TF-IDF vector
            cv_vector: Pre-computed CV TF-IDF vector
            user_salary_min: User's minimum salary preference
            user_salary_max: User's maximum salary preference

        Returns:
            RankingSignals object with all signal values (0-1)
        """
        from sklearn.metrics.pairwise import cosine_similarity
        from datetime import datetime

        signals = RankingSignals()

        # 1. TF-IDF Cosine Similarity (0-1)
        try:
            if cv_vector is not None and job_vector is not None:
                sim = cosine_similarity(cv_vector, job_vector)[0][0]
                signals.tfidf_cosine = float(max(0, min(1, sim)))
        except Exception as e:
            logger.debug(f"TF-IDF similarity failed: {e}")

        # 2. Skill Jaccard (exact overlap)
        job_skills_raw = job.get("skills", [])
        # Handle both dict and string formats
        job_skills = [s["skill_name"] if isinstance(s, dict) else s for s in job_skills_raw]
        if cv_skills and job_skills:
            cv_set = set(s.lower() for s in cv_skills)
            job_set = set(s.lower() for s in job_skills)
            intersection = cv_set & job_set
            union = cv_set | job_set
            signals.skill_jaccard = len(intersection) / len(union) if union else 0.0

        # 3. Skill Semantic (hybrid matching)
        if cv_skills and job_skills:
            match_result = match_skills_hybrid(cv_skills, job_skills, self.semantic_threshold)
            matched = len(match_result.get("matched_skills", []))
            total_job = len(job_skills)
            signals.skill_semantic = matched / total_job if total_job > 0 else 0.0

        # 4. Career Match (binary: 0 or 1)
        job_category = job.get("category")
        if predicted_career and job_category:
            signals.career_match = 1.0 if predicted_career == job_category else 0.0

        # 5. Recency (newer jobs get higher score)
        created_at = job.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = None

            if created_at:
                days_old = (datetime.utcnow() - created_at.replace(tzinfo=None)).days
                # Exponential decay: 1.0 at 0 days, ~0.37 at 30 days, ~0.14 at 60 days
                signals.recency = max(0.0, min(1.0, 2.718 ** (-days_old / 30.0)))

        # 6. Salary Match (placeholder for future)
        if user_salary_min is not None or user_salary_max is not None:
            job_min = job.get("salary_min")
            job_max = job.get("salary_max")
            if job_min is not None or job_max is not None:
                # Simple overlap check
                if user_salary_min and job_max and user_salary_min <= job_max:
                    signals.salary = 1.0
                elif user_salary_max and job_min and user_salary_max >= job_min:
                    signals.salary = 1.0
                else:
                    signals.salary = 0.0

        return signals

    def compute_score(self, signals: RankingSignals) -> float:
        """
        Compute weighted final score from signals.

        Returns:
            Score from 0-100
        """
        w = self.weights
        score = (
            signals.tfidf_cosine * w.tfidf_cosine * 100 +
            signals.skill_jaccard * w.skill_jaccard * 100 +
            signals.skill_semantic * w.skill_semantic * 100 +
            signals.career_match * w.career_match * 100 +
            signals.recency * w.recency * 100 +
            signals.salary * w.salary * 100
        )
        return round(score, 2)

    def rank_jobs(
        self,
        cv_text: str,
        cv_skills: List[str],
        predicted_career: Optional[str],
        jobs: List[Dict],
        cv_vector: Any,
        job_vectors: List[Any],
        user_salary_min: Optional[int] = None,
        user_salary_max: Optional[int] = None
    ) -> List[Dict]:
        """
        Rank jobs for a user.

        Args:
            cv_text: Raw CV text
            cv_skills: Extracted CV skills
            predicted_career: Predicted career category
            jobs: List of job dictionaries
            cv_vector: Pre-computed CV TF-IDF vector
            job_vectors: List of pre-computed job TF-IDF vectors
            user_salary_min: User's minimum salary preference
            user_salary_max: User's maximum salary preference

        Returns:
            List of jobs with added ranking info, sorted by score descending
        """
        ranked = []

        for i, job in enumerate(jobs):
            job_vector = job_vectors[i] if i < len(job_vectors) else None

            signals = self.compute_signals(
                cv_text=cv_text,
                cv_skills=cv_skills,
                predicted_career=predicted_career,
                job=job,
                job_vector=job_vector,
                cv_vector=cv_vector,
                user_salary_min=user_salary_min,
                user_salary_max=user_salary_max
            )

            score = self.compute_score(signals)

            ranked.append({
                **job,
                "match_score": score,
                "ranking_signals": signals.to_dict(),
                "ranking_weights": {
                    "tfidf_cosine": self.weights.tfidf_cosine,
                    "skill_jaccard": self.weights.skill_jaccard,
                    "skill_semantic": self.weights.skill_semantic,
                    "career_match": self.weights.career_match,
                    "recency": self.weights.recency,
                    "salary": self.weights.salary
                }
            })

        # Sort by score descending
        ranked.sort(key=lambda x: x["match_score"], reverse=True)

        return ranked

    def explain_ranking(self, job: Dict) -> Dict:
        """
        Generate human-readable explanation of ranking for a job.

        Args:
            job: Job dict with ranking_signals and ranking_weights

        Returns:
            Dictionary with explanation components
        """
        signals = job.get("ranking_signals", {})
        weights = job.get("ranking_weights", {})

        contributions = {}
        for signal, value in signals.items():
            weight = weights.get(signal, 0)
            contributions[signal] = {
                "signal_value": value,
                "weight": weight,
                "contribution": round(value * weight * 100, 1)
            }

        # Sort by contribution
        sorted_contrib = sorted(
            contributions.items(),
            key=lambda x: x[1]["contribution"],
            reverse=True
        )

        explanations = []
        for signal, data in sorted_contrib:
            if data["contribution"] > 1:  # Only show meaningful contributions
                signal_name = {
                    "tfidf_cosine": "Nội dung CV phù hợp",
                    "skill_jaccard": "Kỹ năng khớp chính xác",
                    "skill_semantic": "Kỹ năng liên quan ngữ nghĩa",
                    "career_match": "Chuyên ngành phù hợp",
                    "recency": "Tin tuyển mới",
                    "salary": "Mức lương phù hợp"
                }.get(signal, signal)

                explanations.append({
                    "signal": signal,
                    "label": signal_name,
                    "value": f"{data['signal_value']*100:.0f}%",
                    "weight": f"{data['weight']*100:.0f}%",
                    "contribution": f"{data['contribution']:.1f}%"
                })

        return {
            "total_score": job.get("match_score", 0),
            "contributions": explanations,
            "summary": self._generate_summary(explanations)
        }

    def _generate_summary(self, explanations: List[Dict]) -> str:
        """Generate summary text from explanations."""
        if not explanations:
            return "Độ phù hợp tổng thể dựa trên nhiều yếu tố."

        top = explanations[0]
        if len(explanations) == 1:
            return f"Chủ yếu do {top['label'].lower()} ({top['contribution']})."

        second = explanations[1]
        return f"Chủ yếu do {top['label'].lower()} ({top['contribution']}) và {second['label'].lower()} ({second['contribution']})."


# Default engine instance
_default_engine: Optional[RankingEngine] = None


def get_ranking_engine() -> RankingEngine:
    """Get default RankingEngine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = RankingEngine()
    return _default_engine


def rank_jobs_for_user(
    cv_text: str,
    cv_skills: List[str],
    predicted_career: Optional[str],
    jobs: List[Dict],
    cv_vector: Any,
    job_vectors: List[Any]
) -> List[Dict]:
    """Convenience function for ranking."""
    return get_ranking_engine().rank_jobs(
        cv_text, cv_skills, predicted_career, jobs, cv_vector, job_vectors
    )


if __name__ == "__main__":
    # Test
    weights = RankingWeights()
    print("Default weights:", weights)
    print("Normalized:", weights.normalize())