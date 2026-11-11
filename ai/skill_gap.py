"""
Skill Gap Analysis v3 - Enhanced with match status, required/preferred, CV evidence, priority scoring
"""
import logging
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ai.skill_extractor import extract_skills
from ai.learning_resources import get_learning_path, get_resources_for_skills
from database.connection_pool import get_cursor

logger = logging.getLogger(__name__)


class MatchStatus(Enum):
    """Match status for a job skill."""
    HAS = "has"              # User has this skill (exact match)
    PARTIAL = "partial"      # User has related/semantic match
    MISSING = "missing"      # User doesn't have this skill


@dataclass
class SkillMatchDetail:
    """Detailed match information for a single job skill."""
    skill_name: str
    status: MatchStatus
    reason: str
    is_required: bool
    cv_evidence: Optional[str] = None
    proficiency: Optional[str] = None
    market_demand: int = 0
    priority_score: float = 0.0
    related_cv_skills: List[str] = None


@dataclass
class SkillGapResult:
    """Structured skill gap analysis result."""
    cv_skills: List[str]
    job_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    match_ratio: float
    match_percentage: float
    total_required: int
    total_matched: int
    total_missing: int
    # Enhanced fields
    market_demand: Dict[str, int]  # skill -> job count
    priority_scores: Dict[str, float]  # skill -> priority score
    learning_path: Optional[Dict] = None
    resources: Optional[Dict] = None
    # New: detailed match status per job skill
    skill_details: List[SkillMatchDetail] = None
    # Grouped skills for UI
    required_skills: List[SkillMatchDetail] = None
    preferred_skills: List[SkillMatchDetail] = None


def get_skill_market_demand(skills: List[str] = None) -> Dict[str, int]:
    """
    Get market demand for skills (frequency in active jobs).

    Args:
        skills: Optional list of skills to check. If None, get all.

    Returns:
        Dictionary mapping skill -> number of active jobs requiring it
    """
    try:
        with get_cursor() as cur:
            if skills:
                normalized_skills = [skill.strip() for skill in skills if isinstance(skill, str) and skill.strip()]
                if not normalized_skills:
                    return {}
                placeholders = ", ".join(["%s"] * len(normalized_skills))
                cur.execute(f"""
                    SELECT s.skill_name, COUNT(DISTINCT js.job_id) as job_count
                    FROM job_skills js
                    JOIN skills s ON js.skill_id = s.skill_id
                    JOIN jobs j ON js.job_id = j.job_id
                    WHERE j.status = 'active' AND s.skill_name IN ({placeholders})
                    GROUP BY s.skill_id, s.skill_name
                """, normalized_skills)
            else:
                cur.execute("""
                    SELECT s.skill_name, COUNT(DISTINCT js.job_id) as job_count
                    FROM job_skills js
                    JOIN skills s ON js.skill_id = s.skill_id
                    JOIN jobs j ON js.job_id = j.job_id
                    WHERE j.status = 'active'
                    GROUP BY s.skill_id, s.skill_name
                    ORDER BY job_count DESC
                    LIMIT 100
                """)

            return {row["skill_name"]: row["job_count"] for row in cur.fetchall()}
    except Exception as exc:  # pragma: no cover - fallback for tests without database
        logger.warning("Unable to fetch market demand; using empty fallback: %s", exc)
        if skills:
            normalized_skills = [skill.strip() for skill in skills if isinstance(skill, str) and skill.strip()]
            return {skill: 0 for skill in normalized_skills}
        return {}


def calculate_priority_score(
    skill: str,
    market_demand: int,
    user_has_skill: bool,
    job_category: str = "",
    role_relevance: float = 1.0
) -> float:
    """
    Calculate priority score for a missing skill.

    Formula: priority = market_demand * (1 - user_proficiency) * role_relevance

    Args:
        skill: Skill name (for future category-specific logic)
        market_demand: Number of jobs requiring this skill
        user_has_skill: Whether user already has this skill
        job_category: Job category for role relevance (for future use)
        role_relevance: Role relevance multiplier (0-1)

    Returns:
        Priority score (higher = more important to learn)
    """
    if user_has_skill:
        return 0.0

    # Normalize market demand (log scale to prevent domination by very popular skills)
    import math
    demand_score = math.log1p(market_demand)  # log(1 + count)

    # User proficiency: 0 if missing, 1 if has
    proficiency = 1.0 if user_has_skill else 0.0

    priority = demand_score * (1 - proficiency) * role_relevance

    return round(priority, 3)


def get_job_skill_requirements(job_id: int) -> List[Dict]:
    """
    Get job skills with importance level (required/preferred).

    Args:
        job_id: Job ID

    Returns:
        List of dicts with skill_name, importance_level
    """
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.skill_name, js.importance_level
            FROM job_skills js
            JOIN skills s ON js.skill_id = s.skill_id
            WHERE js.job_id = %s
            ORDER BY s.skill_name
        """, (job_id,))
        rows = cur.fetchall()
        result = []
        for row in rows:
            importance = row.get("importance_level")
            if importance is None:
                importance = "required"
            result.append({"skill_name": row["skill_name"], "importance_level": importance})
        return result


def get_latest_cv_skills(user_id: int) -> Tuple[List[str], str]:
    """
    Get skills from user's latest CV, fallback to profile skills.

    Returns:
        Tuple of (skill_list, source) where source is "cv" or "profile"
    """
    with get_cursor() as cur:
        # Get latest CV
        cur.execute("""
            SELECT extracted_skills FROM cvs
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        cv = cur.fetchone()

        if cv and cv["extracted_skills"]:
            return cv["extracted_skills"], "cv"

        # Fallback to profile skills
        cur.execute("""
            SELECT s.skill_name
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.skill_id
            WHERE ss.user_id = %s
            ORDER BY s.skill_name
        """, (user_id,))
        rows = cur.fetchall()
        return [row["skill_name"] for row in rows], "profile"


def find_cv_evidence(cv_text: str, job_skill: str) -> Optional[str]:
    """
    Find evidence of a skill in CV text.

    Args:
        cv_text: Raw CV text
        job_skill: Skill to find evidence for

    Returns:
        Snippet of CV text showing the skill, or None
    """
    if not cv_text:
        return None

    import re
    # Look for the skill in context (50 chars before and after)
    pattern = re.compile(re.escape(job_skill), re.IGNORECASE)
    match = pattern.search(cv_text)
    if match:
        start = max(0, match.start() - 50)
        end = min(len(cv_text), match.end() + 50)
        snippet = cv_text[start:end].strip()
        # Clean up snippet
        snippet = re.sub(r'\s+', ' ', snippet)
        return f"...{snippet}..."
    return None


def get_proficiency_from_cv(cv_text: str, skill: str) -> Optional[str]:
    """
    Infer proficiency level from CV text context.

    Returns:
        "beginner", "intermediate", "advanced", or None
    """
    if not cv_text:
        return None

    import re
    # Look for years of experience or proficiency indicators that directly modify this skill
    # Use smaller context window (50 chars) to avoid cross-contamination between skills
    pattern = re.compile(rf'(.{{0,50}}{re.escape(skill)}.{{0,50}})', re.IGNORECASE)
    matches = pattern.findall(cv_text)

    skill_lower = skill.lower()

    for match in matches:
        match_lower = match.lower()
        # Check for years of experience specifically mentioning this skill
        years_match = re.search(rf'(\d+)\s*(?:year|yr|năm).*{re.escape(skill_lower)}|{re.escape(skill_lower)}.*(\d+)\s*(?:year|yr|năm)', match_lower)
        if years_match:
            years = int(years_match.group(1) or years_match.group(2))
            if years >= 5:
                return "advanced"
            elif years >= 2:
                return "intermediate"
            else:
                return "beginner"

        # Check for proficiency keywords that DIRECTLY modify this skill
        # Patterns: "expert in X", "X expert", "senior X", "lead X", "architect X"
        # "proficient in X", "X proficiency", "good at X", "strong X", "solid X"
        # "basic X", "familiar with X", "know X", "know how to X"
        # "knowledge of X", "cơ bản X", "biết X", "hiểu X", "am hiểu X", "kinh nghiệm X"

        # Advanced patterns
        advanced_patterns = [
            rf'expert\s+in\s+{re.escape(skill_lower)}',
            rf'{re.escape(skill_lower)}\s+expert',
            rf'senior\s+{re.escape(skill_lower)}',
            rf'lead\s+{re.escape(skill_lower)}',
            rf'architect\s+{re.escape(skill_lower)}',
            rf'chuyên\s+gia\s+{re.escape(skill_lower)}',
        ]
        for p in advanced_patterns:
            if re.search(p, match_lower):
                return "advanced"

        # Intermediate patterns
        intermediate_patterns = [
            rf'proficient\s+in\s+{re.escape(skill_lower)}',
            rf'{re.escape(skill_lower)}\s+proficiency',
            rf'good\s+at\s+{re.escape(skill_lower)}',
            rf'strong\s+{re.escape(skill_lower)}',
            rf'solid\s+{re.escape(skill_lower)}',
            rf'kinh\s+nghiệm\s+{re.escape(skill_lower)}',
            rf'am\s+hiểu\s+{re.escape(skill_lower)}',
        ]
        for p in intermediate_patterns:
            if re.search(p, match_lower):
                return "intermediate"

        # Beginner patterns
        beginner_patterns = [
            rf'basic\s+{re.escape(skill_lower)}',
            rf'familiar\s+with\s+{re.escape(skill_lower)}',
            rf'know\s+(?:how\s+to\s+)?{re.escape(skill_lower)}',
            rf'knowledge\s+of\s+{re.escape(skill_lower)}',
            rf'cơ\s+bản\s+{re.escape(skill_lower)}',
            rf'biết\s+{re.escape(skill_lower)}',
            rf'hiểu\s+{re.escape(skill_lower)}',
        ]
        for p in beginner_patterns:
            if re.search(p, match_lower):
                return "beginner"

    return None


def analyze_skill_gap(
    cv_text: Union[str, List[str]],
    job_text: Union[str, List[str]],
    job_category: str = "",
    include_resources: bool = True,
    include_learning_path: bool = True,
    job_id: Optional[int] = None,
    user_id: Optional[int] = None,
    cv_raw_text: Optional[str] = None
) -> Dict:
    """
    Enhanced skill gap analysis with:
    - Match status per job skill (Has/Partial/Missing with reason)
    - Required vs Preferred distinction
    - CV evidence and proficiency
    - Priority based on JD requirement + market demand
    - Learning resources from backend

    Args:
        cv_text: Raw CV text or pre-extracted skill list
        job_text: Raw job text or pre-extracted skill list
        job_category: Job category for role relevance
        include_resources: Whether to include learning resources
        include_learning_path: Whether to generate learning path
        job_id: Job ID for fetching required/preferred skills
        user_id: User ID for fetching latest CV skills
        cv_raw_text: Raw CV text for evidence extraction

    Returns:
        Dictionary with comprehensive gap analysis
    """
    # If user_id provided, fetch latest CV skills (with fallback to profile)
    if user_id is not None:
        cv_skills, skill_source = get_latest_cv_skills(user_id)
    else:
        # Handle cv_text - could be string or list
        if isinstance(cv_text, list):
            cv_skills = cv_text
        else:
            cv_skills = extract_skills(cv_text)
        skill_source = "provided"

    # If job_id provided, get skills with importance levels
    if job_id is not None:
        job_skill_data = get_job_skill_requirements(job_id)
        job_skills = [s["skill_name"] for s in job_skill_data]
        skill_importance = {s["skill_name"]: s.get("importance_level", "required") for s in job_skill_data}
    else:
        # Handle job_text - could be string or list
        if isinstance(job_text, list):
            job_skills = job_text
        else:
            job_skills = extract_skills(job_text)
        skill_importance = {skill: "required" for skill in job_skills}

    # Normalize skills (lowercase for comparison)
    cv_normalized = {s.lower(): s for s in cv_skills}
    job_normalized = {s.lower(): s for s in job_skills}

    job_lower = set(job_normalized.keys())

    # Deduplicate job_skills while preserving order (for handling duplicate inputs)
    seen = set()
    unique_job_skills = []
    for s in job_skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique_job_skills.append(s)
    job_skills = unique_job_skills

    # Get market demand for all relevant skills
    all_relevant_skills = list(job_skills) + list(cv_skills)
    market_demand = get_skill_market_demand(all_relevant_skills)

    # Build detailed match info for each job skill
    skill_details = []
    matched_skills = []
    missing_skills = []

    from ai.skill_matcher import match_skills_hybrid

    # Use hybrid matching for semantic/alias matches
    hybrid_result = match_skills_hybrid(cv_skills, job_skills)
    exact_matched = set(s.lower() for s in hybrid_result.get("exact_matched", []))
    alias_matched = set(s.lower() for s in hybrid_result.get("alias_matched", []))
    semantic_matched = set(s.lower() for s in hybrid_result.get("semantic_matched", []))

    for job_skill in job_skills:
        job_skill_lower = job_skill.lower()
        is_required = skill_importance.get(job_skill, "required") == "required"

        # Determine match status and reason
        if job_skill_lower in exact_matched:
            status = MatchStatus.HAS
            reason = "Khớp chính xác với kỹ năng trong CV"
            related_cv_skills = [cv_normalized[job_skill_lower]]
        elif job_skill_lower in alias_matched:
            status = MatchStatus.HAS
            # Find which alias matched
            matched_alias = None
            for cv_skill in cv_skills:
                if cv_skill.lower() in job_skill_lower or job_skill_lower in cv_skill.lower():
                    matched_alias = cv_skill
                    break
            reason = f"Khớp qua别名: {matched_alias or 'tương đương'}"
            related_cv_skills = [matched_alias] if matched_alias else []
        elif job_skill_lower in semantic_matched:
            status = MatchStatus.PARTIAL
            reason = "Khớp ngữ nghĩa (kỹ năng liên quan)"
            # Find related CV skills
            related = []
            for cv_skill in cv_skills:
                # Check if semantically related (simplified)
                if cv_skill.lower() != job_skill_lower:
                    related.append(cv_skill)
            related_cv_skills = related[:3]
        else:
            status = MatchStatus.MISSING
            reason = "Chưa có trong CV/hồ sơ"
            related_cv_skills = []

        # Get CV evidence and proficiency if raw text available
        cv_evidence = None
        proficiency = None
        if cv_raw_text and status != MatchStatus.MISSING:
            cv_evidence = find_cv_evidence(cv_raw_text, job_skill)
            proficiency = get_proficiency_from_cv(cv_raw_text, job_skill)

        demand = market_demand.get(job_skill, 0)
        user_has = status != MatchStatus.MISSING

        # Role relevance based on job category
        role_relevance = 1.0
        if job_category:
            # Could add category-specific logic here
            pass

        priority_score = calculate_priority_score(
            job_skill, demand, user_has, job_category, role_relevance
        )

        detail = SkillMatchDetail(
            skill_name=job_skill,
            status=status,
            reason=reason,
            is_required=is_required,
            cv_evidence=cv_evidence,
            proficiency=proficiency,
            market_demand=demand,
            priority_score=priority_score,
            related_cv_skills=related_cv_skills
        )
        skill_details.append(detail)

        if status == MatchStatus.HAS or status == MatchStatus.PARTIAL:
            matched_skills.append(job_skill)
        else:
            missing_skills.append(job_skill)

    # Extra skills (user has but job doesn't require)
    extra_skills = sorted([s for s in cv_skills if s.lower() not in job_lower])

    match_ratio = len(matched_skills) / max(len(job_skills), 1)
    match_percentage = round(match_ratio * 100, 1)

    # Group by required/preferred
    required_skills = [d for d in skill_details if d.is_required]
    preferred_skills = [d for d in skill_details if not d.is_required]

    # Sort missing required skills by priority
    missing_required = sorted(
        [d for d in required_skills if d.status == MatchStatus.MISSING],
        key=lambda x: x.priority_score,
        reverse=True
    )
    missing_preferred = sorted(
        [d for d in preferred_skills if d.status == MatchStatus.MISSING],
        key=lambda x: x.priority_score,
        reverse=True
    )

    # Priority scores dict for backward compatibility
    priority_scores = {d.skill_name: d.priority_score for d in skill_details}

    # Missing skills by priority (required first, then preferred)
    missing_by_priority = [d.skill_name for d in missing_required] + [d.skill_name for d in missing_preferred]

    result = {
        "cv_skills": cv_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "missing_skills_by_priority": missing_by_priority,
        "extra_skills": extra_skills,
        "match_ratio": round(match_ratio, 3),
        "match_percentage": match_percentage,
        "total_required": len(job_skills),
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills),
        "market_demand": market_demand,
        "priority_scores": priority_scores,
        "skill_details": skill_details,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "skill_source": skill_source,
    }

    # Add learning resources
    if include_resources and missing_skills:
        result["resources"] = get_resources_for_skills(missing_by_priority[:10], max_per_skill=3)

    # Add learning path
    if include_learning_path and missing_skills:
        result["learning_path"] = get_learning_path(missing_by_priority, job_category)

    return result


def get_skill_gap_summary(gap_result: Dict) -> str:
    """Generate human-readable summary of skill gap."""
    matched = gap_result.get("matched_skills", [])
    missing = gap_result.get("missing_skills", [])
    match_pct = gap_result.get("match_percentage", 0)

    if not missing:
        return f"🎉 Tuyệt vời! Bạn đáp ứng 100% kỹ năng yêu cầu ({len(matched)}/{len(matched)})."

    if match_pct >= 80:
        level = "Rất tốt"
    elif match_pct >= 60:
        level = "Khá"
    elif match_pct >= 40:
        level = "Trung bình"
    else:
        level = "Cần cải thiện"

    top_missing = missing[:3]
    missing_str = ", ".join(top_missing)
    if len(missing) > 3:
        missing_str += f" và {len(missing) - 3} kỹ năng khác"

    return (
        f"{level}: Bạn khớp {match_pct}% kỹ năng ({len(matched)}/{len(matched)+len(missing)}). "
        f"Kỹ năng thiếu quan trọng: {missing_str}."
    )


def get_action_plan(gap_result: Dict, max_skills: int = 5) -> List[Dict]:
    """
    Generate actionable learning plan from gap analysis.

    Returns:
        List of action items with skill, priority, resources, time estimate
    """
    missing = gap_result.get("missing_skills_by_priority", gap_result.get("missing_skills", []))
    priority_scores = gap_result.get("priority_scores", {})
    resources = gap_result.get("resources", {})

    actions = []
    for i, skill in enumerate(missing[:max_skills]):
        priority = priority_scores.get(skill, 0)
        skill_resources = resources.get(skill, [])

        # Estimate time based on skill complexity (simplified)
        time_estimates = {
            "html/css": "1-2 weeks",
            "javascript": "3-4 weeks",
            "typescript": "2-3 weeks",
            "react": "3-4 weeks",
            "vue.js": "2-3 weeks",
            "angular": "4-6 weeks",
            "python": "3-4 weeks",
            "java": "4-6 weeks",
            "go": "2-3 weeks",
            "rust": "6-8 weeks",
            "sql": "1-2 weeks",
            "postgresql": "2-3 weeks",
            "mongodb": "2-3 weeks",
            "docker": "1-2 weeks",
            "kubernetes": "3-4 weeks",
            "aws": "4-6 weeks",
            "machine learning": "6-8 weeks",
            "deep learning": "8-12 weeks",
            "system design": "4-6 weeks",
        }

        time_estimate = time_estimates.get(skill.lower(), "2-4 weeks")

        # Get best resource
        best_resource = skill_resources[0] if skill_resources else None

        actions.append({
            "step": i + 1,
            "skill": skill,
            "priority_score": priority,
            "priority_label": "Cao" if priority > 2 else "Trung bình" if priority > 1 else "Thấp",
            "time_estimate": time_estimate,
            "best_resource": best_resource,
            "all_resources": skill_resources,
            "action": f"Học {skill} ({time_estimate})"
        })

    return actions


# Backward compatibility
def get_skill_gap_details(cv_skills: List[str], job_skills: List[str]) -> Dict:
    """Original function signature for backward compatibility."""
    return analyze_skill_gap(cv_skills, job_skills)


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    # Test
    cv = "Python, SQL, Machine Learning, Pandas, NumPy, Docker"
    job = "Python, SQL, Machine Learning, TensorFlow, Kubernetes, AWS, Docker, React"

    result = analyze_skill_gap(cv, job, "Data Science")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n--- Action Plan ---")
    for action in get_action_plan(result):
        print(f"Step {action['step']}: {action['action']} | Priority: {action['priority_label']} | Resource: {action['best_resource']['title'] if action['best_resource'] else 'N/A'}")