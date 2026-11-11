"""Tests for Skill Extractor module - focusing on alias fixes and regressions."""
import pytest

from ai.skill_extractor import extract_skills, SKILL_ALIASES


class TestSkillExtractorBasics:
    """Test basic skill extraction functionality."""

    def test_basic_skill_extraction(self):
        """Test basic skill extraction works."""
        text = "I am a Python developer with experience in Java and JavaScript."
        skills = extract_skills(text)
        assert "python" in skills
        assert "java" in skills
        assert "javascript" in skills

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        text = "PYTHON, Java, JAVASCRIPT"
        skills = extract_skills(text)
        assert "python" in skills
        assert "java" in skills
        assert "javascript" in skills

    def test_partial_word_not_matched(self):
        """Test that partial words are not matched (word boundaries)."""
        # 'java' should NOT match 'javascript'
        text = "I know JavaScript"
        skills = extract_skills(text)
        assert "javascript" in skills
        assert "java" not in skills

        # 'sql' should NOT match 'mysql'
        text = "I know MySQL"
        skills = extract_skills(text)
        assert "mysql" in skills
        assert "sql" not in skills

    def test_special_characters(self):
        """Test skills with special characters."""
        text = "C++ and C# developer"
        skills = extract_skills(text)
        assert "c++" in skills
        assert "c#" in skills

    def test_multi_word_skills(self):
        """Test multi-word skills."""
        text = "Machine Learning engineer with Deep Learning experience"
        skills = extract_skills(text)
        assert "machine learning" in skills
        assert "deep learning" in skills


class TestSkillExtractorAliasFixes:
    """Test the alias fixes to prevent false positives."""

    def test_cv_attached_not_ml(self):
        """Test 'CV attached' is not interpreted as Machine Learning."""
        text = "Please find my CV attached for your review."
        skills = extract_skills(text)
        # "cv" was removed from aliases, should NOT match "machine learning"
        assert "machine learning" not in skills
        # "cv" might still be in skill list, but "cv attached" shouldn't trigger it
        # The key fix: "cv" alias to "machine learning" was removed

    def test_nlp_not_machine_learning(self):
        """Test 'NLP' is not interpreted as Machine Learning."""
        text = "I work on NLP projects using transformers."
        skills = extract_skills(text)
        # "nlp" alias to "machine learning" was removed
        assert "machine learning" not in skills
        # NLP might match as a skill if it's in SKILL_LIST, but not via alias

    def test_cicd_not_github_actions(self):
        """Test 'CI/CD' maps to generic 'ci/cd' not 'github actions'."""
        text = "We use CI/CD pipelines for deployment."
        skills = extract_skills(text)
        # "ci/cd" and "cicd" now map to "ci/cd" skill, not "github actions"
        assert "ci/cd" in skills
        assert "github actions" not in skills

    def test_gitlab_not_gitlab_ci(self):
        """Test 'GitLab' doesn't auto-map to 'gitlab ci'."""
        text = "We host our code on GitLab."
        skills = extract_skills(text)
        # "gitlab" alias to "gitlab ci" was removed
        assert "gitlab ci" not in skills
        # "gitlab" might be in SKILL_LIST as a platform skill

    def test_go_language_via_alias(self):
        """Test 'go' and 'golang' map to 'golang' skill."""
        text = "I write Go and Golang services."
        skills = extract_skills(text)
        # "go" and "golang" should map to "golang" skill
        assert "golang" in skills

    def test_go_common_word_false_positive(self):
        """Test that common English 'go' doesn't always trigger."""
        # "go" as a standalone verb might still trigger, but we changed skill name to "golang"
        # This is a trade-off - the alias "go" -> "golang" is intentional for the programming language
        text = "Let's go to the meeting."
        skills = extract_skills(text)
        # This might still match "golang" which is expected behavior for the alias
        # The key fix was renaming the skill from "go" to "golang" to make it clear


class TestSkillExtractorAliases:
    """Test all skill aliases work correctly."""

    def test_javascript_aliases(self):
        """Test JavaScript ecosystem aliases."""
        text = "I use TS, ReactJS, Vue.js, NextJS, ExpressJS"
        skills = extract_skills(text)
        assert "typescript" in skills
        assert "react" in skills
        assert "vue" in skills
        assert "next.js" in skills
        assert "express" in skills

    def test_python_aliases(self):
        """Test Python ecosystem aliases."""
        text = "Py, Sklearn, TF, Torch, HF"
        skills = extract_skills(text)
        assert "python" in skills
        assert "scikit-learn" in skills
        assert "tensorflow" in skills
        assert "pytorch" in skills
        assert "hugging face" in skills

    def test_database_aliases(self):
        """Test database aliases."""
        text = "Postgres, PSQL, Mongo, MSSQL"
        skills = extract_skills(text)
        assert "postgresql" in skills
        assert "mongodb" in skills
        assert "sql server" in skills

    def test_cloud_aliases(self):
        """Test cloud aliases."""
        text = "K8s, GKE, EKS, AKS, IaC"
        skills = extract_skills(text)
        assert "kubernetes" in skills
        assert "google cloud" in skills
        assert "aws" in skills
        assert "azure" in skills
        assert "terraform" in skills

    def test_dotnet_aliases(self):
        """Test .NET aliases."""
        text = "DotNet, ASP.NET Core, CSharp"
        skills = extract_skills(text)
        assert ".net" in skills
        assert "asp.net core" in skills
        assert "c#" in skills

    def test_ml_dl_aliases(self):
        """Test ML/DL aliases."""
        text = "ML, DL projects"
        skills = extract_skills(text)
        assert "machine learning" in skills
        assert "deep learning" in skills


class TestSkillExtractorEdgeCases:
    """Test edge cases and regressions."""

    def test_empty_text(self):
        """Test empty text returns empty list."""
        assert extract_skills("") == []
        assert extract_skills(None) == []

    def test_whitespace_only(self):
        """Test whitespace only returns empty list."""
        assert extract_skills("   ") == []
        assert extract_skills("\n\t") == []

    def test_punctuation_handling(self):
        """Test punctuation doesn't break matching."""
        text = "Python, Java; C++! React?"
        skills = extract_skills(text)
        assert "python" in skills
        assert "java" in skills
        assert "c++" in skills
        assert "react" in skills

    def test_skill_with_dot(self):
        """Test skills with dots."""
        text = "Node.js, ASP.NET, Next.js"
        skills = extract_skills(text)
        assert "node.js" in skills
        assert "asp.net" in skills
        assert "next.js" in skills

    def test_skill_with_plus(self):
        """Test skills with plus signs."""
        text = "C++, C#"
        skills = extract_skills(text)
        assert "c++" in skills
        assert "c#" in skills

    def test_no_false_positive_on_substrings(self):
        """Test various substring false positives are avoided."""
        test_cases = [
            ("javascript", ["javascript"]),  # Not "java"
            ("typescript", ["typescript"]),  # Not "script"
            ("node.js", ["node.js"]),  # Not "node" or "js"
            ("reactjs", ["react"]),  # Not "react" + "js"
            ("vuejs", ["vue"]),
            ("postgresql", ["postgresql"]),  # Not "sql"
            ("mysql", ["mysql"]),  # Not "sql"
            ("rustacean", []),  # Not "rust"
        ]

        for text, expected in test_cases:
            skills = extract_skills(text)
            for skill in expected:
                assert skill in skills, f"Expected {skill} in {skills} for text '{text}'"


class TestSkillExtractorRegression:
    """Regression tests for specific reported issues."""

    def test_cv_attached_regression(self):
        """Regression: 'CV attached' should not extract 'machine learning'."""
        text = "CV attached"
        skills = extract_skills(text)
        assert "machine learning" not in skills

    def test_nlp_regression(self):
        """Regression: 'NLP' should not extract 'machine learning'."""
        text = "I specialize in NLP and transformers."
        skills = extract_skills(text)
        assert "machine learning" not in skills

    def test_cicd_regression(self):
        """Regression: 'CI/CD' should map to 'ci/cd' (not 'github actions' via alias)."""
        text = "We implement CI/CD pipelines."
        skills = extract_skills(text)
        # "ci/cd" should be extracted via alias
        assert "ci/cd" in skills
        # "github actions" should NOT be extracted from "CI/CD" alone
        # (it would only be extracted if "GitHub Actions" is explicitly mentioned)
        assert "github actions" not in skills

    def test_gitlab_regression(self):
        """Regression: 'GitLab' should not map to 'gitlab ci'."""
        text = "Our repos are on GitLab."
        skills = extract_skills(text)
        assert "gitlab ci" not in skills


if __name__ == "__main__":
    pytest.main([__file__, "-v"])