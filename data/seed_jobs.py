import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "database/it_career_match.db"
SOURCE = "IT Career Match Demo"

# =========================================================
# CONFIG
# =========================================================

JOB_CONFIG = {
    "AI / Machine Learning": {
        "count": 6,
        "titles": [
            "AI Engineer",
            "Machine Learning Engineer",
            "Junior AI Engineer",
            "Computer Vision Engineer",
            "NLP Engineer",
            "Machine Learning Intern"
        ],
        "skills": [
            "Python", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "SQL", "Git"
        ],
        "tasks": [
            "Xây dựng và huấn luyện các mô hình Machine Learning.",
            "Tiền xử lý và phân tích dữ liệu phục vụ huấn luyện mô hình.",
            "Đánh giá và cải thiện độ chính xác của mô hình.",
            "Tích hợp mô hình AI vào ứng dụng thực tế.",
            "Phối hợp với Backend và Data team để triển khai mô hình."
        ]
    },

    "Data": {
        "count": 6,
        "titles": [
            "Data Analyst",
            "Junior Data Analyst",
            "Data Engineer",
            "BI Developer",
            "Data Science Intern",
            "Junior Data Scientist"
        ],
        "skills": [
            "Python", "SQL", "Pandas",
            "NumPy", "Excel", "Power BI", "Git"
        ],
        "tasks": [
            "Thu thập và làm sạch dữ liệu.",
            "Phân tích dữ liệu phục vụ hoạt động kinh doanh.",
            "Xây dựng báo cáo và dashboard.",
            "Viết truy vấn SQL để khai thác dữ liệu.",
            "Trình bày insight từ dữ liệu cho các bộ phận liên quan."
        ]
    },

    "Backend Development": {
        "count": 8,
        "titles": [
            "Backend Developer",
            "Python Backend Developer",
            "Java Backend Developer",
            "Junior Backend Engineer",
            "Flask Developer",
            "Spring Boot Developer",
            "Backend Developer Intern",
            "API Developer"
        ],
        "skills": [
            "Python", "Java", "Flask",
            "Spring", "SQL", "Git", "Docker"
        ],
        "tasks": [
            "Phát triển REST API cho hệ thống.",
            "Thiết kế và làm việc với cơ sở dữ liệu.",
            "Xử lý business logic phía server.",
            "Fix bug và tối ưu hiệu năng backend.",
            "Phối hợp với Frontend Developer để tích hợp API."
        ]
    },

    "Frontend Development": {
        "count": 6,
        "titles": [
            "Frontend Developer",
            "React Developer",
            "Junior Frontend Developer",
            "Web Developer",
            "Frontend Intern",
            "JavaScript Developer"
        ],
        "skills": [
            "HTML", "CSS", "JavaScript",
            "React", "Bootstrap", "Git"
        ],
        "tasks": [
            "Xây dựng giao diện website responsive.",
            "Phát triển các component giao diện.",
            "Tích hợp REST API từ backend.",
            "Tối ưu trải nghiệm người dùng.",
            "Sửa lỗi giao diện trên nhiều thiết bị."
        ]
    },

    "Full Stack Development": {
        "count": 5,
        "titles": [
            "Full Stack Developer",
            "Junior Full Stack Developer",
            "Full Stack Web Developer",
            "Full Stack Intern",
            "Web Application Developer"
        ],
        "skills": [
            "HTML", "CSS", "JavaScript",
            "React", "Python", "SQL", "Git"
        ],
        "tasks": [
            "Phát triển cả frontend và backend của ứng dụng.",
            "Xây dựng REST API.",
            "Thiết kế giao diện responsive.",
            "Làm việc với database.",
            "Triển khai và bảo trì ứng dụng web."
        ]
    },

    "DevOps / Cloud": {
        "count": 6,
        "titles": [
            "DevOps Engineer",
            "Cloud Engineer",
            "Junior DevOps Engineer",
            "Cloud Operations Engineer",
            "DevOps Intern",
            "Infrastructure Engineer"
        ],
        "skills": [
            "Linux", "Docker", "Kubernetes",
            "AWS", "Azure", "Git"
        ],
        "tasks": [
            "Xây dựng và duy trì CI/CD pipeline.",
            "Quản lý container và hệ thống deployment.",
            "Theo dõi tình trạng hoạt động của server.",
            "Hỗ trợ triển khai ứng dụng lên cloud.",
            "Tự động hóa các tác vụ vận hành hệ thống."
        ]
    },

    "Cybersecurity": {
        "count": 5,
        "titles": [
            "Cybersecurity Analyst",
            "SOC Analyst",
            "Security Engineer",
            "Security Intern",
            "Junior Security Analyst"
        ],
        "skills": [
            "Linux", "Cybersecurity", "Networking",
            "Python", "Git"
        ],
        "tasks": [
            "Theo dõi và phân tích các sự kiện bảo mật.",
            "Phát hiện các dấu hiệu tấn công hệ thống.",
            "Kiểm tra cấu hình và lỗ hổng bảo mật.",
            "Hỗ trợ xử lý sự cố an toàn thông tin.",
            "Viết báo cáo về các vấn đề bảo mật."
        ]
    },

    "Network / System": {
        "count": 5,
        "titles": [
            "Network Engineer",
            "System Administrator",
            "IT Infrastructure Engineer",
            "Network Administrator",
            "IT Support Engineer"
        ],
        "skills": [
            "Networking", "Linux", "Windows",
            "Cisco", "SQL", "Git"
        ],
        "tasks": [
            "Quản trị hệ thống mạng nội bộ.",
            "Cấu hình và kiểm tra thiết bị mạng.",
            "Theo dõi server và dịch vụ hệ thống.",
            "Xử lý các sự cố kết nối.",
            "Hỗ trợ người dùng về các vấn đề IT."
        ]
    },

    "Software Testing / QA": {
        "count": 5,
        "titles": [
            "Software Tester",
            "QA Engineer",
            "Manual Tester",
            "QA Intern",
            "Junior Tester"
        ],
        "skills": [
            "Testing", "SQL", "Git",
            "Python", "JavaScript"
        ],
        "tasks": [
            "Phân tích yêu cầu phần mềm.",
            "Thiết kế và thực hiện test case.",
            "Ghi nhận và theo dõi bug.",
            "Thực hiện regression testing.",
            "Phối hợp với Developer để đảm bảo chất lượng sản phẩm."
        ]
    },

    "Mobile Development": {
        "count": 4,
        "titles": [
            "Mobile Developer",
            "Android Developer",
            "Flutter Developer",
            "Mobile Developer Intern"
        ],
        "skills": [
            "Java", "Flutter", "Dart",
            "Git", "SQL"
        ],
        "tasks": [
            "Phát triển ứng dụng trên thiết bị di động.",
            "Tích hợp API vào ứng dụng.",
            "Tối ưu giao diện trên nhiều kích thước màn hình.",
            "Fix bug và cải thiện hiệu năng ứng dụng.",
            "Đưa ra các cải tiến về trải nghiệm người dùng."
        ]
    },

    "Game Development": {
        "count": 4,
        "titles": [
            "Unity Game Developer",
            "Game Developer",
            "Junior Unity Developer",
            "Game Developer Intern"
        ],
        "skills": [
            "C#", "C++", "Unity",
            "Unreal Engine", "Git"
        ],
        "tasks": [
            "Phát triển gameplay và các tính năng trong game.",
            "Xử lý chuyển động và tương tác của nhân vật.",
            "Tích hợp UI và game assets.",
            "Fix bug và tối ưu hiệu năng game.",
            "Phối hợp với Game Designer và Artist."
        ]
    }
}

COMPANIES = [
    "TechNova Solutions",
    "NextGen Software",
    "Digital Future Lab",
    "CloudCore Technology",
    "DataVision Solutions",
    "CyberShield Technology",
    "BlueOcean Software",
    "SmartTech Vietnam",
    "Innovatech Labs",
    "FutureSoft"
]

LOCATIONS = [
    "TP. Hồ Chí Minh",
    "Hà Nội",
    "Đà Nẵng",
    "Remote"
]

JOB_TYPES = [
    "Full-time",
    "Full-time",
    "Full-time",
    "Internship"
]

LEVELS = [
    "Intern",
    "Fresher",
    "Junior"
]

EXPERIENCES = [
    "Không yêu cầu kinh nghiệm",
    "Dưới 1 năm",
    "1 năm",
    "1 - 2 năm"
]


# =========================================================
# GENERATE JOB
# =========================================================

def create_job(title, category, config, index):

    random.seed(f"{category}-{title}-{index}")

    company = random.choice(COMPANIES)
    location = random.choice(LOCATIONS)

    # Intern có mức lương thấp hơn
    is_intern = "Intern" in title

    if is_intern:
        salary_min = random.choice([3, 4, 5]) * 1_000_000
        salary_max = salary_min + random.choice([2, 3, 4]) * 1_000_000
        job_type = "Internship"
        level = "Intern"
        experience = "Không yêu cầu kinh nghiệm"
    else:
        salary_min = random.choice([8, 10, 12, 15, 18]) * 1_000_000
        salary_max = salary_min + random.choice([4, 5, 6, 8]) * 1_000_000
        job_type = random.choice(JOB_TYPES)
        level = random.choice(LEVELS[1:])
        experience = random.choice(EXPERIENCES)

    salary_text = (
        f"{salary_min // 1_000_000} - "
        f"{salary_max // 1_000_000} triệu"
    )

    # Lấy một nhóm skill khác nhau cho từng job
    number_of_skills = min(
        len(config["skills"]),
        random.randint(4, 6)
    )

    selected_skills = random.sample(
        config["skills"],
        number_of_skills
    )

    skills = ", ".join(selected_skills)

    description = "\n".join(
        f"- {task}"
        for task in config["tasks"]
    )

    requirements = "\n".join([
        f"- Có kiến thức về {skill}."
        for skill in selected_skills
    ])

    requirements += (
        "\n- Có khả năng làm việc nhóm."
        "\n- Chủ động học hỏi công nghệ mới."
        "\n- Có khả năng đọc tài liệu kỹ thuật tiếng Anh."
    )

    benefits = "\n".join([
        "- Được hướng dẫn và đào tạo trong quá trình làm việc.",
        "- Môi trường làm việc trẻ và năng động.",
        "- Được tham gia các dự án thực tế.",
        "- Có cơ hội phát triển chuyên môn.",
        "- Được đánh giá năng lực định kỳ."
    ])

    deadline = (
        datetime.now()
        + timedelta(days=random.randint(30, 90))
    ).strftime("%Y-%m-%d")

    return (
        title,
        description,
        company,
        location,
        job_type,
        category,
        requirements,
        benefits,
        skills,
        salary_min,
        salary_max,
        salary_text,
        experience,
        level,
        deadline,
        SOURCE,
        None,
        "active"
    )


# =========================================================
# DATABASE
# =========================================================

def seed_jobs():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Chỉ xóa dữ liệu demo do script này tạo.
    # Không đụng đến 10 job cũ.
    cursor.execute(
        "DELETE FROM jobs WHERE source = ?",
        (SOURCE,)
    )

    inserted = 0

    sql = """
    INSERT INTO jobs (
        title,
        description,
        company,
        location,
        job_type,
        category,
        requirements,
        benefits,
        skills,
        salary_min,
        salary_max,
        salary_text,
        experience,
        level,
        deadline,
        source,
        source_url,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for category, config in JOB_CONFIG.items():

        titles = config["titles"][:config["count"]]

        for index, title in enumerate(titles, start=1):

            job = create_job(
                title,
                category,
                config,
                index
            )

            cursor.execute(sql, job)
            inserted += 1

    connection.commit()

    # =====================================================
    # RESULT
    # =====================================================

    cursor.execute("""
        SELECT category, COUNT(*)
        FROM jobs
        WHERE source = ?
        GROUP BY category
        ORDER BY category
    """, (SOURCE,))

    result = cursor.fetchall()

    print("\n===== JOB DATASET =====")

    for category, count in result:
        print(f"{category:<30} {count}")

    print("------------------------------")
    print("Demo jobs inserted:", inserted)

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    print("Total jobs in database:", total_jobs)

    connection.close()

    print("\nSeed jobs thành công!")


if __name__ == "__main__":
    seed_jobs()