import re
import unicodedata
from urllib.parse import urlencode
from database.database import get_connection


# =========================================================
# 1. CHUẨN HÓA VĂN BẢN TIẾNG VIỆT
# =========================================================

def chatbot_normalize(text):
    """Chuẩn hóa câu hỏi về chữ thường không dấu để dễ trích xuất thông tin."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )
    text = text.replace("đ", "d")
    text = re.sub(r"[^a-z0-9+#/.\-\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# =========================================================
# 2. TỪ ĐIỂN NHẬN DIỆN THỰC THỂ VIỆC LÀM (DATABASE MAPPING)
# =========================================================

# Ánh xạ từ khóa người dùng sang đúng Category trong bảng `jobs`
CATEGORY_KEYWORDS = [
    (
        "Backend Development",
        [
            "backend", "back end", "back-end",
            "api developer", "spring boot", "flask developer",
            "java backend", "python backend", "lap trinh backend"
        ]
    ),
    (
        "Frontend Development",
        [
            "frontend", "front end", "front-end",
            "react developer", "javascript developer",
            "giao dien web", "lap trinh frontend", "lap trinh giao dien"
        ]
    ),
    (
        "Full Stack Development",
        [
            "fullstack", "full stack", "full-stack",
            "web application developer", "lap trinh fullstack"
        ]
    ),
    (
        "AI / Machine Learning",
        [
            "ai/ml", "machine learning", "ai engineer",
            "nlp engineer", "computer vision", "tri tue nhan tao",
            "hoc may", "deep learning", "ml engineer",
            "nganh ai", "viec lam ai", "tim viec ai", "job ai",
            "tuyen ai", "vi tri ai", "mang ai", "nlp"
        ]
    ),
    (
        "Data",
        [
            "data analyst", "data engineer", "data scientist",
            "data science", "bi developer", "phan tich du lieu",
            "ky su du lieu", "khoa hoc du lieu", "business intelligence",
            "nganh data", "viec lam data", "tim viec data",
            "job data", "mang data", "du lieu"
        ]
    ),
    (
        "DevOps / Cloud",
        [
            "devops", "cloud engineer", "cloud operations",
            "infrastructure engineer", "dien toan dam may",
            "nganh cloud", "viec lam cloud", "job cloud",
            "he thong cloud", "sre"
        ]
    ),
    (
        "Cybersecurity",
        [
            "cybersecurity", "an ninh mang", "bao mat",
            "security analyst", "pentest", "penetration tester",
            "soc analyst", "information security", "attt",
            "bao mat thong tin"
        ]
    ),
    (
        "Network / System",
        [
            "network engineer", "network administrator",
            "system administrator", "system admin", "sysadmin",
            "it support", "it infrastructure", "quan tri mang",
            "quan tri he thong", "ky su mang", "ha tang mang",
            "mang may tinh"
        ]
    ),
    (
        "Software Testing / QA",
        [
            "software tester", "manual tester", "junior tester",
            "tester", "qa engineer", "qa intern", "kiem thu",
            "kiem thu phan mem", "testing", "qa/qc", "qc"
        ]
    ),
    (
        "Mobile Development",
        [
            "mobile developer", "mobile", "android developer",
            "android", "flutter developer", "ios developer",
            "lap trinh di dong", "ung dung di dong", "app mobile"
        ]
    ),
    (
        "Game Development",
        [
            "game developer", "unity developer", "unity game",
            "unreal engine", "lam game", "lap trinh game",
            "phat trien game", "nganh game", "job game",
            "viec lam game", "tim viec game"
        ]
    ),
]

# Danh sách kỹ năng thực tế trong bảng `jobs`
SKILL_PATTERNS = [
    ("Unreal Engine", [r"\bunreal engine\b", r"\bunreal\b"]),
    ("Machine Learning", [r"\bmachine learning\b", r"\bhoc may\b"]),
    ("Deep Learning", [r"\bdeep learning\b", r"\bhoc sau\b"]),
    ("Cybersecurity", [r"\bcybersecurity\b", r"\ban ninh mang\b"]),
    ("Power BI", [r"\bpower bi\b", r"\bpowerbi\b"]),
    ("Spring", [r"\bspring boot\b", r"\bspring\b"]),
    ("JavaScript", [r"\bjavascript\b", r"\bjs\b"]),
    ("TensorFlow", [r"\btensorflow\b"]),
    ("Kubernetes", [r"\bkubernetes\b", r"\bk8s\b"]),
    ("Networking", [r"\bnetworking\b", r"\bmang may tinh\b"]),
    ("Bootstrap", [r"\bbootstrap\b"]),
    ("PyTorch", [r"\bpytorch\b"]),
    ("Flutter", [r"\bflutter\b"]),
    ("Testing", [r"\btesting\b", r"\bmanual test\b", r"\bautomation test\b"]),
    ("Windows", [r"\bwindows server\b", r"\bwindows\b"]),
    ("Python", [r"\bpython\b"]),
    ("Docker", [r"\bdocker\b"]),
    ("Pandas", [r"\bpandas\b"]),
    ("React", [r"\breactjs\b", r"\breact\.js\b", r"\breact\b"]),
    ("Flask", [r"\bflask\b"]),
    ("Linux", [r"\blinux\b", r"\bubuntu\b"]),
    ("Unity", [r"\bunity\b"]),
    ("Azure", [r"\bazure\b"]),
    ("Cisco", [r"\bcisco\b", r"\bccna\b"]),
    ("Excel", [r"\bexcel\b"]),
    ("NumPy", [r"\bnumpy\b"]),
    ("HTML", [r"\bhtml5?\b"]),
    ("Java", [r"\bjava\b"]),
    ("Dart", [r"\bdart\b"]),
    ("CSS", [r"\bcss3?\b"]),
    ("SQL", [r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b", r"\bsqlite\b"]),
    ("AWS", [r"\baws\b"]),
    ("Git", [r"\bgit\b", r"\bgithub\b"]),
    ("C++", [r"(?<![a-z0-9])c\+\+(?![a-z0-9])", r"\bcpp\b"]),
    ("C#", [r"(?<![a-z0-9])c#(?![a-z0-9])", r"\bcsharp\b", r"\b\.net\b", r"\bdotnet\b"]),
]

# Địa điểm làm việc
LOCATION_KEYWORDS = [
    ("Hà Nội", ["ha noi", "hanoi", "hn", "thu do"]),
    (
        "TP. Hồ Chí Minh",
        [
            "ho chi minh", "tp. ho chi minh", "tp ho chi minh",
            "tphcm", "tp hcm", "hcm", "sai gon", "saigon", "sg"
        ]
    ),
    ("Đà Nẵng", ["da nang", "danang", "dn"]),
    (
        "Remote",
        [
            "remote", "tu xa", "lam tu xa",
            "work from home", "wfh", "lam online", "tai nha"
        ]
    ),
]

# Danh sách công ty trong hệ thống
COMPANY_KEYWORDS = [
    ("FutureSoft", ["futuresoft", "future soft"]),
    ("CloudCore Technology", ["cloudcore", "cloud core"]),
    ("Digital Future Lab", ["digital future"]),
    ("DataVision Solutions", ["datavision", "data vision"]),
    ("Innovatech Labs", ["innovatech"]),
    ("TechNova Solutions", ["technova", "tech nova"]),
    ("NextGen Software", ["nextgen", "next gen"]),
    ("CyberShield Technology", ["cybershield", "cyber shield"]),
    ("BlueOcean Software", ["blueocean", "blue ocean"]),
    ("SmartTech Vietnam", ["smarttech", "smart tech"]),
    ("Tech AI", ["tech ai"]),
    ("Data Solutions", ["data solutions"]),
    ("Software Tech", ["software tech"]),
    ("Web Solutions", ["web solutions"]),
    ("Cloud Tech", ["cloud tech"]),
    ("Cloud Solutions", ["cloud solutions"]),
    ("Secure IT", ["secure it"]),
    ("Network Solutions", ["network solutions"]),
    ("IT Infrastructure", ["it infrastructure"]),
    ("AI Lab", ["ai lab"]),
]

DEFAULT_SUGGESTIONS = [
    "Tìm việc làm IT đang tuyển",
    "Việc làm Thực tập / Fresher",
    "Thống kê việc làm trên web",
    "Cách viết CV IT",
]


# =========================================================
# 3. TRÍCH XUẤT THÔNG TIN TỪ CÂU HỎI ỨNG VIÊN
# =========================================================

def extract_entities(message):
    """Phân tích câu hỏi của ứng viên để lấy bộ lọc việc làm."""
    norm = chatbot_normalize(message)
    entities = {
        "category": None,
        "skills": [],
        "location": None,
        "level": None,
        "job_type": None,
        "no_experience": False,
        "min_salary": None,
        "max_salary": None,
        "salary_sort": None,
        "company": None,
        "job_id": None,
        "ordinal": None,
    }

    # 1. Category
    best_cat_len = 0
    for category, kw_list in CATEGORY_KEYWORDS:
        for kw in kw_list:
            kw_norm = chatbot_normalize(kw)
            if kw_norm in norm and len(kw_norm) > best_cat_len:
                entities["category"] = category
                best_cat_len = len(kw_norm)

    # Kiểm tra từ đơn đặc biệt nếu chưa bắt được category
    if not entities["category"]:
        if re.search(r"\b(qa|qc)\b", norm):
            entities["category"] = "Software Testing / QA"
        elif re.search(r"\b(ai|ml)\b", norm):
            entities["category"] = "AI / Machine Learning"
        elif re.search(r"\bdata\b", norm):
            entities["category"] = "Data"
        elif re.search(r"\bcloud\b", norm):
            entities["category"] = "DevOps / Cloud"
        elif re.search(r"\bgame\b", norm):
            entities["category"] = "Game Development"
        elif re.search(r"\bnetwork\b", norm):
            entities["category"] = "Network / System"

    # 2. Skills
    found_skills = []
    for skill_name, patterns in SKILL_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, norm):
                found_skills.append(skill_name)
                break
    entities["skills"] = found_skills

    # 3. Location
    for loc_name, kw_list in LOCATION_KEYWORDS:
        for kw in kw_list:
            if re.search(r"\b" + re.escape(kw) + r"\b", norm):
                entities["location"] = loc_name
                break
        if entities["location"]:
            break

    # 4. Level / Job Type / Experience
    has_intern = bool(re.search(r"\b(thuc tap|thuc tap sinh|intern|internship)\b", norm))
    has_fresher = bool(re.search(r"\b(fresher|moi ra truong|moi tot nghiep|sinh vien moi ra truong)\b", norm))

    if has_intern and has_fresher:
        entities["level"] = "Intern / Fresher"
    elif has_intern:
        entities["level"] = "Intern"
        entities["job_type"] = "Internship"
    elif has_fresher:
        entities["level"] = "Fresher"
    elif re.search(r"\bjunior\b", norm):
        entities["level"] = "Junior"

    if re.search(r"\b(full time|full-time|fulltime|toan thoi gian|chinh thuc)\b", norm):
        entities["job_type"] = "Full-time"

    if any(
        phrase in norm
        for phrase in [
            "khong yeu cau kinh nghiem",
            "khong can kinh nghiem",
            "chua co kinh nghiem",
            "0 nam kinh nghiem"
        ]
    ):
        entities["no_experience"] = True

    # 5. Company
    for comp_name, kw_list in COMPANY_KEYWORDS:
        if any(kw in norm for kw in kw_list):
            entities["company"] = comp_name
            break

    # 6. Salary parsing (đơn vị: triệu VNĐ)
    # Ví dụ: "từ 10 đến 15 triệu", "10 - 15 triệu"
    range_match = re.search(
        r"(?:tu\s+)?(\d{1,2})\s*(?:den|-|toi)\s*(\d{1,2})\s*(?:trieu|tr|m\b|cu\b)",
        norm
    )
    if range_match:
        low = int(range_match.group(1)) * 1_000_000
        high = int(range_match.group(2)) * 1_000_000
        entities["min_salary"] = min(low, high)
        entities["max_salary"] = max(low, high)
    else:
        # "trên 15 triệu", "từ 15 triệu", "hơn 15 triệu", ">= 15 triệu"
        min_match = re.search(
            r"(?:tren|tu|hon|it nhat|>=?)\s*(\d{1,2})\s*(?:trieu|tr|m\b|cu\b)",
            norm
        )
        # "dưới 10 triệu", "tối đa 10 triệu", "<= 10 triệu"
        max_match = re.search(
            r"(?:duoi|it hon|toi da|<=?)\s*(\d{1,2})\s*(?:trieu|tr|m\b|cu\b)",
            norm
        )
        # "lương 15 triệu", "khoảng 15 triệu"
        exact_match = re.search(
            r"(?:luong|muc luong|khoang|tam)\s*(\d{1,2})\s*(?:trieu|tr|m\b|cu\b)",
            norm
        )

        if min_match:
            entities["min_salary"] = int(min_match.group(1)) * 1_000_000
        if max_match:
            entities["max_salary"] = int(max_match.group(1)) * 1_000_000
        if not min_match and not max_match and exact_match:
            target = int(exact_match.group(1)) * 1_000_000
            entities["min_salary"] = target
            entities["max_salary"] = target

    if any(
        phrase in norm
        for phrase in [
            "luong cao nhat", "luong tot nhat",
            "luong cao", "top luong", "muc luong cao"
        ]
    ):
        entities["salary_sort"] = "high"

    # 7. Mã công việc (Job ID) hoặc Số thứ tự (Ordinal trong danh sách vừa hiển thị)
    id_match = re.search(r"(?:ma|id|job\s*id|#)\s*(\d{1,4})\b", norm)
    if id_match:
        entities["job_id"] = int(id_match.group(1))

    ord_match = re.search(
        r"(?:so|thu|vi tri|cong viec|job|muc)\s*(\d)\b",
        norm
    )
    if ord_match and not entities["job_id"]:
        idx = int(ord_match.group(1))
        if 1 <= idx <= 10:
            entities["ordinal"] = idx - 1
    elif any(p in norm for p in ["cong viec dau tien", "job dau tien", "vi tri dau tien"]):
        entities["ordinal"] = 0

    return entities


def has_any_job_filter(entities):
    """Kiểm tra xem câu hỏi có chứa ít nhất một tiêu chí lọc công việc không."""
    return bool(
        entities.get("category")
        or entities.get("skills")
        or entities.get("location")
        or entities.get("level")
        or entities.get("job_type")
        or entities.get("no_experience")
        or entities.get("min_salary") is not None
        or entities.get("max_salary") is not None
        or entities.get("salary_sort")
        or entities.get("company")
    )


# =========================================================
# 4. TRUY VẤN DATABASE VIỆC LÀM (`jobs`)
# =========================================================

def build_job_query_conditions(filters):
    """Tạo mệnh đề WHERE và tham số SQL từ bộ lọc."""
    where = ["COALESCE(status, 'active') = 'active'"]
    params = []

    category = filters.get("category")
    if category:
        where.append("category = ?")
        params.append(category)

    location = filters.get("location")
    if location:
        if location == "TP. Hồ Chí Minh":
            where.append(
                "(location LIKE ? OR location LIKE ?)"
            )
            params.extend(["%Hồ Chí Minh%", "%Ho Chi Minh%"])
        else:
            where.append("location LIKE ?")
            params.append(f"%{location}%")

    level = filters.get("level")
    job_type = filters.get("job_type")
    if level == "Intern / Fresher":
        where.append(
            "(level IN ('Intern', 'Fresher') OR job_type = 'Internship' OR title LIKE '%Intern%')"
        )
    elif level == "Intern" or job_type == "Internship":
        where.append(
            "(level = 'Intern' OR job_type = 'Internship' OR title LIKE '%Intern%')"
        )
    else:
        if level:
            where.append("level = ?")
            params.append(level)
        if job_type:
            where.append("job_type = ?")
            params.append(job_type)

    if filters.get("no_experience"):
        where.append(
            "(experience LIKE '%Không yêu cầu%' OR level IN ('Intern', 'Fresher'))"
        )

    company = filters.get("company")
    if company:
        where.append("company LIKE ?")
        params.append(f"%{company}%")

    skills = filters.get("skills") or []
    for skill in skills:
        where.append(
            "(skills LIKE ? OR title LIKE ? OR description LIKE ? OR requirements LIKE ?)"
        )
        kw = f"%{skill}%"
        params.extend([kw, kw, kw, kw])

    min_sal = filters.get("min_salary")
    max_sal = filters.get("max_salary")
    if min_sal is not None and max_sal is not None and min_sal == max_sal:
        # Tìm công việc có khoảng lương bao phủ mức lương người dùng hỏi
        where.append("salary_max >= ? AND (salary_min <= ? OR salary_min = 0)")
        params.extend([min_sal, max_sal + 3_000_000])
    else:
        if min_sal is not None:
            where.append("salary_max >= ?")
            params.append(min_sal)
        if max_sal is not None:
            where.append("salary_min > 0 AND salary_min <= ?")
            params.append(max_sal)

    return where, params


def query_jobs_from_db(filters, limit=5, offset=0):
    """Truy vấn danh sách công việc thực tế từ bảng `jobs`."""
    where, params = build_job_query_conditions(filters)
    where_sql = " AND ".join(where)

    if filters.get("salary_sort") == "high":
        order_sql = "ORDER BY COALESCE(salary_max, 0) DESC, job_id DESC"
    else:
        order_sql = (
            "ORDER BY CASE WHEN COALESCE(salary_max, 0) > 0 THEN 0 ELSE 1 END, "
            "job_id DESC"
        )

    connection = get_connection()
    try:
        total_row = connection.execute(
            f"SELECT COUNT(*) AS total FROM jobs WHERE {where_sql}",
            params
        ).fetchone()
        total = total_row["total"] if total_row else 0

        rows = connection.execute(
            f"""
            SELECT
                job_id, title, company, location,
                job_type, category, level, experience,
                salary_min, salary_max, salary_text,
                skills, deadline
            FROM jobs
            WHERE {where_sql}
            {order_sql}
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset]
        ).fetchall()

        return total, [dict(r) for r in rows]
    finally:
        connection.close()


def get_job_by_id_or_title(job_id=None, message=""):
    """Tìm 1 công việc cụ thể theo ID hoặc theo tên tiêu đề trong câu hỏi."""
    connection = get_connection()
    try:
        if job_id is not None:
            row = connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,)
            ).fetchone()
            if row:
                return dict(row)

        # Thử khớp theo tiêu đề công việc trong DB
        norm_msg = chatbot_normalize(message)
        all_jobs = connection.execute(
            """
            SELECT * FROM jobs
            WHERE COALESCE(status, 'active') = 'active'
            ORDER BY job_id DESC
            """
        ).fetchall()

        best_job = None
        best_len = 0
        for row in all_jobs:
            title_norm = chatbot_normalize(row["title"])
            if title_norm and len(title_norm) >= 6 and title_norm in norm_msg:
                if len(title_norm) > best_len:
                    best_len = len(title_norm)
                    best_job = dict(row)

        return best_job
    finally:
        connection.close()


def format_salary(job):
    """Định dạng chuỗi lương hiển thị thân thiện."""
    if job.get("salary_text"):
        return job["salary_text"]
    s_min = job.get("salary_min") or 0
    s_max = job.get("salary_max") or 0
    if s_min > 0 and s_max > 0:
        return f"{s_min // 1_000_000} - {s_max // 1_000_000} triệu"
    if s_max > 0:
        return f"Tối đa {s_max // 1_000_000} triệu"
    return "Thỏa thuận"


def describe_filters(filters):
    """Tạo chuỗi mô tả ngắn gọn các tiêu chí đang lọc."""
    parts = []
    if filters.get("category"):
        parts.append(f"ngành {filters['category']}")
    if filters.get("skills"):
        parts.append(f"kỹ năng {', '.join(filters['skills'])}")
    if filters.get("level"):
        parts.append(f"cấp độ {filters['level']}")
    elif filters.get("job_type"):
        parts.append(f"hình thức {filters['job_type']}")
    if filters.get("no_experience"):
        parts.append("không yêu cầu kinh nghiệm")
    if filters.get("location"):
        parts.append(f"tại {filters['location']}")
    if filters.get("company"):
        parts.append(f"công ty {filters['company']}")

    min_s = filters.get("min_salary")
    max_s = filters.get("max_salary")
    if min_s and max_s and min_s != max_s:
        parts.append(f"lương {min_s // 1_000_000}–{max_s // 1_000_000} triệu")
    elif min_s:
        parts.append(f"lương từ {min_s // 1_000_000} triệu")
    elif max_s:
        parts.append(f"lương dưới {max_s // 1_000_000} triệu")

    if filters.get("salary_sort") == "high":
        parts.append("sắp xếp lương cao nhất")

    return ", ".join(parts) if parts else "tất cả vị trí IT đang mở"


def build_jobs_page_url(filters):
    """Tạo đường dẫn `/jobs?...` tương ứng với bộ lọc để ứng viên mở trên web."""
    query = {}
    if filters.get("category"):
        query["category"] = filters["category"]
    if filters.get("location"):
        query["location"] = filters["location"]
    if filters.get("job_type"):
        query["job_type"] = filters["job_type"]
    if filters.get("level") and filters.get("level") != "Intern / Fresher":
        query["level"] = filters["level"]
    if filters.get("skills"):
        query["q"] = filters["skills"][0]
    elif filters.get("company"):
        query["q"] = filters["company"]
    if filters.get("salary_sort") == "high":
        query["sort"] = "salary_high"

    if query:
        return "/jobs?" + urlencode(query)
    return "/jobs"


# =========================================================
# 5. XÂY DỰNG PHẢN HỒI CHO TỪNG Ý ĐỊNH (INTENT HANDLERS)
# =========================================================

def handle_cv_analysis_redirect(user_id=None):
    """
    Khi ứng viên hỏi về đánh giá/phân tích CV hoặc kỹ năng của mình hợp nghề gì:
    Đề xuất ứng viên sử dụng trực tiếp chức năng Phân tích CV & Gợi ý việc làm của Web.
    """
    reply = (
        "📄 ĐÁNH GIÁ CV & ĐỊNH HƯỚNG NGHỀ NGHIỆP TRÊN WEB\n\n"
        "Hệ thống IT Career Match đã tích hợp sẵn công cụ Phân tích CV "
        "và Gợi ý việc làm bằng AI/Machine Learning chuyên biệt trên website.\n\n"
        "Để biết chính xác CV và kỹ năng của bạn hợp với nghề gì, bạn hãy thực hiện trên web theo các bước sau:\n"
        "1. Mở trang «Tải CV lên» và chọn file CV của bạn (PDF hoặc DOCX).\n"
        "2. Hệ thống sẽ tự động trích xuất kỹ năng và dự đoán nhóm nghề IT phù hợp nhất.\n"
        "3. Chuyển sang trang «Gợi ý việc làm» để xem danh sách công việc kèm điểm phù hợp (Match Score), "
        "các kỹ năng đã khớp (Matched Skills) và kỹ năng cần bổ sung (Missing Skills).\n\n"
        "Bạn có thể nhấn vào các nút bên dưới để sử dụng tính năng này ngay, "
        "hoặc nhắn cho mình vị trí/kỹ năng bạn muốn tìm việc để mình tra cứu công việc đang tuyển nhé!"
    )

    actions = [
        {"label": "📄 Tải CV & Phân tích ngay", "url": "/upload-cv"},
        {"label": "🎯 Xem Gợi ý việc làm", "url": "/recommendations"},
        {"label": "👤 Cập nhật Hồ sơ cá nhân", "url": "/profile"},
    ]

    suggestions = [
        "Tìm việc làm IT đang tuyển",
        "Việc làm Thực tập / Fresher",
        "Cách viết CV IT",
        "Phỏng vấn IT",
    ]

    return {
        "reply": reply,
        "actions": actions,
        "suggestions": suggestions,
    }


def handle_job_detail(job, context):
    """Hiển thị thông tin chi tiết của 1 công việc từ database."""
    salary_str = format_salary(job)
    level_str = job.get("level") or "Không phân cấp"
    exp_str = job.get("experience") or "Trao đổi khi phỏng vấn"
    skills_str = job.get("skills") or "Xem trong mô tả công việc"
    deadline_str = job.get("deadline") or "Đang mở tuyển"

    lines = [
        f"💼 CHI TIẾT CÔNG VIỆC #{job['job_id']}",
        f"• Vị trí: {job['title']}",
        f"• Công ty: {job['company']}",
        f"• Nhóm nghề: {job.get('category') or 'IT'}",
        f"• Địa điểm: {job.get('location') or 'Việt Nam'}",
        f"• Hình thức: {job.get('job_type') or 'Full-time'} | Cấp độ: {level_str}",
        f"• Kinh nghiệm: {exp_str}",
        f"• Mức lương: {salary_str}",
        f"• Kỹ năng cần có: {skills_str}",
        f"• Hạn nộp hồ sơ: {deadline_str}",
    ]

    if job.get("description"):
        desc = job["description"].strip()
        lines.append(f"\n📌 Mô tả công việc:\n{desc}")

    if job.get("requirements"):
        req = job["requirements"].strip()
        lines.append(f"\n✅ Yêu cầu ứng viên:\n{req}")

    if job.get("benefits"):
        ben = job["benefits"].strip()
        lines.append(f"\n🎁 Quyền lợi:\n{ben}")

    context["last_intent"] = "job_detail"
    if job.get("category"):
        context.setdefault("filters", {})["category"] = job["category"]

    cat = job.get("category") or "IT"
    suggestions = [
        f"Tìm việc {cat}",
        f"Việc làm công ty {job['company']}",
        "Việc làm Thực tập / Fresher",
        "Thống kê việc làm trên web",
    ]

    return {
        "reply": "\n".join(lines),
        "actions": [
            {
                "label": f"🔗 Mở trang công việc: {job['title']}",
                "url": f"/jobs/{job['job_id']}"
            },
            {
                "label": "🔎 Xem danh sách việc làm",
                "url": "/jobs"
            }
        ],
        "suggestions": suggestions,
    }


def handle_job_salary_inquiry(filters, context):
    """Giải đáp thắc mắc về mức lương dựa trên dữ liệu thực tế trong bảng `jobs`."""
    where, params = build_job_query_conditions(filters)
    where.append("COALESCE(salary_max, 0) > 0")
    where_sql = " AND ".join(where)

    connection = get_connection()
    try:
        stats = connection.execute(
            f"""
            SELECT
                COUNT(*) AS count_jobs,
                MIN(salary_min) AS min_sal,
                MAX(salary_max) AS max_sal,
                AVG((salary_min + salary_max) / 2.0) AS avg_sal
            FROM jobs
            WHERE {where_sql}
            """,
            params
        ).fetchone()

        top_jobs = connection.execute(
            f"""
            SELECT job_id, title, company, location, level, salary_text, salary_min, salary_max
            FROM jobs
            WHERE {where_sql}
            ORDER BY salary_max DESC, job_id DESC
            LIMIT 5
            """,
            params
        ).fetchall()
    finally:
        connection.close()

    filter_desc = describe_filters(filters)

    if not stats or stats["count_jobs"] == 0:
        return {
            "reply": (
                f"💰 THÔNG TIN MỨC LƯƠNG ({filter_desc})\n\n"
                "Hiện chưa có dữ liệu mức lương cụ thể cho bộ lọc này. "
                "Tuy nhiên trên hệ thống, mặt bằng lương các vị trí IT đang mở dao động:\n"
                "• Thực tập sinh (Intern): 3 – 9 triệu VNĐ/tháng\n"
                "• Fresher (Mới ra trường): 8 – 23 triệu VNĐ/tháng\n"
                "• Junior (1 – 2 năm KN): 10 – 26 triệu VNĐ/tháng\n\n"
                "Bạn có thể hỏi mức lương theo từng ngành cụ thể nhé!"
            ),
            "actions": [{"label": "🔎 Xem việc làm theo lương cao nhất", "url": "/jobs?sort=salary_high"}],
            "suggestions": [
                "Công việc nào lương cao nhất?",
                "Lương ngành Backend",
                "Lương ngành AI / Machine Learning",
                "Việc làm lương trên 15 triệu",
            ],
        }

    min_m = (stats["min_sal"] or 0) // 1_000_000
    max_m = (stats["max_sal"] or 0) // 1_000_000
    avg_m = round((stats["avg_sal"] or 0) / 1_000_000, 1)

    lines = [
        f"💰 THỐNG KÊ MỨC LƯƠNG THỰC TẾ ({filter_desc})",
        f"Dựa trên {stats['count_jobs']} công việc có công bố lương trên hệ thống:\n",
        f"• Mức thấp nhất: ~{min_m} triệu VNĐ",
        f"• Mức cao nhất: ~{max_m} triệu VNĐ",
        f"• Mức trung bình: ~{avg_m} triệu VNĐ\n",
        "📌 Các vị trí có mức lương nổi bật đang tuyển:",
    ]

    actions = []
    job_ids = []
    for idx, j in enumerate(top_jobs, start=1):
        j_dict = dict(j)
        job_ids.append(j_dict["job_id"])
        sal = format_salary(j_dict)
        lvl = f" ({j_dict['level']})" if j_dict.get("level") else ""
        lines.append(
            f"{idx}. {j_dict['title']}{lvl} — {j_dict['company']}\n"
            f"   📍 {j_dict['location']} | 💵 {sal}"
        )
        actions.append({
            "label": f"#{idx} {j_dict['title']} ({sal})",
            "url": f"/jobs/{j_dict['job_id']}"
        })

    lines.append("\n💡 Bạn có thể nhắn «Chi tiết công việc số 1» để xem yêu cầu cụ thể!")

    context["last_intent"] = "job_salary"
    context["filters"] = filters
    context["last_job_ids"] = job_ids

    return {
        "reply": "\n".join(lines),
        "actions": actions[:4],
        "suggestions": [
            "Chi tiết công việc số 1",
            "Việc làm lương trên 15 triệu",
            "Việc làm lương từ 10 đến 15 triệu",
            "Tìm việc Thực tập / Fresher",
        ],
    }


def handle_job_skills_inquiry(filters, context):
    """Tổng hợp các kỹ năng thực tế mà các công việc trên web đang yêu cầu."""
    where, params = build_job_query_conditions(filters)
    where_sql = " AND ".join(where)

    connection = get_connection()
    try:
        rows = connection.execute(
            f"""
            SELECT job_id, title, company, location, skills, salary_text, salary_min, salary_max
            FROM jobs
            WHERE {where_sql}
            ORDER BY job_id DESC
            """,
            params
        ).fetchall()
    finally:
        connection.close()

    filter_desc = describe_filters(filters)
    if not rows:
        return {
            "reply": (
                f"Hiện mình chưa tìm thấy công việc nào khớp với tiêu chí ({filter_desc}) "
                "để thống kê kỹ năng yêu cầu. Bạn thử chọn ngành khác nhé!"
            ),
            "actions": [{"label": "🔎 Xem tất cả việc làm", "url": "/jobs"}],
            "suggestions": DEFAULT_SUGGESTIONS,
        }

    skill_counts = {}
    for r in rows:
        raw_skills = r["skills"] or ""
        for s in raw_skills.split(","):
            s_clean = s.strip()
            if s_clean:
                skill_counts[s_clean] = skill_counts.get(s_clean, 0) + 1

    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)

    lines = [
        f"🛠️ YÊU CẦU KỸ NĂNG TỪ NHÀ TUYỂN DỤNG ({filter_desc})",
        f"Tổng hợp từ {len(rows)} công việc đang mở trên IT Career Match:\n",
    ]

    if sorted_skills:
        lines.append("📊 Các kỹ năng được yêu cầu nhiều nhất:")
        for skill_name, count in sorted_skills[:8]:
            lines.append(f"• {skill_name}: xuất hiện trong {count} công việc")
    else:
        lines.append("• Các công việc yêu cầu kiến thức nền tảng IT, Git, SQL và kỹ năng chuyên ngành.")

    lines.append("\n💼 Một số công việc tiêu biểu đang tuyển:")
    actions = []
    job_ids = []
    for idx, r in enumerate(rows[:4], start=1):
        j = dict(r)
        job_ids.append(j["job_id"])
        sal = format_salary(j)
        lines.append(
            f"{idx}. {j['title']} — {j['company']} ({j['location']})\n"
            f"   🔧 Kỹ năng: {j.get('skills') or 'Đang cập nhật'} | 💵 {sal}"
        )
        actions.append({
            "label": f"#{idx} {j['title']}",
            "url": f"/jobs/{j['job_id']}"
        })

    context["last_intent"] = "job_skills"
    context["filters"] = filters
    context["last_job_ids"] = job_ids

    return {
        "reply": "\n".join(lines),
        "actions": actions,
        "suggestions": [
            "Chi tiết công việc số 1",
            "Mức lương vị trí này bao nhiêu?",
            "Có tuyển Intern / Fresher không?",
            "Tìm việc ở Hà Nội",
        ],
    }


def handle_job_stats_overview(context):
    """Thống kê tổng quan toàn bộ việc làm đang tuyển trong database."""
    connection = get_connection()
    try:
        total = connection.execute(
            "SELECT COUNT(*) AS c FROM jobs WHERE COALESCE(status, 'active') = 'active'"
        ).fetchone()["c"]

        by_cat = connection.execute(
            """
            SELECT category, COUNT(*) AS c
            FROM jobs
            WHERE COALESCE(status, 'active') = 'active'
              AND category IS NOT NULL
            GROUP BY category
            ORDER BY c DESC
            """
        ).fetchall()

        by_loc = connection.execute(
            """
            SELECT
                CASE
                    WHEN location LIKE '%Hồ Chí Minh%' OR location LIKE '%Ho Chi Minh%'
                    THEN 'TP. Hồ Chí Minh'
                    ELSE location
                END AS loc_name,
                COUNT(*) AS c
            FROM jobs
            WHERE COALESCE(status, 'active') = 'active'
              AND location IS NOT NULL
            GROUP BY loc_name
            ORDER BY c DESC
            """
        ).fetchall()

        intern_count = connection.execute(
            """
            SELECT COUNT(*) AS c
            FROM jobs
            WHERE COALESCE(status, 'active') = 'active'
              AND (level = 'Intern' OR job_type = 'Internship')
            """
        ).fetchone()["c"]

        fresher_count = connection.execute(
            """
            SELECT COUNT(*) AS c
            FROM jobs
            WHERE COALESCE(status, 'active') = 'active'
              AND level = 'Fresher'
            """
        ).fetchone()["c"]
    finally:
        connection.close()

    lines = [
        f"📊 TỔNG QUAN VIỆC LÀM TRÊN IT CAREER MATCH",
        f"Hiện tại hệ thống đang có {total} công việc đang mở tuyển:\n",
        "📂 Theo nhóm ngành:",
    ]
    for row in by_cat:
        lines.append(f"• {row['category']}: {row['c']} việc làm")

    lines.append("\n📍 Theo khu vực:")
    for row in by_loc:
        lines.append(f"• {row['loc_name']}: {row['c']} việc làm")

    lines.append(
        f"\n🎓 Dành cho sinh viên & người mới:\n"
        f"• Thực tập sinh (Intern / Internship): {intern_count} việc làm\n"
        f"• Mới ra trường (Fresher): {fresher_count} việc làm\n\n"
        "Bạn muốn tìm công việc ở ngành nào, kỹ năng gì hay khu vực nào? Hãy nhắn cho mình nhé!"
    )

    context["last_intent"] = "job_stats"

    return {
        "reply": "\n".join(lines),
        "actions": [
            {"label": "🔎 Khám phá tất cả việc làm", "url": "/jobs"},
            {"label": "🎓 Việc làm Thực tập (Internship)", "url": "/jobs?job_type=Internship"},
        ],
        "suggestions": [
            "Tìm việc Backend",
            "Tìm việc AI / Machine Learning",
            "Việc làm Thực tập / Fresher",
            "Việc làm tại TP. Hồ Chí Minh",
        ],
    }


def handle_company_overview(context):
    """Thống kê các công ty đang tuyển dụng trên hệ thống."""
    connection = get_connection()
    try:
        companies = connection.execute(
            """
            SELECT company, COUNT(*) AS c
            FROM jobs
            WHERE COALESCE(status, 'active') = 'active'
              AND company IS NOT NULL
            GROUP BY company
            ORDER BY c DESC, company ASC
            """
        ).fetchall()
    finally:
        connection.close()

    lines = [
        f"🏢 DANH SÁCH DOANH NGHIỆP ĐANG TUYỂN DỤNG ({len(companies)} công ty)\n"
    ]
    for idx, row in enumerate(companies[:10], start=1):
        lines.append(f"{idx}. {row['company']} — đang mở {row['c']} vị trí")

    lines.append(
        "\nBạn muốn xem các công việc của công ty nào? "
        "Hãy nhắn tên công ty (ví dụ: «Việc làm công ty FutureSoft») nhé!"
    )

    context["last_intent"] = "company_overview"

    return {
        "reply": "\n".join(lines),
        "actions": [{"label": "🔎 Xem toàn bộ việc làm", "url": "/jobs"}],
        "suggestions": [
            "Việc làm công ty FutureSoft",
            "Việc làm công ty CloudCore Technology",
            "Việc làm công ty Digital Future Lab",
            "Tìm việc Thực tập / Fresher",
        ],
    }


def handle_job_search(filters, context, offset=0):
    """Tìm kiếm việc làm thực tế từ bảng `jobs` và trả về kết quả kèm link."""
    total, jobs = query_jobs_from_db(filters, limit=5, offset=offset)
    filter_desc = describe_filters(filters)

    # Nếu không tìm thấy kết quả do lọc quá hẹp -> Tự động nới lỏng điều kiện để gợi ý
    if total == 0:
        fallback_filters = {}
        if filters.get("category"):
            fallback_filters["category"] = filters["category"]
        elif filters.get("skills"):
            fallback_filters["skills"] = [filters["skills"][0]]
        elif filters.get("location"):
            fallback_filters["location"] = filters["location"]
        elif filters.get("level"):
            fallback_filters["level"] = filters["level"]

        fb_total, fb_jobs = (0, [])
        if fallback_filters and fallback_filters != filters:
            fb_total, fb_jobs = query_jobs_from_db(fallback_filters, limit=4, offset=0)

        lines = [
            f"🔍 Hiện chưa có công việc nào khớp đồng thời tất cả tiêu chí ({filter_desc})."
        ]
        actions = [{"label": "🔎 Xem tất cả việc làm", "url": "/jobs"}]
        job_ids = []

        if fb_jobs:
            fb_desc = describe_filters(fallback_filters)
            lines.append(
                f"\n💡 Tuy nhiên, hệ thống đang có {fb_total} công việc gần nhất ({fb_desc}) bạn có thể tham khảo:"
            )
            for idx, j in enumerate(fb_jobs, start=1):
                job_ids.append(j["job_id"])
                sal = format_salary(j)
                lvl = f" [{j['level']}]" if j.get("level") else ""
                lines.append(
                    f"\n{idx}. {j['title']}{lvl}\n"
                    f"   🏢 {j['company']} | 📍 {j['location']}\n"
                    f"   💵 {sal} | 🔧 {j.get('skills') or 'IT'}"
                )
                actions.insert(idx - 1, {
                    "label": f"#{idx} {j['title']}",
                    "url": f"/jobs/{j['job_id']}"
                })
            context["filters"] = fallback_filters
            context["last_job_ids"] = job_ids
            context["offset"] = 0
        else:
            lines.append(
                "\nBạn hãy thử tìm với từ khóa rộng hơn (ví dụ theo ngành Backend, Frontend, "
                "AI/ML, Data, Tester, Mobile, Game hoặc theo địa điểm Hà Nội, TP.HCM, Đà Nẵng, Remote) nhé!"
            )

        return {
            "reply": "\n".join(lines),
            "actions": actions[:4],
            "suggestions": [
                "Tìm việc làm IT đang tuyển",
                "Việc làm Thực tập / Fresher",
                "Việc làm tại Hà Nội",
                "Việc làm tại TP. Hồ Chí Minh",
            ],
        }

    # Có kết quả khớp
    shown_start = offset + 1
    shown_end = offset + len(jobs)
    lines = [
        f"🎯 TÌM THẤY {total} CÔNG VIỆC PHÙ HỢP ({filter_desc})",
        f"Hiển thị kết quả {shown_start}–{shown_end}:\n",
    ]

    actions = []
    job_ids = []
    for idx, j in enumerate(jobs, start=1):
        job_ids.append(j["job_id"])
        sal = format_salary(j)
        lvl = j.get("level") or j.get("job_type") or "Full-time"
        skills_text = j.get("skills") or "Xem chi tiết"
        lines.append(
            f"{idx}. {j['title']} ({lvl})\n"
            f"   🏢 {j['company']} | 📍 {j.get('location') or 'Việt Nam'}\n"
            f"   💵 Lương: {sal}\n"
            f"   🔧 Kỹ năng: {skills_text}"
        )
        actions.append({
            "label": f"#{idx} {j['title']}",
            "url": f"/jobs/{j['job_id']}"
        })

    # Thêm nút mở trang danh sách đã lọc trên web
    page_url = build_jobs_page_url(filters)
    actions.append({
        "label": f"🔎 Xem tất cả ({total} việc làm)",
        "url": page_url
    })

    lines.append(
        "\n💬 Bạn có thể nhắn «Chi tiết công việc số 1» để xem mô tả đầy đủ, "
        "hoặc lọc thêm theo địa điểm / mức lương / cấp độ nhé!"
    )

    context["last_intent"] = "job_search"
    context["filters"] = filters
    context["last_job_ids"] = job_ids
    context["offset"] = offset
    context["total_last_search"] = total

    # Tạo gợi ý động thông minh theo ngữ cảnh hiện tại
    suggestions = ["Chi tiết công việc số 1"]
    if total > offset + len(jobs):
        suggestions.append("Xem thêm việc làm khác")
    if not filters.get("location"):
        suggestions.append("Ở Hà Nội có không?")
        suggestions.append("Ở TP. Hồ Chí Minh có không?")
    if not filters.get("level"):
        suggestions.append("Có tuyển Thực tập / Fresher không?")
    suggestions.append("Mức lương vị trí này bao nhiêu?")

    return {
        "reply": "\n".join(lines),
        "actions": actions[:4],
        "suggestions": suggestions[:4],
    }


# =========================================================
# 6. ĐIỀU PHỐI HỘI THOẠI CHÍNH (MAIN CHATBOT ROUTER)
# =========================================================

def get_user_first_name(user_id):
    """Lấy tên ứng viên đang đăng nhập để xưng hô thân thiện."""
    if not user_id:
        return None
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT full_name FROM student_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        if row and row["full_name"]:
            return row["full_name"].strip()
        return None
    except Exception:
        return None
    finally:
        connection.close()


def generate_chatbot_response(message, user_id=None, context=None):
    """
    Hàm trung tâm xử lý câu hỏi của ứng viên:
    - Kết hợp ngữ cảnh hội thoại (`context`)
    - Truy vấn dữ liệu việc làm thực tế từ SQLite (`jobs`)
    - Điều hướng đánh giá/phân tích CV sang chức năng có sẵn của Web
    """
    if context is None or not isinstance(context, dict):
        context = {}

    norm = chatbot_normalize(message)
    entities = extract_entities(message)
    prev_filters = dict(context.get("filters") or {})

    # -----------------------------------------------------
    # 1. CÂU HỎI LIÊN QUAN ĐẾN PHÂN TÍCH / ĐÁNH GIÁ CV & ĐỊNH HƯỚNG NGHỀ TỪ CV
    #    -> Đề xuất sử dụng chức năng có sẵn trên Web để tránh trùng lặp
    # -----------------------------------------------------
    cv_evaluation_keywords = [
        "danh gia cv", "phan tich cv", "cham diem cv", "kiem tra cv",
        "nhan xet cv", "xem cv cua minh", "xem cv cua toi",
        "cv cua minh", "cv cua toi", "upload cv", "tai cv",
        "ky nang cua minh hop", "ky nang cua toi hop",
        "minh hop nghe gi", "minh hop nganh nao", "toi hop nghe gi",
        "toi hop nganh nao", "hop voi nghe nao", "hop voi nganh nao",
        "kham pha ban than", "dinh huong cho minh",
        "goi y viec lam cho minh", "goi y viec lam tu cv",
        "viec lam phu hop voi cv", "viec lam hop voi cv",
        "viec lam hop voi minh", "cv thieu ky nang gi",
        "minh thieu ky nang gi", "match score", "diem phu hop",
        "quy trinh danh gia cv", "quy trinh phan tich cv"
    ]
    if any(kw in norm for kw in cv_evaluation_keywords):
        return handle_cv_analysis_redirect(user_id), context

    # Nếu ứng viên liệt kê kỹ năng cá nhân và hỏi hợp nghề gì (VD: "mình biết python, sql thì hợp nghề gì")
    if (
        re.search(r"\b(minh biet|em biet|toi biet|minh co ky nang|em hoc)\b", norm)
        and re.search(r"\b(hop nghe|hop nganh|lam nghe gi|lam vi tri nao|hop vi tri nao)\b", norm)
    ):
        return handle_cv_analysis_redirect(user_id), context

    # -----------------------------------------------------
    # 2. CÁCH VIẾT CV IT (Giữ lại hướng dẫn trình bày CV cơ bản + dẫn link web)
    # -----------------------------------------------------
    if any(
        kw in norm
        for kw in ["cach viet cv", "viet cv", "lam cv", "cv it", "mau cv", "ho so xin viec", "resume"]
    ):
        return {
            "reply": (
                "📄 HƯỚNG DẪN VIẾT CV IT ẤN TƯỢNG\n\n"
                "1. Thông tin liên hệ & Mục tiêu nghề nghiệp rõ ràng (vị trí ứng tuyển: Intern/Fresher/Junior...).\n"
                "2. Kỹ năng kỹ thuật (Technical Skills): Nhóm theo Ngôn ngữ lập trình, Framework, Database, Công cụ (Git, Docker...).\n"
                "3. Dự án thực tế (Projects): Trình bày 2–3 dự án tiêu biểu (Mô tả ngắn, công nghệ sử dụng, vai trò của bạn và link GitHub/Demo).\n"
                "4. Học vấn & Chứng chỉ liên quan.\n"
                "5. Kiểm tra kỹ chính tả và xuất file định dạng PDF hoặc DOCX.\n\n"
                "💡 Sau khi hoàn thiện CV, bạn hãy sử dụng chức năng «Tải CV lên» ngay trên website IT Career Match "
                "để hệ thống phân tích mức độ phù hợp và gợi ý việc làm cho bạn nhé!"
            ),
            "actions": [
                {"label": "📄 Tải CV lên web để phân tích", "url": "/upload-cv"},
                {"label": "🔎 Tìm việc làm IT đang tuyển", "url": "/jobs"},
            ],
            "suggestions": [
                "Tìm việc làm IT đang tuyển",
                "Việc làm Thực tập / Fresher",
                "Phỏng vấn IT",
                "Đánh giá CV của mình",
            ],
        }, context

    # -----------------------------------------------------
    # 3. CHUẨN BỊ PHỎNG VẤN IT (Giữ lại hướng dẫn phỏng vấn cơ bản)
    # -----------------------------------------------------
    if any(kw in norm for kw in ["phong van", "interview", "kinh nghiem phong van"]):
        return {
            "reply": (
                "🎯 CÁCH CHUẨN BỊ PHỎNG VẤN IT HIỆU QUẢ\n\n"
                "1. Nắm vững yêu cầu công việc (JD) và các kỹ năng bắt buộc của vị trí ứng tuyển.\n"
                "2. Chuẩn bị phần giới thiệu bản thân ngắn gọn (1–2 phút) và nắm thật chắc các dự án đã ghi trong CV.\n"
                "3. Ôn tập kiến thức nền tảng: OOP, Cấu trúc dữ liệu & Giải thuật, SQL, Git và kiến thức chuyên ngành.\n"
                "4. Chuẩn bị các tình huống giải quyết lỗi (debug, tối ưu, làm việc nhóm).\n"
                "5. Tìm hiểu trước về công ty và chuẩn bị 1–2 câu hỏi ngược lại cho nhà tuyển dụng.\n\n"
                "💡 Bạn muốn tìm hiểu yêu cầu cụ thể của vị trí nào trên hệ thống để chuẩn bị ứng tuyển? "
                "Hãy nhắn tên vị trí cho mình nhé!"
            ),
            "actions": [{"label": "🔎 Xem các vị trí đang tuyển", "url": "/jobs"}],
            "suggestions": [
                "Tìm việc làm IT đang tuyển",
                "Việc làm Thực tập / Fresher",
                "Các công ty đang tuyển dụng",
                "Cách viết CV IT",
            ],
        }, context

    # -----------------------------------------------------
    # 4. HỎI CHI TIẾT 1 CÔNG VIỆC CỤ THỂ (Theo số thứ tự, ID hoặc Tên Job)
    # -----------------------------------------------------
    is_asking_detail = any(
        kw in norm
        for kw in [
            "chi tiet", "mo ta cong viec", "yeu cau cong viec",
            "quyen loi", "han nop", "thong tin cong viec", "xem cong viec", "xem job"
        ]
    ) or entities["ordinal"] is not None or entities["job_id"] is not None

    if is_asking_detail:
        target_job = None
        # Nếu ứng viên hỏi theo số thứ tự trong danh sách vừa hiển thị ("công việc số 1")
        if entities["ordinal"] is not None:
            last_ids = context.get("last_job_ids") or []
            ord_idx = entities["ordinal"]
            if 0 <= ord_idx < len(last_ids):
                target_job = get_job_by_id_or_title(job_id=last_ids[ord_idx])
        # Hoặc theo mã công việc ("mã 60", "#60")
        if not target_job and entities["job_id"] is not None:
            target_job = get_job_by_id_or_title(job_id=entities["job_id"])
        # Hoặc theo tên công việc trong câu hỏi
        if not target_job:
            target_job = get_job_by_id_or_title(message=message)
        # Hoặc nếu người dùng nói "chi tiết công việc này" khi danh sách trước chỉ có 1-5 job
        if not target_job and ("cong viec nay" in norm or "job nay" in norm or "vi tri nay" in norm):
            last_ids = context.get("last_job_ids") or []
            if last_ids:
                target_job = get_job_by_id_or_title(job_id=last_ids[0])

        if target_job:
            return handle_job_detail(target_job, context), context

    # -----------------------------------------------------
    # 5. XEM THÊM KẾT QUẢ TÌM VIỆC (LOAD MORE / PAGINATION)
    # -----------------------------------------------------
    if any(
        kw in norm
        for kw in [
            "xem them", "con viec nao khac", "con job nao khac",
            "con cong viec nao", "viec lam khac", "tiep theo", "trang sau"
        ]
    ) and prev_filters:
        next_offset = (context.get("offset") or 0) + 5
        total_last = context.get("total_last_search") or 0
        if next_offset >= total_last:
            next_offset = 0
        return handle_job_search(prev_filters, context, offset=next_offset), context

    # -----------------------------------------------------
    # 6. HỎI VỀ MỨC LƯƠNG VIỆC LÀM TRÊN HỆ THỐNG
    # -----------------------------------------------------
    is_asking_salary_info = any(
        kw in norm
        for kw in [
            "luong bao nhieu", "muc luong", "thu nhap",
            "luong nganh", "luong vi tri", "luong cao nhat",
            "luong the nao", "luong ra sao", "che do luong"
        ]
    ) and entities["min_salary"] is None and entities["max_salary"] is None

    if is_asking_salary_info:
        merged_filters = {}
        if has_any_job_filter(entities):
            merged_filters = {k: v for k, v in entities.items() if v}
        elif prev_filters:
            merged_filters = dict(prev_filters)
        return handle_job_salary_inquiry(merged_filters, context), context

    # -----------------------------------------------------
    # 7. HỎI VỀ KỸ NĂNG YÊU CẦU CỦA CÁC CÔNG VIỆC TRÊN WEB
    # -----------------------------------------------------
    is_asking_job_skills = any(
        kw in norm
        for kw in [
            "can ky nang gi", "yeu cau ky nang gi", "can biet gi",
            "can hoc ky nang gi", "yeu cau nhung gi", "ky nang can co"
        ]
    )
    if is_asking_job_skills:
        merged_filters = {}
        if has_any_job_filter(entities):
            merged_filters = {k: v for k, v in entities.items() if v}
        elif prev_filters:
            merged_filters = dict(prev_filters)
        return handle_job_skills_inquiry(merged_filters, context), context

    # -----------------------------------------------------
    # 8. HỎI DANH SÁCH CÔNG TY ĐANG TUYỂN DỤNG
    # -----------------------------------------------------
    if any(
        kw in norm
        for kw in [
            "cong ty nao dang tuyen", "danh sach cong ty",
            "nhung cong ty nao", "cac cong ty tuyen dung",
            "doanh nghiep nao"
        ]
    ) and not entities.get("company"):
        return handle_company_overview(context), context

    # -----------------------------------------------------
    # 9. HỎI THỐNG KÊ / TỔNG QUAN VIỆC LÀM TRÊN WEB
    # -----------------------------------------------------
    if any(
        kw in norm
        for kw in [
            "bao nhieu viec lam", "bao nhieu cong viec", "bao nhieu job",
            "thong ke viec lam", "tong quan viec lam",
            "dang tuyen nhung nganh nao", "co nhung nganh nao",
            "web co nhung viec gi"
        ]
    ):
        return handle_job_stats_overview(context), context

    # -----------------------------------------------------
    # 10. TÌM KIẾM VIỆC LÀM TỪ DATABASE (KÈM GHI NHỚ NGỮ CẢNH HỘI THOẠI)
    # -----------------------------------------------------
    job_search_triggers = [
        "tim viec", "tim job", "tim cong viec", "viec lam",
        "cong viec", "job", "tuyen dung", "dang tuyen",
        "co viec", "co tuyen", "vi tri", "ung tuyen"
    ]
    has_search_trigger = any(kw in norm for kw in job_search_triggers)
    has_filter = has_any_job_filter(entities)

    # Kiểm tra câu hỏi nối tiếp theo ngữ cảnh (VD: "Ở Hà Nội có không?", "Có tuyển Intern không?")
    followup_cues = [
        "o ha noi", "o tp", "o da nang", "co khong", "thi sao",
        "con o", "co tuyen", "nganh nay", "vi tri nay", "mang nay",
        "cong ty nay", "the con"
    ]
    is_explicit_new_search = norm.startswith(("tim viec", "viec lam", "tim job", "tim cong viec"))
    is_followup_refinement = (
        bool(prev_filters)
        and has_filter
        and not entities.get("category")
        and not entities.get("company")
        and not entities.get("skills")
        and (any(cue in norm for cue in followup_cues) or not is_explicit_new_search)
    )

    if has_filter or has_search_trigger:
        active_filters = {}

        if is_followup_refinement and not any(w in norm for w in ["tat ca", "moi nganh", "xoa loc"]):
            # Kế thừa nhóm ngành hoặc kỹ năng từ câu hỏi ngay trước đó
            if prev_filters.get("category"):
                active_filters["category"] = prev_filters["category"]
            elif prev_filters.get("skills") and not entities.get("skills"):
                active_filters["skills"] = prev_filters["skills"]
            if prev_filters.get("company"):
                active_filters["company"] = prev_filters["company"]

        # Ghi đè hoặc bổ sung các tiêu chí mới người dùng vừa nhập
        for key in [
            "category", "skills", "location", "level", "job_type",
            "no_experience", "min_salary", "max_salary", "salary_sort", "company"
        ]:
            val = entities.get(key)
            if val:
                active_filters[key] = val

        # Nếu người dùng hỏi "Ngành này ở Hà Nội có việc không?"
        if any(p in norm for p in ["nganh nay", "mang nay", "vi tri nay"]) and prev_filters.get("category"):
            active_filters["category"] = prev_filters["category"]

        return handle_job_search(active_filters, context, offset=0), context

    # -----------------------------------------------------
    # 11. HƯỚNG DẪN SỬ DỤNG WEBSITE IT CAREER MATCH
    # -----------------------------------------------------
    if any(
        kw in norm
        for kw in [
            "su dung website", "cach dung web", "it career match",
            "huong dan su dung", "chuc nang cua web", "web lam duoc gi"
        ]
    ):
        return {
            "reply": (
                "🚀 HƯỚNG DẪN SỬ DỤNG IT CAREER MATCH\n\n"
                "1. Tìm kiếm việc làm (`/jobs`): Tìm và lọc 70+ công việc IT theo ngành, địa điểm, mức lương, cấp độ (Intern/Fresher/Junior).\n"
                "2. Phân tích CV & Gợi ý việc làm (`/upload-cv` & `/recommendations`): Tải CV (PDF/DOCX) lên để AI dự đoán nhóm nghề, tính điểm Match Score và chỉ ra kỹ năng còn thiếu.\n"
                "3. Quản lý Hồ sơ (`/profile`): Cập nhật thông tin cá nhân và theo dõi kỹ năng.\n"
                "4. Trợ lý tìm việc (Chatbot): Hỏi đáp trực tiếp về các vị trí đang tuyển, mức lương, kỹ năng yêu cầu và lọc việc làm nhanh ngay trong khung chat."
            ),
            "actions": [
                {"label": "🔎 Trang Việc làm", "url": "/jobs"},
                {"label": "📄 Tải CV & Phân tích", "url": "/upload-cv"},
                {"label": "🎯 Gợi ý việc làm", "url": "/recommendations"},
            ],
            "suggestions": DEFAULT_SUGGESTIONS,
        }, context

    # -----------------------------------------------------
    # 12. CHÀO HỎI / CẢM ƠN / TẠM BIỆT / TRÒ CHUYỆN TỰ NHIÊN
    # -----------------------------------------------------
    if any(
         re.search(r"\b" + re.escape(kw) + r"\b", norm)
        for kw in ["xin chao", "chao", "hello", "hi", "hey", "alo", "chao bot", "chao ban"]
    ):
        user_name = get_user_first_name(user_id)
        greeting_name = f" {user_name}" if user_name else " bạn"
        return {
            "reply": (
                f"Xin chào{greeting_name}! 👋\n\n"
                "Mình là Trợ lý Tìm việc của IT Career Match. Mình có thể giúp bạn:\n"
                "• 🔎 Tìm kiếm việc làm thực tế đang mở trên hệ thống (theo ngành, kỹ năng Python/Java/React/SQL..., khu vực Hà Nội/TP.HCM/Đà Nẵng/Remote, mức lương).\n"
                "• 🎓 Tra cứu vị trí Thực tập sinh (Intern) và Fresher mới ra trường.\n"
                "• 💰 Xem thống kê mức lương và kỹ năng nhà tuyển dụng yêu cầu.\n"
                "• 📄 Hướng dẫn viết CV, chuẩn bị phỏng vấn và sử dụng công cụ Phân tích CV trên web.\n\n"
                "Bạn đang tìm công việc ở vị trí hay khu vực nào?"
            ),
            "actions": [
                {"label": "🔎 Xem tất cả việc làm", "url": "/jobs"},
                {"label": "📄 Phân tích CV trên web", "url": "/upload-cv"},
            ],
            "suggestions": DEFAULT_SUGGESTIONS,
        }, context

    if any(kw in norm for kw in ["cam on", "thank", "thanks", "tuyet voi", "hay qua", "ok bot"]):
        return {
            "reply": (
                "Rất vui vì đã hỗ trợ được bạn! 😊\n"
                "Nếu bạn muốn tìm thêm công việc ở vị trí khác, lọc theo mức lương/địa điểm "
                "hoặc xem chi tiết công việc nào thì cứ nhắn cho mình nhé!"
            ),
            "actions": [],
            "suggestions": DEFAULT_SUGGESTIONS,
        }, context

    if any(kw in norm for kw in ["tam biet", "bye", "goodbye", "hen gap lai"]):
        return {
            "reply": (
                "Tạm biệt bạn! 👋 Chúc bạn sớm tìm được công việc IT ưng ý trên IT Career Match nhé!"
            ),
            "actions": [],
            "suggestions": DEFAULT_SUGGESTIONS,
        }, context

    if any(kw in norm for kw in ["ban la ai", "bot la ai", "ban ten gi", "ban giup gi", "tro giup", "help"]):
        return {
            "reply": (
                "🤖 Mình là IT Career Assistant — trợ lý tra cứu việc làm và hỗ trợ ứng viên của IT Career Match.\n\n"
                "Bạn có thể hỏi mình những câu như:\n"
                "• «Tìm việc làm Backend ở Hà Nội»\n"
                "• «Có việc làm Thực tập / Fresher nào ở TP.HCM không?»\n"
                "• «Việc làm Python lương trên 12 triệu»\n"
                "• «Lương ngành Tester trên web khoảng bao nhiêu?»\n"
                "• «Đánh giá CV của mình» (Mình sẽ dẫn bạn tới công cụ Phân tích CV của web)"
            ),
            "actions": [{"label": "🔎 Mở trang Việc làm", "url": "/jobs"}],
            "suggestions": DEFAULT_SUGGESTIONS,
        }, context

    # -----------------------------------------------------
    # 13. FALLBACK THÔNG MINH (KHI CÂU HỎI CHƯA RÕ Ý ĐỊNH)
    # -----------------------------------------------------
    return {
        "reply": (
            "Mình chưa hiểu rõ yêu cầu của bạn. 🤔\n\n"
            "Hiện tại mình chuyên hỗ trợ **tra cứu & hỏi đáp việc làm thực tế** trên hệ thống IT Career Match. "
            "Bạn có thể thử hỏi mình:\n"
            "• Tìm việc theo ngành: «Tìm việc Backend / Frontend / AI / Data / Tester / Mobile / Game»\n"
            "• Tìm theo kỹ năng & địa điểm: «Việc làm Python ở Hà Nội», «Việc làm Remote»\n"
            "• Tìm theo cấp độ & lương: «Việc làm Thực tập / Fresher», «Việc làm lương trên 15 triệu»\n"
            "• Hoặc sử dụng chức năng «Phân tích CV & Gợi ý việc làm» trực tiếp trên web!"
        ),
        "actions": [
            {"label": "🔎 Tìm việc làm trên web", "url": "/jobs"},
            {"label": "📄 Phân tích CV bằng AI", "url": "/upload-cv"},
        ],
        "suggestions": DEFAULT_SUGGESTIONS,
    }, context
