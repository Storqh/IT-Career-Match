"""
Explanation Generator - Detailed, actionable explanations for job recommendations
Uses rich skill gap analysis to provide specific, non-generic reasons.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def generate_explanation(
    predicted_career: Optional[str],
    job_category: Optional[str],
    skill_gap: Dict[str, Any],
    ranking_explanation: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate detailed, actionable explanation for a job recommendation.

    Args:
        predicted_career: Career predicted from user's CV
        job_category: Job's category
        skill_gap: Result from analyze_skill_gap (contains matched_skills, missing_skills, skill_details, etc.)
        ranking_explanation: Optional ranking signals explanation

    Returns:
        Dictionary with structured explanation components for UI rendering
    """
    matched_skills = skill_gap.get("matched_skills", [])
    missing_skills = skill_gap.get("missing_skills", [])
    missing_by_priority = skill_gap.get("missing_skills_by_priority", missing_skills)
    match_percentage = skill_gap.get("match_percentage", 0)
    skill_details = skill_gap.get("skill_details", [])
    required_skills = skill_gap.get("required_skills", [])
    preferred_skills = skill_gap.get("preferred_skills", [])
    resources = skill_gap.get("resources", {})
    extra_skills = skill_gap.get("extra_skills", [])

    # Build structured explanation
    explanation = {
        "match_percentage": match_percentage,
        "summary": "",
        "match_reasons": [],      # Why this job matches (strengths)
        "gaps": [],               # What's missing (with priority)
        "actions": [],            # Concrete learning steps
        "bonus_skills": extra_skills[:5],  # Skills user has that job doesn't require
        "career_alignment": "",
        "ranking_factors": [],
    }

    # 1. Career alignment explanation
    if predicted_career and job_category:
        if predicted_career == job_category:
            explanation["career_alignment"] = (
                f"✅ Công việc thuộc chính nhóm nghề **{predicted_career}** "
                "mà CV của bạn được dự đoán phù hợp nhất."
            )
        else:
            explanation["career_alignment"] = (
                f"⚠️ Công việc thuộc nhóm **{job_category}**, "
                f"trong khi CV của bạn phù hợp nhất với **{predicted_career}**. "
                "Đây có thể là cơ hội chuyển ngành hoặc mở rộng kỹ năng."
            )
    else:
        explanation["career_alignment"] = ""

    # 2. Match reasons (strengths) - specific, not generic
    if matched_skills:
        # Separate required vs preferred matched
        required_matched = [d for d in required_skills if d.status.value == "has" or d.status.value == "partial"]
        preferred_matched = [d for d in preferred_skills if d.status.value == "has" or d.status.value == "partial"]

        if required_matched:
            core_matched = [d.skill_name for d in required_matched if d.status.value == "has"]
            if core_matched:
                explanation["match_reasons"].append({
                    "type": "core_match",
                    "icon": "✅",
                    "title": "Đáp ứng kỹ năng cốt lõi",
                    "detail": f"Bạn đã có {len(core_matched)}/{len(required_matched)} kỹ năng bắt buộc: {', '.join(core_matched[:5])}"
                    + (f" và {len(core_matched) - 5} khác" if len(core_matched) > 5 else ""),
                    "skills": core_matched
                })

        if preferred_matched:
            pref_matched = [d.skill_name for d in preferred_matched if d.status.value == "has"]
            if pref_matched:
                explanation["match_reasons"].append({
                    "type": "preferred_match",
                    "icon": "⭐",
                    "title": "Có thêm kỹ năng ưu tiên",
                    "detail": f"Bạn sở hữu {len(pref_matched)} kỹ năng ưu tiên: {', '.join(pref_matched[:5])}"
                    + (f" và {len(pref_matched) - 5} khác" if len(pref_matched) > 5 else ""),
                    "skills": pref_matched
                })

        # Semantic/partial matches
        partial_matched = [d for d in skill_details if d.status.value == "partial"]
        if partial_matched:
            sem_skills = [d.skill_name for d in partial_matched]
            explanation["match_reasons"].append({
                "type": "semantic_match",
                "icon": "🔄",
                "title": "Kỹ năng liên quan (ngữ nghĩa)",
                "detail": f"Bạn có nền tảng cho: {', '.join(sem_skills[:3])}"
                + (f" và {len(sem_skills) - 3} khác" if len(sem_skills) > 3 else ""),
                "skills": sem_skills
            })

    # 3. Gaps (missing skills) - prioritized, with market context
    missing_required = [d for d in required_skills if d.status.value == "missing"]
    missing_preferred = [d for d in preferred_skills if d.status.value == "missing"]

    if missing_required:
        # Top 3 highest priority
        top_missing = sorted(missing_required, key=lambda x: x.priority_score, reverse=True)[:3]
        for d in top_missing:
            demand = d.market_demand
            demand_text = f" ({demand} việc làm đang tuyển)" if demand > 0 else ""
            explanation["gaps"].append({
                "type": "required_missing",
                "icon": "🔴",
                "priority": "Cao",
                "skill": d.skill_name,
                "reason": d.reason,
                "market_context": f"Kỹ năng bắt buộc{demand_text}",
                "resources": resources.get(d.skill_name, [])[:2],
                "priority_score": d.priority_score
            })

    if missing_preferred:
        top_missing = sorted(missing_preferred, key=lambda x: x.priority_score, reverse=True)[:2]
        for d in top_missing:
            demand = d.market_demand
            demand_text = f" ({demand} việc làm đang tuyển)" if demand > 0 else ""
            explanation["gaps"].append({
                "type": "preferred_missing",
                "icon": "🟡",
                "priority": "Trung bình",
                "skill": d.skill_name,
                "reason": d.reason,
                "market_context": f"Kỹ năng ưu tiên{demand_text}",
                "resources": resources.get(d.skill_name, [])[:2],
                "priority_score": d.priority_score
            })

    # 4. Actions - concrete learning steps from action_plan
    if missing_skills:
        # Get top priority missing skills with resources
        for skill in missing_by_priority[:3]:
            skill_resources = resources.get(skill, [])
            best_resource = skill_resources[0] if skill_resources else None
            priority_score = skill_gap.get("priority_scores", {}).get(skill, 0)
            priority_label = "Cao" if priority_score > 2 else "Trung bình" if priority_score > 1 else "Thấp"

            explanation["actions"].append({
                "skill": skill,
                "priority": priority_label,
                "priority_score": priority_score,
                "action": f"Học {skill}",
                "time_estimate": _estimate_learning_time(skill),
                "resource": best_resource,
                "all_resources": skill_resources[:3]
            })

    # 5. Summary text (concise, for card view)
    explanation["summary"] = _generate_summary_text(
        match_percentage, matched_skills, missing_required, missing_preferred,
        predicted_career, job_category, extra_skills
    )

    # 6. Ranking factors (if available)
    if ranking_explanation and ranking_explanation.get("contributions"):
        for contrib in ranking_explanation["contributions"][:3]:
            explanation["ranking_factors"].append({
                "label": contrib["label"],
                "value": contrib["value"],
                "contribution": contrib["contribution"]
            })

    return explanation


def _generate_summary_text(
    match_pct: float,
    matched: List[str],
    missing_required: List,
    missing_preferred: List,
    predicted_career: Optional[str],
    job_category: Optional[str],
    bonus: List[str]
) -> str:
    """Generate concise summary for card display."""
    if match_pct >= 80:
        level = "Rất phù hợp"
        emoji = "🎯"
    elif match_pct >= 60:
        level = "Phù hợp khá"
        emoji = "✅"
    elif match_pct >= 40:
        level = "Phù hợp một phần"
        emoji = "⚠️"
    else:
        level = "Cần bổ sung kỹ năng"
        emoji = "📚"

    parts = [f"{emoji} **{level}** ({match_pct:.0f}%)"]

    if matched:
        core_matched = matched[:3]
        parts.append(f"Đã có: {', '.join(core_matched)}"
                     + (f" +{len(matched)-3} khác" if len(matched) > 3 else ""))

    total_missing = len(missing_required) + len(missing_preferred)
    if total_missing > 0:
        top_missing = [d.skill_name for d in missing_required[:2]] + [d.skill_name for d in missing_preferred[:1]]
        parts.append(f"Thiếu: {', '.join(top_missing)}"
                     + (f" +{total_missing - len(top_missing)} khác" if total_missing > len(top_missing) else ""))

    if bonus:
        parts.append(f"Kỹ năng thêm: {', '.join(bonus[:2])}")

    if predicted_career == job_category and predicted_career:
        parts.append(f"✓ Đúng chuyên ngành {predicted_career}")

    return " | ".join(parts)


def _estimate_learning_time(skill: str) -> str:
    """Estimate learning time for a skill."""
    time_estimates = {
        "html/css": "1-2 tuần",
        "javascript": "3-4 tuần",
        "typescript": "2-3 tuần",
        "react": "3-4 tuần",
        "vue.js": "2-3 tuần",
        "angular": "4-6 tuần",
        "python": "3-4 tuần",
        "java": "4-6 tuần",
        "go": "2-3 tuần",
        "rust": "6-8 tuần",
        "sql": "1-2 tuần",
        "postgresql": "2-3 tuần",
        "mongodb": "2-3 tuần",
        "docker": "1-2 tuần",
        "kubernetes": "3-4 tuần",
        "aws": "4-6 tuần",
        "machine learning": "6-8 tuần",
        "deep learning": "8-12 tuần",
        "system design": "4-6 tuần",
    }
    return time_estimates.get(skill.lower(), "2-4 tuần")


# Backward compatibility
def generate_explanation_legacy(
    predicted_career,
    job_category,
    matched_skills,
    missing_skills
):
    """Legacy function signature - returns string only."""
    reasons = []

    if predicted_career == job_category:
        reasons.append(
            f"Công việc thuộc đúng nhóm nghề {predicted_career} "
            "được mô hình dự đoán từ CV."
        )
    else:
        reasons.append(
            f"Công việc thuộc nhóm {job_category}, trong khi CV "
            f"được dự đoán phù hợp nhất với {predicted_career}."
        )

    if matched_skills:
        reasons.append(
            "Các kỹ năng phù hợp: "
            + ", ".join(matched_skills[:5])
            + ("." if len(matched_skills) <= 5 else f" và {len(matched_skills) - 5} khác.")
        )

    if missing_skills:
        reasons.append(
            "Các kỹ năng nên bổ sung: "
            + ", ".join(missing_skills[:5])
            + ("." if len(missing_skills) <= 5 else f" và {len(missing_skills) - 5} khác.")
        )

    return " ".join(reasons)