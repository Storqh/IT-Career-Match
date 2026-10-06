SKILL_LIST = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "php",
    "html",
    "css",
    "sql",

    "flask",
    "django",
    "fastapi",
    "spring",
    "react",
    "angular",
    "vue",
    "bootstrap",
    "asp.net",

    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",

    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",

    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",

    "linux",
    "networking",
    "cybersecurity",

    "unity",
    "unreal engine"
]
SKILL_ALIASES = {
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node.js": "node.js",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "asp.net core": "asp.net",
    "dotnet": ".net"
}

def extract_skills(text):

    if not text:
        return []

    text = text.lower()

    found_skills = set()

    for skill in SKILL_LIST:
        if skill in text:
            found_skills.add(skill)

    for alias, standard_skill in SKILL_ALIASES.items():
        if alias in text:
            found_skills.add(standard_skill)

    return sorted(found_skills)