import re


# =========================================================
# SKILL TAXONOMY - Curated list of IT skills
# =========================================================
SKILL_LIST = [
    # Programming Languages
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "php",
    "ruby",
    "golang",  # Changed from "go" to avoid false positives with common English word
    "rust",
    "swift",
    "kotlin",
    "scala",
    "r",
    "matlab",
    "sql",
    "bash",
    "powershell",

    # Web Frontend
    "html",
    "css",
    "react",
    "vue",
    "angular",
    "svelte",
    "next.js",
    "nuxt.js",
    "tailwind css",
    "bootstrap",
    "sass",
    "less",
    "webpack",
    "vite",
    "jquery",

    # Web Backend
    "node.js",
    "express",
    "fastify",
    "nestjs",
    "django",
    "flask",
    "fastapi",
    "spring",
    "spring boot",
    "asp.net",
    "asp.net core",
    "laravel",
    "symfony",
    "rails",
    "gin",
    "echo",
    "fiber",

    # Databases
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",
    "redis",
    "elasticsearch",
    "cassandra",
    "dynamodb",
    "mariadb",
    "oracle",
    "sql server",
    "prisma",
    "sequelize",
    "typeorm",
    "sqlalchemy",
    "drizzle orm",

    # Cloud & DevOps
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "docker",
    "kubernetes",
    "k8s",
    "helm",
    "terraform",
    "ansible",
    "jenkins",
    "gitlab ci",
    "github actions",
    "circleci",
    "argocd",
    "prometheus",
    "grafana",
    "elk stack",
    "datadog",
    "new relic",
    "linux",
    "nginx",
    "apache",
    "caddy",

    # Version Control
    "git",
    "github",
    "gitlab",
    "bitbucket",

    # Data & AI/ML
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "plotly",
    "jupyter",
    "hugging face",
    "transformers",
    "langchain",
    "openai",
    "llm",
    "rag",
    "vector database",
    "pinecone",
    "weaviate",
    "chromadb",
    "data analysis",
    "data visualization",
    "tableau",
    "power bi",
    "looker",
    "etl",
    "airflow",
    "dbt",
    "spark",
    "hadoop",
    "kafka",
    "flink",

    # Mobile
    "android",
    "ios",
    "react native",
    "flutter",
    "xamarin",
    "swiftui",
    "jetpack compose",

    # Testing
    "jest",
    "vitest",
    "pytest",
    "junit",
    "testng",
    "cypress",
    "playwright",
    "selenium",
    "postman",
    "rest assured",

    # Architecture & Patterns
    "microservices",
    "rest api",
    "graphql",
    "grpc",
    "message queue",
    "rabbitmq",
    "kafka",
    "nats",
    "event driven",
    "domain driven design",
    "clean architecture",
    "hexagonal architecture",
    "cqrs",
    "event sourcing",

    # Security
    "oauth",
    "oauth2",
    "openid connect",
    "jwt",
    "saml",
    "penetration testing",
    "vulnerability assessment",
    "owasp",
    "security audit",

    # Other Tools
    "unity",
    "unreal engine",
    "godot",
    "blender",
    "figma",
    "sketch",
    "adobe xd",
    "jira",
    "confluence",
    "notion",
    "agile",
    "scrum",
    "kanban",
]

# =========================================================
# SKILL ALIASES - Map common variations to standard names
# Only include aliases that don't cause false positives
# =========================================================
SKILL_ALIASES = {
    # JavaScript ecosystem - safe aliases
    "ts": "typescript",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "nextjs": "next.js",
    "nuxtjs": "nuxt.js",
    "expressjs": "express",

    # Python ecosystem
    "py": "python",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "torch": "pytorch",
    "hf": "hugging face",

    # Go language
    "go": "golang",
    "golang": "golang",

    # Databases
    "postgres": "postgresql",
    "psql": "postgresql",
    "mongo": "mongodb",
    "ms sql": "sql server",
    "mssql": "sql server",

    # Cloud
    "k8s": "kubernetes",
    "gke": "google cloud",
    "eks": "aws",
    "aks": "azure",
    "iac": "terraform",

    # CI/CD - Map to generic "ci/cd" skill, not specific tool
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    # "gitlab" removed - too ambiguous (could mean GitLab the platform, not GitLab CI specifically)

    # .NET
    "dotnet": ".net",
    "aspnet": "asp.net",
    "aspnetcore": "asp.net core",
    "csharp": "c#",

    # Other common abbreviations
    "ml": "machine learning",
    "dl": "deep learning",
    # "nlp" removed - too ambiguous (could be "Natural Language Processing" as a field, not "machine learning" skill)
    # "cv" removed - too ambiguous (could mean "computer vision" or "curriculum vitae")
}


def _build_skill_pattern(skill: str) -> re.Pattern:
    """
    Build a regex pattern that matches the skill as a whole word/token.
    Handles special characters: +, #, ., spaces
    """
    # For skills with special separators, we need to match them as a unit
    if any(c in skill for c in "+#. "):
        # Multi-part skill (e.g., "c++", "c#", "node.js", "asp.net", "machine learning")
        # Split by word separators but keep the separators as part of the match
        parts = re.split(r"([\s.+#]+)", skill)
        parts = [p for p in parts if p]
        pattern_parts = []
        for part in parts:
            if re.match(r"[\s.+#]+", part):
                # Separator - match literally
                pattern_parts.append(re.escape(part))
            else:
                # Word part - use word boundary
                pattern_parts.append(r"\b" + re.escape(part) + r"\b")
        full_pattern = "".join(pattern_parts)
    else:
        # Simple skill - use word boundaries
        full_pattern = r"\b" + re.escape(skill) + r"\b"

    return re.compile(full_pattern, re.IGNORECASE)


# Pre-compile all patterns
_COMPILED_SKILL_PATTERNS = {skill: _build_skill_pattern(skill) for skill in SKILL_LIST}
_COMPILED_ALIAS_PATTERNS = {
    alias: (_build_skill_pattern(alias), std)
    for alias, std in SKILL_ALIASES.items()
}


def extract_skills(text):
    """
    Extract skills from text using word-boundary regex matching.

    Fixes the substring matching bug where 'java' would match 'javascript',
    'c' would match 'c++', 'sql' would match 'mysql', etc.

    Args:
        text: Input text (CV, job description, etc.)

    Returns:
        Sorted list of unique matched skill names (standardized)
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = set()

    # Check standard skills
    for skill, pattern in _COMPILED_SKILL_PATTERNS.items():
        if pattern.search(text_lower):
            found_skills.add(skill)

    # Check aliases
    for alias, (pattern, standard_skill) in _COMPILED_ALIAS_PATTERNS.items():
        if pattern.search(text_lower):
            found_skills.add(standard_skill)

    return sorted(found_skills)


if __name__ == "__main__":
    # Quick test
    test_text = """
    I am a Java developer with experience in JavaScript, TypeScript, and Node.js.
    I know Python, C++, C#, and Go. Also familiar with React, Vue, and Angular.
    Database skills: MySQL, PostgreSQL, MongoDB, Redis.
    Cloud: AWS, Docker, Kubernetes. CI/CD: GitHub Actions, GitLab CI.
    """

    skills = extract_skills(test_text)
    print("Extracted skills:")
    for s in skills:
        print(f"  - {s}")

    # Test edge cases
    print("\n--- Edge case tests ---")
    edge_cases = [
        "javascript",      # should NOT match 'java'
        "java developer",  # should match 'java'
        "c++ programmer",  # should match 'c++' only
        "c# developer",    # should match 'c#' only
        "mysql expert",    # should match 'mysql' but NOT 'sql' separately
        "sql expert",      # should match 'sql'
        "node.js backend", # should match 'node.js' only
        "reactjs fan",     # should match 'react' via alias
        "asp.net core",    # should match 'asp.net core'
        "machine learning engineer",  # should match 'machine learning'
        "go developer",    # should match 'go'
        "rustacean",       # should NOT match 'rust' (word boundary)
        "typescript dev",  # should match 'typescript'
        "postgres user",   # should match 'postgresql' via alias
        "k8s admin",       # should match 'kubernetes' via alias
        "ci/cd pipeline",  # should match 'github actions' via alias
    ]

    for case in edge_cases:
        result = extract_skills(case)
        print(f"  '{case}' -> {result}")