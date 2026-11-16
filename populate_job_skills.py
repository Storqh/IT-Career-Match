#!/usr/bin/env python3
"""
Populate job_skills table for jobs that have 0 skills.
Extracts skills from job descriptions and inserts into database.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from ai.skill_extractor import extract_skills
from database.connection_pool import get_cursor

# Category-based skill mappings for better extraction
CATEGORY_SKILLS = {
    "AI / Machine Learning": [
        "Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning",
        "scikit-learn", "Pandas", "NumPy", "Computer Vision", "NLP",
        "Transformers", "Hugging Face", "Keras", "OpenCV", "MLOps",
        "Docker", "Kubernetes", "MLflow", "AWS SageMaker", "GCP Vertex AI"
    ],
    "Data": [
        "SQL", "Python", "Pandas", "NumPy", "Tableau", "Power BI", "Looker",
        "Data Visualization", "Data Analysis", "ETL", "Airflow", "dbt",
        "PostgreSQL", "MySQL", "BigQuery", "Snowflake", "Spark", "Hadoop",
        "Statistics", "A/B Testing", "Regression", "Time Series"
    ],
    "Backend Development": [
        "Python", "Java", "Go", "FastAPI", "Django", "Flask", "Spring Boot",
        "Gin", "Echo", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Docker", "Kubernetes", "Microservices", "gRPC", "GraphQL",
        "RabbitMQ", "Kafka", "CI/CD", "GitLab CI", "GitHub Actions",
        "AWS", "GCP", "Terraform", "System Design"
    ],
    "Frontend Development": [
        "JavaScript", "TypeScript", "React", "Next.js", "Vue", "Nuxt",
        "HTML", "CSS", "Tailwind CSS", "Sass", "Redux", "Zustand",
        "React Query", "TanStack Query", "Vite", "Webpack", "Jest",
        "Cypress", "Playwright", "Storybook", "CSS Modules", "Material UI",
        "Ant Design", "Shadcn/UI", "Vercel", "Netlify"
    ],
    "Full Stack Development": [
        "JavaScript", "TypeScript", "React", "Next.js", "Node.js",
        "Python", "FastAPI", "Django", "PostgreSQL", "MongoDB",
        "Docker", "Kubernetes", "AWS", "CI/CD", "GitHub Actions",
        "GraphQL", "REST API", "WebSocket", "Prisma", "TypeORM"
    ],
    "DevOps / Cloud": [
        "AWS", "GCP", "Azure", "Kubernetes", "Docker", "Terraform",
        "Helm", "ArgoCD", "Flux", "GitOps", "Prometheus", "Grafana",
        "Loki", "Tempo", "ELK Stack", "CI/CD", "GitLab CI", "GitHub Actions",
        "Jenkins", "Linux", "Bash", "Python", "Go", "Networking",
        "Istio", "Cilium", "Vault", "Cert-Manager", "External-DNS"
    ],
    "Cybersecurity": [
        "Network Security", "SIEM", "SOC", "Incident Response",
        "Vulnerability Assessment", "Penetration Testing", "OWASP",
        "Burp Suite", "Nmap", "Wireshark", "Python", "Bash",
        "Linux", "Windows Security", "Active Directory", "IAM",
        "Zero Trust", "Compliance", "ISO 27001", "SOC 2"
    ],
    "Network / System": [
        "Linux", "Windows Server", "Networking", "TCP/IP", "DNS", "DHCP",
        "VPN", "Firewall", "Cisco", "Juniper", "BGP", "OSPF",
        "Ansible", "Terraform", "Python", "Bash", "Monitoring",
        "Zabbix", "Prometheus", "Grafana", "Virtualization", "VMware"
    ],
    "Software Testing / QA": [
        "Selenium", "Cypress", "Playwright", "pytest", "JUnit",
        "TestNG", "Postman", "JMeter", "Load Testing", "API Testing",
        "Automation Testing", "Test Planning", "Bug Tracking",
        "JIRA", "TestRail", "CI/CD", "GitHub Actions", "GitLab CI",
        "Docker", "Python", "Java", "JavaScript"
    ],
    "Mobile Development": [
        "Flutter", "Dart", "React Native", "Swift", "Kotlin",
        "iOS", "Android", "Xcode", "Android Studio", "Firebase",
        "REST API", "GraphQL", "SQLite", "Realm", "CI/CD",
        "Fastlane", "TestFlight", "Play Console", "App Store"
    ],
    "Game Development": [
        "Unity", "C#", "Unreal Engine", "C++", "Game Design",
        "3D Modeling", "Blender", "Shader", "Physics Engine",
        "Multiplayer", "Photon", "Mirror", "Git", "CI/CD",
        "Visual Studio", "Rider", "Profiling", "Optimization"
    ],
}


def get_category_skills(category: str):
    """Get relevant skills for a job category."""
    return CATEGORY_SKILLS.get(category, [])


def main():
    print("=" * 60)
    print("Populating job_skills for jobs with 0 skills")
    print("=" * 60)

    with get_cursor() as cur:
        # Get jobs with 0 skills
        cur.execute("""
            SELECT j.job_id, j.title, j.category, j.description
            FROM jobs j
            LEFT JOIN job_skills js ON j.job_id = js.job_id
            WHERE j.status = 'active'
            GROUP BY j.job_id, j.title, j.category, j.description
            HAVING COUNT(js.skill_id) = 0
            ORDER BY j.job_id
        """)
        jobs = cur.fetchall()

    print(f"Found {len(jobs)} jobs with 0 skills")

    total_added = 0
    for job in jobs:
        job_id = job["job_id"]
        title = job["title"]
        category = job["category"]
        description = job["description"] or ""

        # Extract skills from description + category defaults
        extracted = extract_skills(description)
        category_skills = get_category_skills(category)

        # Combine and deduplicate
        all_skills = list(set(extracted + category_skills))
        # Limit to top 10-15 most relevant
        all_skills = all_skills[:15]

        print(f"\n  Job {job_id}: {title} ({category})")
        print(f"    Extracted: {extracted[:5]}...")
        print(f"    Category defaults: {category_skills[:5]}...")
        print(f"    Final skills ({len(all_skills)}): {', '.join(all_skills)}")

        # Insert into job_skills
        with get_cursor(commit=True) as cur:
            for skill_name in all_skills:
                # Get or create skill
                cur.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,))
                skill_row = cur.fetchone()
                if not skill_row:
                    cur.execute(
                        "INSERT INTO skills (skill_name) VALUES (%s) RETURNING skill_id",
                        (skill_name,)
                    )
                    skill_id = cur.fetchone()["skill_id"]
                else:
                    skill_id = skill_row["skill_id"]

                # Insert job_skill
                cur.execute("""
                    INSERT INTO job_skills (job_id, skill_id, importance_level)
                    VALUES (%s, %s, 'required')
                    ON CONFLICT (job_id, skill_id) DO NOTHING
                """, (job_id, skill_id))
                total_added += 1

    print(f"\n{'=' * 60}")
    print(f"[OK] Added {total_added} job_skill entries for {len(jobs)} jobs")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()