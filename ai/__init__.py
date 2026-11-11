"""
AI Package - IT Career Match AI Modules
"""
from ai.recommender import (
    recommend_jobs_for_user,
    recommend_jobs,
    vectorize_cv,
    vectorize_job,
    calculate_similarity,
    predict_career,
    predict_career_top_k,
    get_all_active_jobs,
    get_user_skills,
    get_user_latest_cv_text,
)

from ai.skill_extractor import (
    extract_skills,
    SKILL_LIST,
    SKILL_ALIASES,
)

from ai.career_classifier import (
    CareerClassifier,
    get_classifier,
    predict_career as predict_career_clf,
    predict_career_proba,
    predict_career_top_k as predict_career_top_k_clf,
)

from ai.skill_gap import (
    analyze_skill_gap,
    get_skill_gap_details,
    get_skill_gap_summary,
    get_action_plan,
    get_skill_market_demand,
)

from ai.explanation import (
    generate_explanation,
)

from ai.text_preprocessing import (
    preprocess_text,
)

from ai.skill_matcher import (
    SkillMatcher,
    get_skill_matcher,
    match_skills_hybrid,
    find_related_skills,
    get_skill_suggestions,
)

from ai.embeddings_cache import (
    EmbeddingsCache,
    get_embeddings_cache,
    get_cached_skill_embeddings,
)

from ai.ranking import (
    RankingEngine,
    RankingWeights,
    RankingSignals,
    get_ranking_engine,
    rank_jobs_for_user,
)

from ai.learning_resources import (
    LearningResourceRecommender,
    get_learning_recommender,
    get_resources_for_skill,
    get_resources_for_skills,
    get_learning_path,
)

from ai.chatbot.engine import (
    get_bot_reply,
    get_suggestions,
    get_categories,
    search_knowledge,
    reload_knowledge_base,
)

__all__ = [
    # Recommender
    "recommend_jobs_for_user",
    "recommend_jobs",
    "vectorize_cv",
    "vectorize_job",
    "calculate_similarity",
    "predict_career",
    "predict_career_top_k",
    "get_all_active_jobs",
    "get_user_skills",
    "get_user_latest_cv_text",

    # Skill Extractor
    "extract_skills",
    "SKILL_LIST",
    "SKILL_ALIASES",

    # Career Classifier
    "CareerClassifier",
    "get_classifier",
    "predict_career_proba",
    "predict_career_top_k_clf",

    # Skill Gap
    "analyze_skill_gap",
    "get_skill_gap_details",
    "get_skill_gap_summary",
    "get_action_plan",
    "get_skill_market_demand",

    # Explanation
    "generate_explanation",

    # Text Preprocessing
    "preprocess_text",

    # Skill Matcher
    "SkillMatcher",
    "get_skill_matcher",
    "match_skills_hybrid",
    "find_related_skills",
    "get_skill_suggestions",

    # Embeddings Cache
    "EmbeddingsCache",
    "get_embeddings_cache",
    "get_cached_skill_embeddings",

    # Ranking
    "RankingEngine",
    "RankingWeights",
    "RankingSignals",
    "get_ranking_engine",
    "rank_jobs_for_user",

    # Learning Resources
    "LearningResourceRecommender",
    "get_learning_recommender",
    "get_resources_for_skill",
    "get_resources_for_skills",
    "get_learning_path",

    # Chatbot
    "get_bot_reply",
    "get_suggestions",
    "get_categories",
    "search_knowledge",
    "reload_knowledge_base",
]

# Version
__version__ = "2.0.0"