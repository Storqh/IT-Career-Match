"""Test for recommendation clearing fix - verifies old recommendations are removed when new CV uploaded."""
import pytest
from unittest.mock import patch, MagicMock


class TestRecommendationClearing:
    """Test that recommendations are properly cleared when new CV uploaded."""

    @patch("database.database.get_cursor")
    @patch("database.database.create_recommendation")
    def test_save_recommendations_clears_old_first(self, mock_create_rec, mock_get_cursor):
        """Test that save_recommendations clears old recommendations before saving new ones."""
        from ai.recommender import save_recommendations

        mock_cur = MagicMock()
        mock_cur.rowcount = 5
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        # Sample new recommendations
        new_recs = [
            {"job_id": 101, "match_score": 90, "skill_match": 80, "career_match": True, "explanation": {"summary": "Good match"}},
            {"job_id": 102, "match_score": 85, "skill_match": 75, "career_match": False, "explanation": {"summary": "Decent match"}},
        ]

        save_recommendations(1, new_recs)

        # Verify clear was called first (DELETE query)
        mock_cur.execute.assert_any_call("DELETE FROM recommendations WHERE user_id = %s", (1,))

        # Verify create_recommendation called for each new recommendation
        assert mock_create_rec.call_count == 2
        mock_create_rec.assert_any_call(1, 101, 90, 80, True, "Good match")
        mock_create_rec.assert_any_call(1, 102, 85, 75, False, "Decent match")

    @patch("database.database.get_cursor")
    @patch("database.database.create_recommendation")
    def test_save_recommendations_empty_list(self, mock_create_rec, mock_get_cursor):
        """Test that clear is called even when no new recommendations."""
        from ai.recommender import save_recommendations

        mock_cur = MagicMock()
        mock_cur.rowcount = 2
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        save_recommendations(1, [])

        # Clear should still be called
        mock_cur.execute.assert_called_once_with("DELETE FROM recommendations WHERE user_id = %s", (1,))
        # create_recommendation should not be called
        mock_create_rec.assert_not_called()


class TestRecommendationIntegration:
    """Integration-style tests for recommendation flow."""

    @patch("database.database.get_cursor")
    @patch("database.database.create_recommendation")
    @patch("ai.recommender.get_all_active_jobs_with_data")
    @patch("ai.recommender.get_user_latest_cv_text")
    @patch("ai.recommender.get_user_skills")
    @patch("ai.recommender.get_user_salary_preferences")
    @patch("ai.recommender.get_ranking_engine")
    @patch("ai.recommender.vectorize_cv")
    @patch("ai.recommender.predict_career")
    @patch("ai.recommender.predict_career_top_k")
    @patch("ai.recommender.get_skill_matcher")
    @patch("ai.recommender.analyze_skill_gap")
    @patch("ai.recommender.generate_explanation")
    def test_recommend_jobs_for_user_clears_old(
        self,
        mock_explanation,
        mock_analyze_gap,
        mock_skill_matcher,
        mock_predict_top_k,
        mock_predict_career,
        mock_vectorize_cv,
        mock_get_ranking_engine,
        mock_get_salary_prefs,
        mock_get_user_skills,
        mock_get_cv_text,
        mock_get_jobs,
        mock_create_rec,
        mock_get_cursor
    ):
        """Test that recommend_jobs_for_user clears old recommendations."""
        from ai.recommender import recommend_jobs_for_user

        mock_cur = MagicMock()
        mock_cur.rowcount = 5
        mock_get_cursor.return_value.__enter__.return_value = mock_cur

        mock_get_cv_text.return_value = "Python developer with Django"
        mock_get_user_skills.return_value = ["python", "django", "postgresql"]
        mock_get_salary_prefs.return_value = (None, None)

        mock_jobs = [
            {"job_id": 1, "title": "Python Dev", "company": "A", "category": "backend", "skills": ["python", "django"], "_vector": None},
            {"job_id": 2, "title": "Java Dev", "company": "B", "category": "backend", "skills": ["java", "spring"], "_vector": None},
        ]
        mock_get_jobs.return_value = mock_jobs

        mock_ranking_engine = MagicMock()
        mock_ranking_engine.rank_jobs.return_value = [
            {"job_id": 1, "match_score": 90, "ranking_signals": {"tfidf_cosine": 0.8}, "category": "backend"},
        ]
        mock_get_ranking_engine.return_value = mock_ranking_engine

        mock_vectorize_cv.return_value = MagicMock()
        mock_predict_career.return_value = "backend"
        mock_predict_top_k.return_value = []

        mock_matcher = MagicMock()
        mock_matcher.match_skills.return_value = {"matched_skills": ["python"], "semantic_matched": []}
        mock_skill_matcher.return_value = mock_matcher

        mock_analyze_gap.return_value = {
            "match_ratio": 0.5,
            "matched_skills": ["python"],
            "missing_skills": ["kubernetes"],
            "missing_skills_by_priority": [],
            "extra_skills": [],
            "skill_details": [],
            "required_skills": ["python"],
            "preferred_skills": ["kubernetes"],
            "market_demand": {},
            "priority_scores": {},
            "resources": {},
            "learning_path": {},
        }

        mock_explanation.return_value = {"summary": "Good match"}

        # Call the function
        results = recommend_jobs_for_user(1, top_k=5)

        # Verify clear was called (DELETE query)
        mock_cur.execute.assert_any_call("DELETE FROM recommendations WHERE user_id = %s", (1,))

        # Verify new recommendation was saved
        mock_create_rec.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])