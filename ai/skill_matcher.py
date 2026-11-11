"""
Skill Matcher - Semantic skill matching using sentence embeddings
Hybrid approach: exact matching + alias expansion + semantic similarity
"""
import logging
from typing import List, Dict, Set, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ai.skill_extractor import SKILL_LIST, SKILL_ALIASES
from ai.embeddings_cache import get_embeddings_cache, get_cached_skill_embeddings

logger = logging.getLogger(__name__)

# Default embedding model (multilingual, supports Vietnamese + English)
DEFAULT_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Semantic similarity threshold for considering skills as related
DEFAULT_SEMANTIC_THRESHOLD = 0.75


class SkillMatcher:
    """
    Hybrid skill matcher combining:
    1. Exact matching (case-insensitive)
    2. Alias expansion (from SKILL_ALIASES)
    3. Semantic similarity (via sentence embeddings)
    """

    def __init__(
        self,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        semantic_threshold: float = DEFAULT_SEMANTIC_THRESHOLD,
        use_cache: bool = True
    ):
        self.embedding_model_name = embedding_model
        self.semantic_threshold = semantic_threshold
        self.use_cache = use_cache

        self._model = None
        self._embeddings_cache = get_embeddings_cache() if use_cache else None
        self._skill_embeddings = None
        self._skill_names = None
        self._skill_to_index = None
        self._is_initialized = False

    def _load_embedding_model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"Loaded embedding model: {self.embedding_model_name}")
            except ImportError:
                logger.warning("sentence-transformers not installed, semantic matching disabled")
                self._model = None
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self._model = None

    def _load_skill_embeddings(self) -> bool:
        """Load pre-computed skill embeddings from cache."""
        if not self.use_cache:
            return False

        embeddings, skill_names = get_cached_skill_embeddings()

        if len(embeddings) > 0 and len(skill_names) > 0:
            self._skill_embeddings = embeddings
            self._skill_names = skill_names
            self._skill_to_index = {name: i for i, name in enumerate(skill_names)}
            logger.info(f"Loaded {len(skill_names)} pre-computed skill embeddings")
            return True

        return False

    def initialize(self) -> bool:
        """
        Initialize the matcher: load model and embeddings.
        Returns True if semantic matching is available.
        """
        if self._is_initialized:
            return self._model is not None

        # Try loading cached embeddings first
        self._load_skill_embeddings()

        # Load model for on-the-fly embedding
        self._load_embedding_model()

        self._is_initialized = True

        semantic_available = self._model is not None
        logger.info(f"SkillMatcher initialized. Semantic matching: {'available' if semantic_available else 'unavailable'}")

        return semantic_available

    def compute_skill_embeddings(self, skill_names: List[str]) -> np.ndarray:
        """Compute embeddings for a list of skills."""
        self._load_embedding_model()

        if self._model is None:
            logger.warning("No embedding model available")
            return np.array([])

        try:
            embeddings = self._model.encode(skill_names, show_progress_bar=False, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to compute embeddings: {e}")
            return np.array([])

    def build_embeddings_cache(self, skill_list: List[str] = None) -> bool:
        """
        Build and save embeddings cache for all skills.

        Args:
            skill_list: List of skills to embed. Defaults to SKILL_LIST.

        Returns:
            True if successful
        """
        skills = skill_list or SKILL_LIST

        logger.info(f"Building embeddings cache for {len(skills)} skills...")

        embeddings = self.compute_skill_embeddings(skills)

        if len(embeddings) == 0:
            return False

        if self._embeddings_cache:
            return self._embeddings_cache.save(embeddings, skills)

        return False

    def _expand_with_aliases(self, skills: List[str]) -> Set[str]:
        """Expand skills using SKILL_ALIASES mapping."""
        expanded = set(skills)

        for skill in skills:
            # Check if skill is an alias
            if skill.lower() in SKILL_ALIASES:
                canonical = SKILL_ALIASES[skill.lower()]
                expanded.add(canonical)

            # Check if any alias maps to this skill
            for alias, canonical in SKILL_ALIASES.items():
                if canonical.lower() == skill.lower():
                    expanded.add(alias)

        return expanded

    def match_skills(
        self,
        cv_skills: List[str],
        job_skills: List[str],
        threshold: float = None
    ) -> Dict:
        """
        Match CV skills to job skills using hybrid approach.

        Args:
            cv_skills: List of skills from CV/profile
            job_skills: List of skills required by job
            threshold: Semantic similarity threshold (default from config)

        Returns:
            Dictionary with matched, missing, semantic_matched, exact_matched skills
        """
        if not self._is_initialized:
            self.initialize()

        threshold = threshold or self.semantic_threshold

        # Normalize skills (lowercase for comparison)
        cv_normalized = {s.lower(): s for s in cv_skills}
        job_normalized = {s.lower(): s for s in job_skills}

        # 1. Exact matching (case-insensitive)
        cv_lower = set(cv_normalized.keys())
        job_lower = set(job_normalized.keys())
        exact_matched = cv_lower & job_lower

        # 2. Alias expansion
        cv_expanded = self._expand_with_aliases(list(cv_lower))
        job_expanded = self._expand_with_aliases(list(job_lower))
        alias_matched = cv_expanded & job_expanded

        # Combine exact + alias matches
        all_matched_lower = exact_matched | alias_matched

        # 3. Semantic matching for remaining unmatched job skills
        remaining_job = job_lower - all_matched_lower
        semantic_matched = set()

        if remaining_job and self._model is not None and self._skill_embeddings is not None:
            # Embed remaining job skills
            job_skill_list = [job_normalized[s] for s in remaining_job]
            job_embeddings = self.compute_skill_embeddings(job_skill_list)

            if len(job_embeddings) > 0:
                # Compare with all known skill embeddings
                for i, job_skill in enumerate(job_skill_list):
                    job_emb = job_embeddings[i].reshape(1, -1)

                    # Compute similarity with all cached skills
                    similarities = cosine_similarity(job_emb, self._skill_embeddings)[0]

                    # Find best matches above threshold
                    best_indices = np.where(similarities >= threshold)[0]

                    for idx in best_indices:
                        matched_skill = self._skill_names[idx]
                        if matched_skill.lower() in cv_lower:
                            semantic_matched.add(job_skill)
                            break

        # Final matched set
        final_matched_lower = all_matched_lower | {s.lower() for s in semantic_matched}
        final_matched = [cv_normalized[s] for s in final_matched_lower if s in cv_normalized]

        # Missing skills (job skills not matched)
        missing_lower = job_lower - final_matched_lower
        missing = [job_normalized[s] for s in missing_lower]

        return {
            "matched_skills": sorted(final_matched),
            "missing_skills": sorted(missing),
            "exact_matched": sorted([cv_normalized[s] for s in exact_matched]),
            "alias_matched": sorted([cv_normalized[s] for s in (alias_matched - exact_matched) if s in cv_normalized]),
            "semantic_matched": sorted(list(semantic_matched)),
            "cv_skills": cv_skills,
            "job_skills": job_skills
        }

    def find_related_skills(self, skill: str, top_k: int = 5) -> List[Dict]:
        """
        Find skills semantically related to a given skill.

        Args:
            skill: Input skill name
            top_k: Number of related skills to return

        Returns:
            List of {"skill": str, "similarity": float} dicts
        """
        if not self._is_initialized:
            self.initialize()

        if self._model is None or self._skill_embeddings is None:
            return []

        try:
            # Embed the query skill
            query_emb = self._model.encode([skill], convert_to_numpy=True)[0].reshape(1, -1)

            # Compute similarities
            similarities = cosine_similarity(query_emb, self._skill_embeddings)[0]

            # Get top-k (excluding self)
            top_indices = similarities.argsort()[::-1]

            results = []
            for idx in top_indices:
                matched_skill = self._skill_names[idx]
                sim = float(similarities[idx])

                # Skip if it's the same skill (or very close)
                if matched_skill.lower() == skill.lower():
                    continue

                if sim >= self.semantic_threshold:
                    results.append({"skill": matched_skill, "similarity": round(sim, 3)})

                if len(results) >= top_k:
                    break

            return results

        except Exception as e:
            logger.error(f"find_related_skills failed: {e}")
            return []

    def get_skill_suggestions(self, user_skills: List[str], top_k: int = 10) -> List[Dict]:
        """
        Get skill suggestions based on user's current skills.
        Finds skills that are commonly paired with user's skills.

        Args:
            user_skills: List of user's current skills
            top_k: Number of suggestions to return

        Returns:
            List of suggested skills with scores
        """
        if not self._is_initialized:
            self.initialize()

        if self._model is None:
            return []

        all_suggestions = {}

        for skill in user_skills:
            related = self.find_related_skills(skill, top_k=5)
            for r in related:
                if r["skill"].lower() not in [s.lower() for s in user_skills]:
                    if r["skill"] not in all_suggestions:
                        all_suggestions[r["skill"]] = r["similarity"]
                    else:
                        all_suggestions[r["skill"]] = max(all_suggestions[r["skill"]], r["similarity"])

        # Sort by score
        sorted_suggestions = sorted(
            all_suggestions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"skill": skill, "relevance": round(score, 3)}
            for skill, score in sorted_suggestions[:top_k]
        ]


# Backward compatibility functions
_matcher_instance: Optional[SkillMatcher] = None


def get_skill_matcher() -> SkillMatcher:
    """Get singleton SkillMatcher instance."""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = SkillMatcher()
        _matcher_instance.initialize()
    return _matcher_instance


def match_skills_hybrid(cv_skills: List[str], job_skills: List[str], threshold: float = 0.75) -> Dict:
    """Backward compatible hybrid matching function."""
    return get_skill_matcher().match_skills(cv_skills, job_skills, threshold)


def find_related_skills(skill: str, top_k: int = 5) -> List[Dict]:
    """Backward compatible find related skills."""
    return get_skill_matcher().find_related_skills(skill, top_k)


def get_skill_suggestions(user_skills: List[str], top_k: int = 10) -> List[Dict]:
    """Backward compatible skill suggestions."""
    return get_skill_matcher().get_skill_suggestions(user_skills, top_k)


# CLI for building embeddings cache
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    matcher = SkillMatcher()
    matcher.initialize()

    if len(sys.argv) > 1 and sys.argv[1] == "build-cache":
        success = matcher.build_embeddings_cache()
        if success:
            print("Embeddings cache built successfully!")
        else:
            print("Failed to build embeddings cache")
            sys.exit(1)
    else:
        print("Usage: python -m ai.skill_matcher build-cache")