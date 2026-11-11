"""
Learning Resources - Free learning resource recommendations for skills
Integrates with freeCodeCamp, Coursera audit, YouTube, official docs
"""
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LearningResource:
    """Represents a learning resource."""
    title: str
    url: str
    type: str  # "course", "tutorial", "documentation", "video", "project"
    platform: str  # "freeCodeCamp", "Coursera", "YouTube", "Official Docs", "GitHub"
    duration: Optional[str] = None  # e.g., "10 hours", "2 weeks"
    level: Optional[str] = None  # "beginner", "intermediate", "advanced"
    language: str = "en"  # "en", "vi"
    is_free: bool = True
    rating: Optional[float] = None


# Curated resource mappings for common IT skills
RESOURCE_MAPPINGS = {
    # Programming Languages
    "python": [
        LearningResource("Python for Everybody (Coursera)", "https://www.coursera.org/specializations/python", "course", "Coursera", "3 months", "beginner", "en", True, 4.8),
        LearningResource("Python Tutorial (freeCodeCamp)", "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "course", "freeCodeCamp", "300 hours", "beginner", "en", True, 4.7),
        LearningResource("Python Official Tutorial", "https://docs.python.org/3/tutorial/", "documentation", "Official Docs", None, "beginner", "en", True, None),
        LearningResource("Python Programming (Vietnamese)", "https://www.youtube.com/playlist?list=PLaKf_rw704n8K8C1eJ8K8K8K8K8K8K8K8", "video", "YouTube", "20 hours", "beginner", "vi", True, None),
    ],
    "javascript": [
        LearningResource("JavaScript Algorithms (freeCodeCamp)", "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "course", "freeCodeCamp", "300 hours", "beginner", "en", True, 4.8),
        LearningResource("JavaScript.info", "https://javascript.info/", "tutorial", "Documentation", None, "beginner", "en", True, 4.9),
        LearningResource("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "documentation", "MDN", None, "beginner", "en", True, None),
        LearningResource("JavaScript Cơ Bản (Vietnamese)", "https://www.youtube.com/playlist?list=PLaKf_rw704n8K8C1eJ8K8K8K8K8K8K8K8", "video", "YouTube", "15 hours", "beginner", "vi", True, None),
    ],
    "typescript": [
        LearningResource("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html", "documentation", "Official Docs", None, "intermediate", "en", True, None),
        LearningResource("TypeScript Course (freeCodeCamp)", "https://www.freecodecamp.org/news/learn-typescript/", "course", "freeCodeCamp", "10 hours", "intermediate", "en", True, None),
    ],
    "java": [
        LearningResource("Java Programming (Coursera)", "https://www.coursera.org/specializations/java-programming", "course", "Coursera", "5 months", "beginner", "en", True, 4.7),
        LearningResource("Java Tutorial (Oracle)", "https://docs.oracle.com/javase/tutorial/", "documentation", "Official Docs", None, "beginner", "en", True, None),
    ],
    "go": [
        LearningResource("Go Tour", "https://go.dev/tour/welcome/1", "tutorial", "Official Docs", "4 hours", "beginner", "en", True, None),
        LearningResource("Go by Example", "https://gobyexample.com/", "tutorial", "Documentation", None, "beginner", "en", True, None),
    ],
    "rust": [
        LearningResource("The Rust Book", "https://doc.rust-lang.org/book/", "documentation", "Official Docs", "20 hours", "beginner", "en", True, 4.9),
        LearningResource("Rustlings", "https://github.com/rust-lang/rustlings", "project", "GitHub", "10 hours", "beginner", "en", True, None),
    ],
    "c#": [
        LearningResource("C# Fundamentals (Microsoft)", "https://learn.microsoft.com/en-us/training/paths/csharp-fundamentals/", "course", "Microsoft Learn", "12 hours", "beginner", "en", True, None),
    ],
    "php": [
        LearningResource("PHP Manual", "https://www.php.net/manual/en/", "documentation", "Official Docs", None, "beginner", "en", True, None),
        LearningResource("PHP Tutorial (freeCodeCamp)", "https://www.freecodecamp.org/news/php-tutorial/", "course", "freeCodeCamp", "5 hours", "beginner", "en", True, None),
    ],

    # Frontend
    "react": [
        LearningResource("React Official Tutorial", "https://react.dev/learn", "documentation", "Official Docs", "10 hours", "beginner", "en", True, None),
        LearningResource("React Course (freeCodeCamp)", "https://www.freecodecamp.org/learn/front-end-development-libraries/#react", "course", "freeCodeCamp", "20 hours", "beginner", "en", True, 4.8),
        LearningResource("React Vietnamese", "https://reactjs.vn/", "documentation", "Community", None, "beginner", "vi", True, None),
    ],
    "vue.js": [
        LearningResource("Vue.js Guide", "https://vuejs.org/guide/introduction.html", "documentation", "Official Docs", "8 hours", "beginner", "en", True, None),
    ],
    "angular": [
        LearningResource("Angular Tutorial", "https://angular.io/tutorial", "documentation", "Official Docs", "20 hours", "beginner", "en", True, None),
    ],
    "next.js": [
        LearningResource("Next.js Learn", "https://nextjs.org/learn", "documentation", "Official Docs", "10 hours", "intermediate", "en", True, None),
    ],
    "html/css": [
        LearningResource("Responsive Web Design (freeCodeCamp)", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "course", "freeCodeCamp", "300 hours", "beginner", "en", True, 4.8),
        LearningResource("MDN HTML/CSS", "https://developer.mozilla.org/en-US/docs/Learn/HTML", "documentation", "MDN", None, "beginner", "en", True, None),
    ],
    "tailwind css": [
        LearningResource("Tailwind CSS Docs", "https://tailwindcss.com/docs/installation", "documentation", "Official Docs", "4 hours", "beginner", "en", True, None),
    ],

    # Backend
    "node.js": [
        LearningResource("Node.js Guide (MDN)", "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs", "tutorial", "MDN", "10 hours", "beginner", "en", True, None),
        LearningResource("Node.js Official Docs", "https://nodejs.org/en/docs/", "documentation", "Official Docs", None, "beginner", "en", True, None),
    ],
    "express.js": [
        LearningResource("Express.js Guide", "https://expressjs.com/en/guide/routing.html", "documentation", "Official Docs", "6 hours", "intermediate", "en", True, None),
    ],
    "django": [
        LearningResource("Django Tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "documentation", "Official Docs", "10 hours", "beginner", "en", True, None),
        LearningResource("Django for Everybody (Coursera)", "https://www.coursera.org/specializations/django", "course", "Coursera", "4 months", "beginner", "en", True, 4.7),
    ],
    "flask": [
        LearningResource("Flask Tutorial", "https://flask.palletsprojects.com/en/stable/tutorial/", "documentation", "Official Docs", "6 hours", "beginner", "en", True, None),
    ],
    "fastapi": [
        LearningResource("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/", "documentation", "Official Docs", "4 hours", "beginner", "en", True, None),
    ],
    "spring boot": [
        LearningResource("Spring Boot Reference", "https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/", "documentation", "Official Docs", None, "intermediate", "en", True, None),
        LearningResource("Spring Boot Guides", "https://spring.io/guides", "tutorial", "Official Docs", "20 hours", "beginner", "en", True, None),
    ],

    # Databases
    "sql": [
        LearningResource("SQL Tutorial (freeCodeCamp)", "https://www.freecodecamp.org/news/sql-tutorial-full-database-course-for-beginners/", "course", "freeCodeCamp", "4 hours", "beginner", "en", True, 4.8),
        LearningResource("SQL Bolt", "https://sqlbolt.com/", "tutorial", "Interactive", "2 hours", "beginner", "en", True, None),
        LearningResource("PostgreSQL Tutorial", "https://www.postgresqltutorial.com/", "documentation", "Official Docs", None, "beginner", "en", True, None),
    ],
    "postgresql": [
        LearningResource("PostgreSQL Documentation", "https://www.postgresql.org/docs/", "documentation", "Official Docs", None, "intermediate", "en", True, None),
    ],
    "mysql": [
        LearningResource("MySQL Tutorial", "https://www.mysqltutorial.org/", "documentation", "Official Docs", None, "beginner", "en", True, None),
    ],
    "mongodb": [
        LearningResource("MongoDB University", "https://learn.mongodb.com/", "course", "MongoDB", "10 hours", "beginner", "en", True, None),
    ],
    "redis": [
        LearningResource("Redis Documentation", "https://redis.io/docs/", "documentation", "Official Docs", None, "intermediate", "en", True, None),
    ],

    # Cloud & DevOps
    "aws": [
        LearningResource("AWS Skill Builder", "https://skillbuilder.aws/", "course", "AWS", "varies", "beginner", "en", True, None),
        LearningResource("AWS Free Tier Tutorials", "https://aws.amazon.com/free/", "tutorial", "AWS", None, "beginner", "en", True, None),
    ],
    "gcp": [
        LearningResource("Google Cloud Training", "https://cloud.google.com/training", "course", "Google Cloud", "varies", "beginner", "en", True, None),
    ],
    "azure": [
        LearningResource("Microsoft Learn Azure", "https://learn.microsoft.com/en-us/training/azure/", "course", "Microsoft Learn", "varies", "beginner", "en", True, None),
    ],
    "docker": [
        LearningResource("Docker Get Started", "https://docs.docker.com/get-started/", "documentation", "Official Docs", "4 hours", "beginner", "en", True, None),
        LearningResource("Docker for Beginners (freeCodeCamp)", "https://www.freecodecamp.org/news/docker-tutorial-for-beginners/", "course", "freeCodeCamp", "2 hours", "beginner", "en", True, None),
    ],
    "kubernetes": [
        LearningResource("Kubernetes Basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "documentation", "Official Docs", "6 hours", "intermediate", "en", True, None),
        LearningResource("Kubernetes by Example", "https://kubernetesbyexample.com/", "tutorial", "Interactive", "10 hours", "intermediate", "en", True, None),
    ],
    "terraform": [
        LearningResource("Terraform Tutorials", "https://developer.hashicorp.com/terraform/tutorials", "tutorial", "Official Docs", "10 hours", "intermediate", "en", True, None),
    ],
    "ci/cd": [
        LearningResource("GitHub Actions Docs", "https://docs.github.com/en/actions", "documentation", "Official Docs", "6 hours", "intermediate", "en", True, None),
        LearningResource("GitLab CI/CD", "https://docs.gitlab.com/ee/ci/", "documentation", "Official Docs", None, "intermediate", "en", True, None),
    ],
    "jenkins": [
        LearningResource("Jenkins Tutorial", "https://www.jenkins.io/doc/tutorials/", "documentation", "Official Docs", None, "intermediate", "en", True, None),
    ],

    # Data & AI
    "machine learning": [
        LearningResource("ML Crash Course (Google)", "https://developers.google.com/machine-learning/crash-course", "course", "Google", "15 hours", "beginner", "en", True, 4.8),
        LearningResource("Machine Learning (Coursera - Andrew Ng)", "https://www.coursera.org/learn/machine-learning", "course", "Coursera", "11 weeks", "beginner", "en", True, 4.9),
        LearningResource("Fast.ai", "https://course.fast.ai/", "course", "fast.ai", "7 weeks", "intermediate", "en", True, 4.9),
    ],
    "deep learning": [
        LearningResource("Deep Learning Specialization (Coursera)", "https://www.coursera.org/specializations/deep-learning", "course", "Coursera", "4 months", "intermediate", "en", True, 4.9),
    ],
    "tensorflow": [
        LearningResource("TensorFlow Tutorials", "https://www.tensorflow.org/tutorials", "documentation", "Official Docs", "varies", "intermediate", "en", True, None),
    ],
    "pytorch": [
        LearningResource("PyTorch Tutorials", "https://pytorch.org/tutorials/", "documentation", "Official Docs", "varies", "intermediate", "en", True, None),
    ],
    "pandas": [
        LearningResource("Pandas Documentation", "https://pandas.pydata.org/docs/", "documentation", "Official Docs", None, "beginner", "en", True, None),
        LearningResource("Pandas Tutorial (Data School)", "https://www.dataschool.io/", "tutorial", "YouTube", "10 hours", "beginner", "en", True, None),
    ],
    "numpy": [
        LearningResource("NumPy Tutorial", "https://numpy.org/doc/stable/user/quickstart_tutorial.html", "documentation", "Official Docs", "4 hours", "beginner", "en", True, None),
    ],

    # Tools
    "git": [
        LearningResource("Git Handbook (GitHub)", "https://guides.github.com/introduction/git-handbook/", "documentation", "GitHub", "1 hour", "beginner", "en", True, None),
        LearningResource("Pro Git Book", "https://git-scm.com/book/en/v2", "documentation", "Official Docs", "10 hours", "beginner", "en", True, 4.9),
    ],
    "linux": [
        LearningResource("Linux Journey", "https://linuxjourney.com/", "tutorial", "Interactive", "10 hours", "beginner", "en", True, None),
        LearningResource("The Linux Command Line", "https://linuxcommand.org/tlcl.php", "documentation", "Book", "20 hours", "beginner", "en", True, None),
    ],

    # Soft skills / Career
    "system design": [
        LearningResource("System Design Primer", "https://github.com/donnemartin/system-design-primer", "project", "GitHub", "40 hours", "intermediate", "en", True, 4.9),
        LearningResource("Designing Data-Intensive Applications", "https://dataintensiveapplications.com/", "book", "Book", "20 hours", "advanced", "en", False, 4.9),
    ],
    "software architecture": [
        LearningResource("Software Architecture Patterns", "https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/", "book", "O'Reilly", "10 hours", "intermediate", "en", False, None),
    ],
}


# Fallback generic resources
GENERIC_RESOURCES = [
    LearningResource("freeCodeCamp Curriculum", "https://www.freecodecamp.org/learn/", "course", "freeCodeCamp", "3000+ hours", "beginner", "en", True, 4.8),
    LearningResource("Coursera Audit Mode", "https://www.coursera.org/", "course", "Coursera", "varies", "beginner", "en", True, None),
    LearningResource("edX Free Courses", "https://www.edx.org/", "course", "edX", "varies", "beginner", "en", True, None),
    LearningResource("YouTube Programming", "https://www.youtube.com/results?search_query=programming+tutorial", "video", "YouTube", "unlimited", "beginner", "en", True, None),
    LearningResource("GitHub Awesome Lists", "https://github.com/sindresorhus/awesome", "project", "GitHub", "unlimited", "all", "en", True, None),
    LearningResource("Roadmap.sh", "https://roadmap.sh/", "tutorial", "Community", "varies", "all", "en", True, None),
]


class LearningResourceRecommender:
    """Recommends learning resources for skills."""

    def __init__(self):
        self.resource_mappings = RESOURCE_MAPPINGS
        # Normalize keys for matching
        self._normalized_mappings = {
            k.lower().replace(" ", "").replace(".", "").replace("#", "sharp"): v
            for k, v in RESOURCE_MAPPINGS.items()
        }

    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for matching."""
        return skill.lower().replace(" ", "").replace(".", "").replace("#", "sharp").replace("+", "plus")

    def get_resources_for_skill(
        self,
        skill: str,
        max_results: int = 5,
        language: str = "en"
    ) -> List[Dict]:
        """
        Get learning resources for a specific skill.

        Args:
            skill: Skill name
            max_results: Maximum resources to return
            language: Preferred language (en, vi)

        Returns:
            List of resource dictionaries
        """
        normalized = self._normalize_skill(skill)

        # Direct match
        if normalized in self._normalized_mappings:
            resources = self._normalized_mappings[normalized]
        else:
            # Fuzzy match - check if any key is contained in skill or vice versa
            resources = []
            for key, value in self._normalized_mappings.items():
                if key in normalized or normalized in key:
                    resources = value
                    break

            # Fallback to generic
            if not resources:
                resources = GENERIC_RESOURCES

        # Filter by language preference
        filtered = []
        for r in resources:
            if r.language == language or language == "any":
                filtered.append(r)
            elif language == "vi" and r.language == "en":
                # Include English if no Vietnamese available
                filtered.append(r)

        # Convert to dict
        result = []
        for r in filtered[:max_results]:
            result.append({
                "title": r.title,
                "url": r.url,
                "type": r.type,
                "platform": r.platform,
                "duration": r.duration,
                "level": r.level,
                "language": r.language,
                "is_free": r.is_free,
                "rating": r.rating
            })

        return result

    def get_resources_for_skills(
        self,
        skills: List[str],
        max_per_skill: int = 3,
        language: str = "en"
    ) -> Dict[str, List[Dict]]:
        """
        Get resources for multiple skills.

        Args:
            skills: List of skill names
            max_per_skill: Max resources per skill
            language: Preferred language

        Returns:
            Dictionary mapping skill -> list of resources
        """
        result = {}
        for skill in skills:
            result[skill] = self.get_resources_for_skill(
                skill, max_per_skill, language
            )
        return result

    def get_learning_path(
        self,
        missing_skills: List[str],
        target_role: str = "",
        max_per_skill: int = 3
    ) -> Dict:
        """
        Generate a structured learning path for missing skills.

        Args:
            missing_skills: List of skills to learn
            target_role: Target role (for context)
            max_per_skill: Resources per skill

        Returns:
            Dictionary with phases, resources, time estimates
        """
        # Define skill prerequisites (simplified)
        prerequisites = {
            "react": ["javascript", "html/css"],
            "next.js": ["react", "javascript"],
            "vue.js": ["javascript", "html/css"],
            "angular": ["typescript", "html/css"],
            "django": ["python", "sql"],
            "flask": ["python"],
            "fastapi": ["python", "sql"],
            "spring boot": ["java", "sql"],
            "node.js": ["javascript"],
            "express.js": ["node.js", "javascript"],
            "tensorflow": ["python", "machine learning"],
            "pytorch": ["python", "machine learning"],
            "kubernetes": ["docker", "linux"],
            "terraform": ["cloud", "linux"],
            "machine learning": ["python", "statistics"],
            "deep learning": ["machine learning", "python"],
            "data analysis": ["python", "sql"],
        }

        # Sort skills by prerequisites
        ordered_skills = []
        added = set()

        def add_skill(skill):
            if skill in added:
                return
            prereqs = prerequisites.get(skill.lower(), [])
            for p in prereqs:
                if p in [s.lower() for s in missing_skills] and p not in added:
                    add_skill(p)
            ordered_skills.append(skill)
            added.add(skill)

        for skill in missing_skills:
            add_skill(skill)

        # Create phases
        phases = [
            {
                "phase": 1,
                "name": "Cơ bản (Prerequisites)",
                "skills": [s for s in ordered_skills if prerequisites.get(s.lower(), []) == []],
                "duration_weeks": 2
            },
            {
                "phase": 2,
                "name": "Core Skills",
                "skills": [s for s in ordered_skills if prerequisites.get(s.lower(), []) != [] and len(prerequisites.get(s.lower(), [])) <= 1],
                "duration_weeks": 4
            },
            {
                "phase": 3,
                "name": "Advanced / Integration",
                "skills": [s for s in ordered_skills if len(prerequisites.get(s.lower(), [])) > 1],
                "duration_weeks": 4
            }
        ]

        # Remove empty phases
        phases = [p for p in phases if p["skills"]]

        # Add resources to each skill
        for phase in phases:
            for skill in phase["skills"]:
                phase[f"{skill}_resources"] = self.get_resources_for_skill(skill, max_per_skill)

        total_weeks = sum(p["duration_weeks"] for p in phases)

        return {
            "target_role": target_role,
            "total_skills": len(missing_skills),
            "estimated_weeks": total_weeks,
            "phases": phases,
            "all_resources": self.get_resources_for_skills(missing_skills, max_per_skill)
        }


# Singleton instance
_recommender_instance = None


def get_learning_recommender() -> LearningResourceRecommender:
    """Get singleton instance."""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = LearningResourceRecommender()
    return _recommender_instance


def get_resources_for_skill(skill: str, max_results: int = 5, language: str = "en") -> List[Dict]:
    """Convenience function."""
    return get_learning_recommender().get_resources_for_skill(skill, max_results, language)


def get_resources_for_skills(skills: List[str], max_per_skill: int = 3, language: str = "en") -> Dict:
    """Convenience function."""
    return get_learning_recommender().get_resources_for_skills(skills, max_per_skill, language)


def get_learning_path(missing_skills: List[str], target_role: str = "", max_per_skill: int = 3) -> Dict:
    """Convenience function."""
    return get_learning_recommender().get_learning_path(missing_skills, target_role, max_per_skill)


if __name__ == "__main__":
    import json
    recommender = LearningResourceRecommender()

    # Test
    skills = ["React", "TypeScript", "Node.js", "Docker"]
    result = recommender.get_learning_path(skills, "Frontend Developer")
    print(json.dumps(result, indent=2, ensure_ascii=False))