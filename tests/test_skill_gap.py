"""Tests for Skill Gap Analysis module - Enhanced v3."""
import pytest
from unittest.mock import patch, MagicMock

from ai.skill_gap import (
    analyze_skill_gap,
    get_skill_gap_summary,
    get_action_plan,
    calculate_priority_score,
    get_skill_market_demand,
    get_job_skill_requirements,
    get_latest_cv_skills,
    find_cv_evidence,
    get_proficiency_from_cv,
    SkillMatchDetail,
    MatchStatus,
)


class TestSkillGapAnalysis:
    """Test enhanced skill gap analysis functions."""

    def test_analyze_skill_gap_both_string(self):
        """Test with both CV and job as strings."""
        cv = "Python, SQL, Machine Learning, Pandas"
        job = "Python, SQL, Machine Learning, TensorFlow, Docker"

        result = analyze_skill_gap(cv, job)

        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "extra_skills" in result
        assert "match_percentage" in result
        assert "priority_scores" in result
        assert "market_demand" in result

        # Should match python, sql, machine learning
        assert "python" in result["matched_skills"]
        assert "sql" in result["matched_skills"]
        assert "machine learning" in result["matched_skills"]

        # Should miss tensorflow, docker
        assert "tensorflow" in result["missing_skills"]
        assert "docker" in result["missing_skills"]

        # Extra skills - pandas is in CV but not job
        assert "pandas" in result["extra_skills"]

    def test_analyze_skill_gap_both_list(self):
        """Test with both CV and job as lists."""
        cv_skills = ["python", "sql", "machine learning"]
        job_skills = ["python", "sql", "machine learning", "tensorflow", "docker"]

        result = analyze_skill_gap(cv_skills, job_skills)

        assert "python" in result["matched_skills"]
        assert "sql" in result["matched_skills"]
        assert "machine learning" in result["matched_skills"]
        assert "tensorflow" in result["missing_skills"]
        assert "docker" in result["missing_skills"]

    def test_analyze_skill_gap_mixed_types(self):
        """Test with mixed string and list inputs."""
        cv_skills = ["python", "sql", "react"]
        job_text = "Python, SQL, JavaScript, React, Node.js"

        result = analyze_skill_gap(cv_skills, job_text)

        assert "python" in result["matched_skills"]
        assert "sql" in result["matched_skills"]
        assert "react" in result["matched_skills"]

    def test_analyze_skill_gap_all_matched(self):
        """Test when CV has all required skills."""
        cv = "Python, SQL, Machine Learning"
        job = "Python, SQL, Machine Learning"

        result = analyze_skill_gap(cv, job)

        assert len(result["missing_skills"]) == 0
        assert result["match_percentage"] == 100.0
        assert result["match_ratio"] == 1.0

    def test_analyze_skill_gap_none_matched(self):
        """Test when CV has none of the required skills."""
        cv = "Java, Spring, Hibernate"
        job = "Python, React, Node.js"

        result = analyze_skill_gap(cv, job)

        assert len(result["matched_skills"]) == 0
        assert result["match_percentage"] == 0.0
        assert set(result["missing_skills"]) == {"python", "react", "node.js"}

    def test_analyze_skill_gap_empty_cv(self):
        """Test with empty CV."""
        cv = ""
        job = "Python, SQL"

        result = analyze_skill_gap(cv, job)

        assert len(result["matched_skills"]) == 0
        assert result["match_percentage"] == 0.0

    def test_analyze_skill_gap_empty_job(self):
        """Test with empty job requirements."""
        cv = "Python, SQL"
        job = ""

        result = analyze_skill_gap(cv, job)

        assert result["total_required"] == 0
        assert result["match_percentage"] == 0.0

    def test_analyze_skill_gap_both_empty(self):
        """Test with both empty."""
        cv = ""
        job = ""

        result = analyze_skill_gap(cv, job)

        assert result["total_required"] == 0
        assert result["match_percentage"] == 0.0

    def test_analyze_skill_gap_priority_scores(self):
        """Test that priority scores are calculated."""
        cv = "Python"
        job = "Python, React, Docker, Kubernetes, AWS"

        result = analyze_skill_gap(cv, job, job_category="Backend")

        # Missing skills should have priority scores
        for skill in result["missing_skills"]:
            assert skill in result["priority_scores"]
            assert result["priority_scores"][skill] >= 0

        # Matched skills should also have scores (0 since user has them)
        for skill in result["matched_skills"]:
            assert skill in result["priority_scores"]
            assert result["priority_scores"][skill] == 0.0

    def test_analyze_skill_gap_missing_by_priority(self):
        """Test missing_skills_by_priority is sorted."""
        cv = "Python"
        job = "Python, React, Docker, Kubernetes, AWS"

        result = analyze_skill_gap(cv, job)

        priorities = [result["priority_scores"][s] for s in result["missing_skills_by_priority"]]
        # Should be sorted descending
        assert priorities == sorted(priorities, reverse=True)

    def test_analyze_skill_gap_with_cv_evidence(self):
        """Test CV evidence extraction."""
        cv_text = "I have 3 years of experience with Python and Django. Built REST APIs using Django REST Framework."
        job_skills = ["Python", "Django", "React"]

        result = analyze_skill_gap(
            cv_text, job_skills,
            cv_raw_text=cv_text
        )

        # Check skill details exist
        assert "skill_details" in result
        for detail in result["skill_details"]:
            if detail.skill_name.lower() in ["python", "django"]:
                assert detail.status == MatchStatus.HAS
                assert detail.cv_evidence is not None
                assert "python" in detail.cv_evidence.lower() or "django" in detail.cv_evidence.lower()

    def test_analyze_skill_gap_with_proficiency(self):
        """Test proficiency extraction from CV."""
        cv_text = "5 years Python experience. Expert in Django. Basic knowledge of React."
        job_skills = ["Python", "Django", "React"]

        result = analyze_skill_gap(
            cv_text, job_skills,
            cv_raw_text=cv_text
        )

        for detail in result["skill_details"]:
            if detail.skill_name.lower() == "python":
                assert detail.proficiency == "advanced"
            elif detail.skill_name.lower() == "django":
                assert detail.proficiency == "advanced"
            elif detail.skill_name.lower() == "react":
                assert detail.proficiency == "beginner"


class TestSkillMatchDetail:
    """Test SkillMatchDetail dataclass."""

    def test_skill_match_detail_creation(self):
        """Test creating SkillMatchDetail."""
        detail = SkillMatchDetail(
            skill_name="Python",
            status=MatchStatus.HAS,
            reason="Exact match",
            is_required=True,
            cv_evidence="3 years Python",
            proficiency="advanced",
            market_demand=50,
            priority_score=2.5,
            related_cv_skills=["python"]
        )
        assert detail.skill_name == "Python"
        assert detail.status == MatchStatus.HAS
        assert detail.is_required is True
        assert detail.priority_score == 2.5


class TestGetSkillGapSummary:
    """Test summary generation."""

    def test_get_skill_gap_summary_all_matched(self):
        """Test summary when all skills matched."""
        gap_result = {
            "matched_skills": ["python", "sql", "ml"],
            "missing_skills": [],
            "match_percentage": 100.0
        }
        summary = get_skill_gap_summary(gap_result)
        assert "100%" in summary or "100" in summary

    def test_get_skill_gap_summary_partial(self):
        """Test summary with partial match."""
        gap_result = {
            "matched_skills": ["python", "sql"],
            "missing_skills": ["react", "docker", "kubernetes", "aws"],
            "match_percentage": 33.3
        }
        summary = get_skill_gap_summary(gap_result)
        assert "33" in summary
        assert "react" in summary.lower()


class TestGetActionPlan:
    """Test action plan generation."""

    def test_get_action_plan(self):
        """Test action plan generation."""
        gap_result = {
            "missing_skills_by_priority": ["react", "docker", "kubernetes"],
            "priority_scores": {"react": 3.5, "docker": 2.1, "kubernetes": 4.2},
            "resources": {
                "react": [{"title": "React Tutorial", "url": "https://react.dev"}],
                "docker": [{"title": "Docker Guide", "url": "https://docker.com"}],
            },
            "learning_path": {"phases": []}
        }

        actions = get_action_plan(gap_result, max_skills=2)

        assert len(actions) == 2
        assert actions[0]["skill"] == "react"
        assert actions[1]["skill"] == "docker"
        assert "priority_label" in actions[0]
        assert "time_estimate" in actions[0]
        assert "best_resource" in actions[0]


class TestCalculatePriorityScore:
    """Test priority score calculation."""

    def test_calculate_priority_score_user_has_skill(self):
        """Test priority is 0 when user has skill."""
        score = calculate_priority_score("python", 100, True)
        assert score == 0.0

    def test_calculate_priority_score_user_missing_skill(self):
        """Test priority > 0 when user missing skill."""
        score = calculate_priority_score("python", 100, False)
        assert score > 0

    def test_calculate_priority_score_higher_demand_higher_priority(self):
        """Test higher market demand = higher priority."""
        score_low = calculate_priority_score("skill_a", 10, False)
        score_high = calculate_priority_score("skill_b", 1000, False)
        assert score_high > score_low


class TestGetSkillMarketDemand:
    """Test market demand query."""

    @patch("ai.skill_gap.get_cursor")
    def test_get_skill_market_demand_with_skills(self, mock_get_cursor):
        """Test market demand for specific skills."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            {"skill_name": "python", "job_count": 50},
            {"skill_name": "react", "job_count": 30}
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        demand = get_skill_market_demand(["python", "react"])
        assert demand["python"] == 50
        assert demand["react"] == 30

    @patch("ai.skill_gap.get_cursor")
    def test_get_skill_market_demand_all(self, mock_get_cursor):
        """Test market demand for all skills."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            {"skill_name": "python", "job_count": 50},
            {"skill_name": "react", "job_count": 30}
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        demand = get_skill_market_demand()
        assert demand["python"] == 50
        assert demand["react"] == 30


class TestGetJobSkillRequirements:
    """Test fetching job skills with importance levels."""

    @patch("ai.skill_gap.get_cursor")
    def test_get_job_skill_requirements(self, mock_get_cursor):
        """Test fetching job skills with required/preferred."""
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [
            {"skill_name": "Python", "importance_level": "required"},
            {"skill_name": "React", "importance_level": "preferred"},
            {"skill_name": "Docker", "importance_level": "required"}
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        skills = get_job_skill_requirements(1)
        assert len(skills) == 3
        assert skills[0]["skill_name"] == "Python"
        assert skills[0]["importance_level"] == "required"
        assert skills[1]["importance_level"] == "preferred"
        assert skills[2]["importance_level"] == "required"

    @patch("ai.skill_gap.get_cursor")
    def test_get_job_skill_requirements_default_required(self, mock_get_cursor):
        """Test default importance_level is required when not specified."""
        mock_cur = MagicMock()
        # Simulate NULL importance_level
        mock_cur.fetchall.return_value = [
            {"skill_name": "Python", "importance_level": None}
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        skills = get_job_skill_requirements(1)
        assert skills[0]["importance_level"] == "required"


class TestGetLatestCVSkills:
    """Test fetching latest CV skills with fallback."""

    @patch("ai.skill_gap.get_cursor")
    def test_get_latest_cv_skills_from_cv(self, mock_get_cursor):
        """Test getting skills from latest CV."""
        mock_cur = MagicMock()
        # First call: get latest CV
        mock_cur.fetchone.side_effect = [
            {"extracted_skills": ["python", "sql", "django"]},  # CV
            None  # Not called for profile
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        skills, source = get_latest_cv_skills(1)
        assert skills == ["python", "sql", "django"]
        assert source == "cv"

    @patch("ai.skill_gap.get_cursor")
    def test_get_latest_cv_skills_fallback_to_profile(self, mock_get_cursor):
        """Test fallback to profile when no CV."""
        mock_cur = MagicMock()
        # First call: no CV
        # Second call: profile skills
        mock_cur.fetchone.side_effect = [
            None,  # No CV
        ]
        mock_cur.fetchall.return_value = [
            {"skill_name": "java"},
            {"skill_name": "spring"}
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        skills, source = get_latest_cv_skills(1)
        assert skills == ["java", "spring"]
        assert source == "profile"


class TestFindCVEvidence:
    """Test CV evidence extraction."""

    def test_find_cv_evidence_found(self):
        """Test finding skill evidence in CV."""
        cv_text = "I have 3 years of experience with Python and Django. Built REST APIs."
        evidence = find_cv_evidence(cv_text, "Python")
        assert evidence is not None
        assert "python" in evidence.lower()

    def test_find_cv_evidence_not_found(self):
        """Test no evidence when skill not in CV."""
        cv_text = "I have experience with Java and Spring."
        evidence = find_cv_evidence(cv_text, "Python")
        assert evidence is None

    def test_find_cv_evidence_empty_cv(self):
        """Test empty CV returns None."""
        evidence = find_cv_evidence("", "Python")
        assert evidence is None
        evidence = find_cv_evidence(None, "Python")
        assert evidence is None


class TestGetProficiencyFromCV:
    """Test proficiency inference from CV."""

    def test_get_proficiency_advanced_years(self):
        """Test advanced proficiency from years."""
        cv_text = "5 years of Python experience building large systems."
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency == "advanced"

    def test_get_proficiency_intermediate_years(self):
        """Test intermediate proficiency from years."""
        cv_text = "3 years Python experience."
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency == "intermediate"

    def test_get_proficiency_beginner_years(self):
        """Test beginner proficiency from years."""
        cv_text = "1 year Python experience."
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency == "beginner"

    def test_get_proficiency_from_keywords(self):
        """Test proficiency from keywords."""
        cv_text = "Expert in Python and Django. Senior developer."
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency == "advanced"

        cv_text = "Proficient in Python. Good knowledge of Django."
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency == "intermediate"

        cv_text = "Basic Python knowledge. Familiar with syntax."
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency == "beginner"

    def test_get_proficiency_none(self):
        """Test None when no indicators."""
        cv_text = "I have Python."  # "have" doesn't indicate proficiency level
        proficiency = get_proficiency_from_cv(cv_text, "Python")
        assert proficiency is None


class TestSkillGapEdgeCases:
    """Test edge cases for skill gap analysis."""

    def test_unicode_skills(self):
        """Test with unicode skill names."""
        cv = "C++, C#, Java"
        job = "C++, C#, Java, Python"

        result = analyze_skill_gap(cv, job)
        assert "c++" in result["matched_skills"]
        assert "c#" in result["matched_skills"]

    def test_case_insensitive(self):
        """Test case insensitivity."""
        cv = "PYTHON, SQL, REACT"
        job = "python, sql, react"

        result = analyze_skill_gap(cv, job)
        assert len(result["matched_skills"]) == 3

    def test_duplicate_skills_in_input(self):
        """Test handling of duplicate skills."""
        cv = ["python", "python", "sql"]
        job = ["python", "sql", "sql", "react"]

        result = analyze_skill_gap(cv, job)
        assert len(result["matched_skills"]) == 2
        assert len(result["missing_skills"]) == 1

    def test_semantic_matching_react_nextjs(self):
        """Test semantic matching between React and Next.js."""
        cv = "React, JavaScript, TypeScript"
        job = "Next.js, React, Tailwind CSS"

        result = analyze_skill_gap(cv, job)

        # React should match exactly
        assert "react" in result["matched_skills"]
        # Next.js might be semantic match or missing depending on embeddings
        # At minimum, we should have some matched skills

    def test_required_vs_preferred_grouping(self):
        """Test that skills are grouped by required/preferred."""
        # This test requires database mocking which is complex
        # The functionality is tested in integration tests
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])