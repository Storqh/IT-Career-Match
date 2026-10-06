import pandas as pd


df = pd.read_csv("data/career_dataset.csv")


def map_career_category(job_title, skills):

    title = str(job_title).lower()
    skills = str(skills).lower()

    text = title + " " + skills

    # 1. AI / MACHINE LEARNING
    if any(k in text for k in [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "natural language processing",
        "nlp",
        "tensorflow",
        "pytorch",
        "ai engineer",
        "ai researcher",
        "ai software"
    ]):
        return "AI / Machine Learning"

    # 2. DATA
    elif any(k in text for k in [
        "data scientist",
        "data analyst",
        "data engineer",
        "data analysis",
        "data architect",
        "data model",
        "data warehouse",
        "data visualization",
        "big data",
        "business intelligence",
        "power bi",
        "statistical modeling",
        "database"
    ]):
        return "Data"

    # 3. CYBERSECURITY
    elif any(k in text for k in [
        "cybersecurity",
        "cyber security",
        "application security",
        "information security",
        "penetration",
        "ethical hacker",
        "digital forensics",
        "incident response",
        "identity and access",
        "container security",
        "security engineer"
    ]):
        return "Cybersecurity"

    # 4. DEVOPS / CLOUD
    elif any(k in text for k in [
        "devops",
        "devsecops",
        "ci/cd",
        "build automation",
        "deployment automation",
        "cloud computing",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "ansible",
        "terraform",
        "jenkins",
        "gitlab",
        "github",
        "bitbucket",
        "bamboo",
        "grafana",
        "datadog",
        "service mesh",
        "openshift",
        "openstack",
        "puppet",
        "splunk",
        "site reliability"
    ]):
        return "DevOps / Cloud"

    # 5. MOBILE
    elif any(k in text for k in [
        "android",
        "ios developer",
        "mobile developer",
        "mobile app",
        "flutter",
        "react native"
    ]):
        return "Mobile Development"

    # 6. GAME
    elif any(k in text for k in [
        "game developer",
        "game programmer",
        "game development",
        "unity",
        "unreal engine"
    ]):
        return "Game Development"

    # 7. FULL STACK
    elif any(k in text for k in [
        "full stack",
        "fullstack",
        "full-stack"
    ]):
        return "Full Stack Development"

    # 8. FRONTEND / WEB
    elif any(k in text for k in [
        "frontend",
        "front end",
        "front-end",
        "html",
        "css",
        "javascript",
        "react",
        "angular",
        "vue.js"
    ]):
        return "Frontend Development"

    # 9. BACKEND / SOFTWARE DEVELOPMENT
    elif any(k in text for k in [
        "backend",
        "back end",
        "back-end",
        "java developer",
        "python developer",
        "php development",
        ".net development",
        "c# developer",
        "oracle developer",
        "api development",
        "software development",
        "application development",
        "programming languages",
        "software architecture",
        "firmware development"
    ]):
        return "Backend Development"

    # 10. NETWORK / SYSTEM
    elif any(k in text for k in [
        "networking",
        "network engineer",
        "system administration",
        "systems administration",
        "system engineering",
        "linux administration",
        "unix administration",
        "windows server",
        "technical support",
        "hardware",
        "infrastructure management",
        "embedded systems",
        "troubleshooting"
    ]):
        return "Network / System"

    return "Other IT"

df["Career Category"] = df.apply(
    lambda row: map_career_category(
        row["Job Title"],
        row["Skills"]
    ),
    axis=1
)

print("===== PHÂN BỐ CAREER CATEGORY =====")

print(
    df["Career Category"].value_counts()
)
small_categories = [
    "Frontend Development",
    "Mobile Development",
    "Full Stack Development",
    "Game Development"
]

print("\n===== KIỂM TRA CÁC CLASS NHỎ =====")

for category in small_categories:
    print(f"\n--- {category} ---")

    jobs = df[
        df["Career Category"] == category
    ][["Job Title", "Skills"]]

    for _, row in jobs.iterrows():
        print("JOB:", row["Job Title"])
        print("SKILLS:", row["Skills"])
        print()

category_counts = df["Career Category"].value_counts()

valid_categories = category_counts[
    category_counts >= 10
].index

ml_df = df[
    df["Career Category"].isin(valid_categories)
].copy()

print("\n===== DATASET DÙNG ĐỂ TRAIN ML =====")

print("Số mẫu:", len(ml_df))

print("\nPhân bố class:")
print(ml_df["Career Category"].value_counts())
ml_df.to_csv(
    "data/career_ml_dataset.csv",
    index=False
)

print("\nĐã lưu: data/career_ml_dataset.csv")