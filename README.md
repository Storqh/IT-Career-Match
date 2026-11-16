# 🎯 IT Career Match

## Personalized Job Recommendation System for IT Students

**IT Career Match** là hệ thống web hỗ trợ sinh viên Công nghệ Thông tin phân tích CV, xác định nhóm nghề nghiệp phù hợp và gợi ý công việc IT dựa trên kỹ năng, nội dung CV và Machine Learning. Hệ thống kết hợp **Natural Language Processing (NLP)**, **Machine Learning**, **Content-Based Recommendation** và **Learning Resource Recommendation**.

---

## 🌐 Live Demo

**Website:** https://it-career-match.onrender.com

> Website được triển khai trên Render Free nên lần truy cập đầu tiên có thể cần thời gian để server khởi động (cold start ~30-60s).

---

## ✨ Chức năng chính

### 🎓 Student (Sinh viên)

#### 🔐 Authentication & Bảo mật
- **Đăng ký/Đăng nhập/Đăng xuất** với password hashing (Werkzeug)
- **Xác thực OTP qua email** (OTP 6 số, hết hạn 5 phút, giới hạn gửi lại 60s)
- **Quên mật khẩu / Đặt lại mật khẩu** qua liên kết email (Brevo API)
- **Session-based authentication** với role-based authorization (Student/Admin)

#### 👤 Quản lý hồ sơ (Profile)
- Xem và cập nhật: Họ tên, Ngày sinh, Ngành học, Trường ĐH, Năm tốt nghiệp, Giới thiệu bản thân
- Avatar tự động từ chữ cái đầu email
- Badge hiển thị vai trò (Sinh viên / Admin)

#### 📄 Phân tích CV (CV Analysis)
- **Upload CV**: PDF, DOCX (tối đa 5MB) với drag & drop
- **Nhập CV thủ công**: Dán text để AI trích xuất kỹ năng (fallback khi file lỗi)
- **Trích xuất kỹ năng**: TF-IDF + Dictionary matching từ 1000+ kỹ năng IT
- **Lưu trữ nhiều CV**: Quản lý, xem trước, xóa CV đã upload
- **Xem kỹ năng đã trích xuất** từ mỗi CV

#### 🤖 Dự đoán nghề nghiệp (Career Prediction)
- Phân loại CV thành **7 nhóm nghề**:
  - AI / Machine Learning
  - Backend Development
  - Cybersecurity
  - Data (Data Science / Analytics / Engineering)
  - DevOps / Cloud
  - Network / System
  - Other IT
- Model: **Logistic Regression + TF-IDF** (2000 features, n-gram 1-2)
- Accuracy: **83.64%** (46/55 test samples)

#### 🎯 Gợi ý việc làm (Job Recommendation)
- **Content-Based Filtering** với **Cosine Similarity** giữa CV skills và Job skills
- **Career Category Bonus**: +30 điểm nếu nhóm nghề dự đoán trùng khớp
- **Match Score** (0-100%): Kết hợp skill similarity + career bonus
- Hiển thị chi tiết:
  - Top-K việc làm phù hợp
  - Match Score & Skill Match %
  - **Matched Skills** (kỹ năng đã có)
  - **Missing Skills** (kỹ năng còn thiếu)
  - **Skill Gap Analysis** với giải thích chi tiết
  - **Recommendation Explanation** (tóm tắt lý do gợi ý)

#### 📚 Tài nguyên học tập (Learning Resources) - **MỚI**
- Gợi ý **khóa học/miễn phí** cho từng kỹ năng thiếu:
  - freeCodeCamp, Coursera (audit), YouTube, Official Docs, GitHub
  - Hỗ trợ tiếng Anh & tiếng Việt
  - Đã curate 60+ kỹ năng IT phổ biến
- **Learning Path** (Lộ trình học) tự động:
  - Phase 1: Cơ bản (Prerequisites)
  - Phase 2: Core Skills
  - Phase 3: Advanced / Integration
  - Ước lượng thời gian (tuần) cho từng phase

#### 💬 Chatbot Tư vấn (IT Career Assistant) - **CẬP NHẬT UI**
- Floating widget góc phải dưới
- Hỗ trợ: Tìm hiểu nhóm nghề IT, kỹ năng cần thiết, lộ trình học tập
- **Quick Reply Chips**: Viết CV IT, Học Backend, Học AI/ML, Phỏng vấn IT...
- Header hiện đại: Avatar robot + Title/Subtitle + Nút đóng
- Chat bubbles bo góc mềm mại, thanh cuộn mảnh 4px
- Nội dung chỉ mang tính tham khảo

#### 🔍 Tìm kiếm việc làm (Job Search)
- Tìm kiếm từ khóa (title, company, skills, description)
- **Bộ lọc nâng cao**: Nhóm nghề, Địa điểm, Loại hình (Full-time/Part-time/Intern/Remote), Cấp bậc, Mức lương
- Sắp xếp: Mới nhất, Match Score, Lương
- Phân trang, lưu việc làm yêu thích (Favourites)

#### 📋 Đơn ứng tuyển (Applications)
- Nộp đơn với CV đã upload
- Theo dõi trạng thái: Chờ duyệt / Đã nhận / Đã từ chối
- Xem chi tiết đơn ứng tuyển

---

### 🛡️ Admin Management

#### 📊 Dashboard Admin
- **Thống kê tổng quan**: Users, Jobs, Applications, New Users (7 ngày)
- Biểu đồ: User mới theo tuần/tháng, Jobs theo Category/Location
- Thao tác nhanh: Đăng tin, Quản lý users, Duyệt đơn, Báo cáo, Xuất CSV/Excel

#### 👥 Quản lý Users
- Danh sách có tìm kiếm, lọc (Role: Student/Admin, Status: Verified/Unverified)
- Xem chi tiết: Profile, Skills, CVs, Applications, Favourites
- **Tạo user mới** (Admin có thể tạo cả Admin khác)
- **Sửa user**: Thông tin, Role, Major, Verified status
- **Đổi Role** Student ↔ Admin (Admin không tự hạ quyền/xóa chính mình)
- **Xóa user** (có xác nhận, bảo vệ dữ liệu liên quan)

#### 💼 Quản lý Tin tuyển dụng (Jobs)
- CRUD đầy đủ: Tạo, Sửa, Xem, Xóa, Toggle Active/Inactive
- Form kỹ năng: Checkbox multi-select từ database skills
- Lọc: Active/Inactive/All

#### 📝 Quản lý Đơn ứng tuyển
- Duyệt/Từ chối đơn (Pending → Accepted/Rejected)
- Lọc theo trạng thái
- Xem CV ứng viên, thông tin việc làm

#### 📈 Báo cáo & Phân tích (Analytics)
- Jobs theo Category / Location / Level / Job Type / Month
- Applications theo Status / Month
- Top Skills được yêu cầu
- Career Distribution
- User Growth

#### ⚙️ Cài đặt hệ thống (Settings)
- **Email (Brevo)**: API Key, Sender Email, Sender Name
- **Hệ thống**: Site Name, Maintenance Mode, Default Language, Max File Upload, Session Timeout
- **AI/ML**: Model Version, Confidence Threshold, Top-K Recommendations, Enable Career Bonus, Bonus Points
- Lưu vào database, áp dụng ngay không cần restart

#### 📤 Xuất dữ liệu (Export)
- **Excel**: `IT_Career_Match_Admin_Data.xlsx` (Users, Jobs, Applications, Recommendations)
- **CSV riêng biệt**: Users, Jobs
- **Bảo mật**: Không xuất password, password hash

---

## 🧠 Machine Learning

### Dataset
Dataset ban đầu 289 samples. Sau xử lý: **275 samples, 7 classes**.

| Career Category | Samples |
|---|---:|
| Other IT | 99 |
| DevOps / Cloud | 49 |
| Network / System | 36 |
| Data | 35 |
| Backend | 22 |
| Cybersecurity | 19 |
| AI / ML | 15 |
| **Total** | **275** |

### Pipeline
```text
Career Dataset
      ↓
Text Preprocessing (lowercase, remove special chars, tokenize)
      ↓
TF-IDF Vectorization (max_features=2000, ngram_range=(1,2))
      ↓
Train / Test Split (80/20)
      ↓
Logistic Regression (class_weight=balanced, max_iter=1000)
      ↓
Career Classification
      ↓
Model Evaluation
```

### Model Performance
| Metric | Score |
|---|---:|
| Accuracy | 83.64% |
| Precision (Weighted) | 83.94% |
| Recall (Weighted) | 83.64% |
| F1-Score (Weighted) | 83.43% |

---

## 🎯 Recommendation Algorithm

```text
Student CV
    ↓
Extract Skills (TF-IDF + Dictionary)
    ↓
Career Prediction (Logistic Regression)
    ↓
Load Job Database
    ↓
TF-IDF Vectorization (Job skills)
    ↓
Cosine Similarity (CV skills vs Job skills)
    ↓
Career Category Bonus (+30 if match)
    ↓
Match Score = Skill Similarity + Career Bonus
    ↓
Job Ranking → Top-K
```

### Skill Gap Analysis
- **Matched Skills**: Kỹ năng sinh viên đã có khớp yêu cầu việc làm
- **Missing Skills**: Kỹ năng yêu cầu mà sinh viên chưa có
- **Recommendation Explanation**: Tóm tắt lý do gợi ý (Career match, Skill match %, Similarity)

### Learning Resources Integration
- Mỗi Missing Skill → Gợi ý 3-5 tài nguyên học miễn phí
- **Learning Path**: Tự động sắp xếp theo prerequisite dependencies
  - Ví dụ: React → cần JavaScript + HTML/CSS trước
  - Docker → cần Linux cơ bản
  - Kubernetes → cần Docker + Linux

---

## 🏗️ System Architecture

```text
Web Browser (HTML5 / CSS3 / Bootstrap 5 / JavaScript ES6 / Jinja2)
                         |
                         v
                   Flask Backend (Blueprints)
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      PostgreSQL    CV Processing    AI / ML Module
      Database      PDF / DOCX       TF-IDF + Logistic Regression
                    Text Extraction  Career Classification
                    Skill Extraction |
                                          v
                                 Recommendation Engine
                                 Content-Based Filtering
                                 Cosine Similarity
                                 Match Score / Skill Gap
                                 Recommendation Explanation
                                 Learning Resources
```

---

## 🗄️ Database (PostgreSQL)

**Bảng chính:**
```text
users                 - Tài khoản (email, password_hash, role, is_verified)
student_profiles      - Hồ sơ (full_name, dob, major, university, graduation_year, bio)
cvs                   - CV (filename, filepath, extracted_text, extracted_skills JSON, created_at)
skills                - Danh mục kỹ năng (skill_id, skill_name, category)
student_skills        - Kỹ năng user (user_id, skill_id, proficiency)
jobs                  - Tin tuyển dụng (title, company, location, category, level, salary, description, requirements, benefits, status)
job_skills            - Kỹ năng yêu cầu việc làm (job_id, skill_id, is_required)
recommendations       - Kết quả gợi ý (user_id, job_id, match_score, skill_match, career_match, matched_skills, missing_skills, explanation)
favourites            - Việc làm yêu thích (user_id, job_id)
applications          - Đơn ứng tuyển (user_id, job_id, cv_id, status, applied_at)
admin_settings        - Cài đặt hệ thống (key, value, description)
```

---

## 🎨 UI/UX Features (v1.5 - Latest)

### Sidebar Navigation
- **3-Zone Layout**: Sidebar (fixed) + Header (sticky) + Main Content
- **Collapse/Expand**: Toggle button với smooth transition (260px ↔ 72px)
- **State Persistence**: localStorage, default EXPANDED, anti-flicker script
- **Custom Dark Scrollbar**: 4px width, `rgba(255,255,255,0.15)` thumb
- **No Horizontal Scroll**: `overflow-x: hidden` trên sidebar & nav
- **Collapsed State**: Centered icons, `display:none` labels, tooltip titles, repositioned toggle (right:-12px, border-radius:50%), centered footer avatar/logout
- **Responsive**: Mobile drawer (<992px), backdrop overlay

### Chatbot Widget
- Floating button (bottom-right), animated open/close
- **Header**: Flex layout (Avatar+Title left | Close right), online status dot
- **Messages**: Clean white bg, modern chat bubbles (`#f1f5f9`, radius 16px, max-width 85%), bot avatar 28px
- **Fixed Indentation Bug**: `white-space: normal` (không còn `pre-wrap`)
- **Thin Scrollbar**: 4px, `rgba(0,0,0,0.15)`
- **Quick Reply Chips**: `flex-wrap: wrap`, pill shape (9999px), 12.5px font, không bị cắt mép

### Alert System
- Standardized Bootstrap 5 alerts với **inline SVG close button (16px)**
- Global CSS safeguard: `.alert .btn-close { width: 16px !important; height: 16px !important; }`
- Applied across 12 templates (auth, dashboard, admin, CV, profile)

### Dashboard Cards
- Student Dashboard: 3-column layout (Profile, Skills, CV) với `.card.h-100`
- Proper `.card-header` + `.card-body` structure
- Flash messages at top of content area

---

## 🐳 Docker & Docker Compose

### Requirements
- Git
- Docker Desktop (Engine running)
- Docker Compose (built-in)

### Run with Docker Compose

**1. Clone repository**
```bash
git clone https://github.com/Storqh/IT-Career-Match.git
cd IT-Career-Match
```

**2. Tạo file môi trường**
```powershell
# Windows PowerShell
Copy-Item .env.example .env
```
```bash
# macOS / Linux
cp .env.example .env
```
Mở `.env` và điền các giá trị thực tế (không dùng mẫu cho production).

**3. Build và khởi chạy**
```bash
docker compose up -d --build
```

**4. Kiểm tra & Logs**
```bash
docker compose ps
docker compose logs -f
docker compose logs -f <service>  # Xem log 1 service
```

**5. Truy cập ứng dụng**
```
http://localhost:5000
```
(Port tùy cấu hình `ports` trong `compose.yaml`)

### Docker Commands Cheatsheet
```bash
# Khởi động
docker compose up -d

# Build lại + chạy
docker compose up -d --build

# Kiểm tra container
docker compose ps

# Xem log real-time
docker compose logs -f

# Dừng (giữ volume data)
docker compose down

# Dừng VÀ xóa volume (MẤT DATA DATABASE)
docker compose down -v
```

> ⚠️ **Lưu ý data**: PostgreSQL dùng Docker volume. `down` không xóa volume. Chỉ dùng `down -v` khi chắc chắn muốn reset database.

---

## 📁 Project Structure

```text
IT-Career-Match/
├── app.py                      # Flask app factory
├── requirements.txt
├── README.md
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .env.example
├── .gitignore
├── ai/                         # AI/ML Modules
│   ├── __init__.py
│   ├── career_classifier.py    # Logistic Regression + TF-IDF
│   ├── cv_parser.py            # PDF/DOCX text extraction
│   ├── embeddings_cache.py     # Skill embeddings cache
│   ├── explanation.py          # Recommendation explanations
│   ├── learning_resources.py   # Learning resource recommender (NEW)
│   ├── match_score.py          # Match score calculator
│   ├── ranking.py              # Job ranking logic
│   ├── recommender.py          # Main recommendation engine
│   ├── skill_extractor.py      # Skill extraction from text
│   ├── skill_gap.py            # Skill gap analysis
│   ├── skill_matcher.py        # Hybrid skill matching
│   └── text_preprocessing.py   # Text cleaning, tokenization
├── app/
│   └── routes/                 # Flask Blueprints
│       ├── __init__.py
│       ├── admin.py            # Admin routes
│       ├── auth.py             # Auth routes
│       ├── chatbot.py          # Chatbot API
│       ├── cv.py               # CV routes
│       ├── jobs.py             # Job search/routes
│       └── profile.py          # Profile routes
├── database/
│   └── database.py             # PostgreSQL connection pool
├── data/
│   ├── career_dataset.csv
│   ├── career_ml_dataset.csv
│   ├── jobs.csv
│   └── seed_jobs.py
├── models/
│   ├── career_classifier.joblib
│   ├── tfidf_vectorizer.joblib
│   ├── skill_embeddings.npy
│   └── skill_names.json
├── static/
│   ├── css/
│   │   ├── pro-ui.css          # Main design system
│   │   └── chatbot.css         # Chatbot widget styles
│   └── js/
│       ├── main.js
│       ├── pro-ui.js           # Sidebar, toggle, utils
│       ├── auth.js
│       └── chatbot.js          # Chatbot logic
├── templates/
│   ├── base.html
│   ├── layouts/
│   │   ├── auth.html           # Auth pages layout
│   │   ├── dashboard.html      # Dashboard layout (3-zone)
│   │   └── public.html         # Public pages layout
│   ├── components/
│   │   ├── app_header.html     # Top header
│   │   ├── app_sidebar.html    # Sidebar nav
│   │   ├── chatbot.html        # Chatbot widget
│   │   ├── page_header.html
│   │   └── ui_macros.html      # Jinja2 macros
│   ├── admin/                  # Admin templates
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── add_user.html
│   │   ├── edit_user.html
│   │   ├── user_detail.html
│   │   ├── jobs.html
│   │   ├── job_form.html
│   │   ├── applications.html
│   │   ├── analytics.html
│   │   └── settings.html
│   ├── dashboard.html          # Student dashboard
│   ├── profile.html
│   ├── edit_profile.html
│   ├── upload_cv.html
│   ├── parse_text.html         # Manual CV input
│   ├── my_cvs.html
│   ├── view_cv.html
│   ├── recommendations.html    # Job recommendations
│   ├── gap_analysis.html       # Skill gap detail
│   ├── jobs.html
│   ├── job_detail.html
│   ├── my_favourites.html
│   ├── my_applications.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── verify_otp.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
├── uploads/                    # CV uploads (gitignored)
└── tests/
    └── test_recommendation_fix.py
```

---

## 🛠️ Technologies

| Category | Stack |
|---|---|
| **Backend** | Python 3.10+, Flask, PostgreSQL, psycopg2, Gunicorn |
| **Machine Learning** | scikit-learn, pandas, NumPy, TF-IDF, Logistic Regression, Cosine Similarity, joblib |
| **CV Processing** | pypdf (PDF), python-docx (DOCX) |
| **Frontend** | HTML5, CSS3 (Custom Properties), Bootstrap 5.3, Bootstrap Icons, Vanilla JS ES6, Jinja2 |
| **Email** | Brevo (Sendinblue) API |
| **Export** | openpyxl (Excel), csv |
| **Dev/Deploy** | Git, GitHub, Docker, Docker Compose, Render |

---

## 🚀 Run Locally Without Docker

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally

### Steps
```bash
# 1. Clone
git clone https://github.com/Storqh/IT-Career-Match.git
cd IT-Career-Match

# 2. Virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment (.env)
# Tham khảo .env.example, điền:
# SECRET_KEY, DATABASE_URL, BREVO_API_KEY, v.v.
# Tạo secret key:
python -c "import secrets; print(secrets.token_hex(32))"

# 5. Run
python app.py
```
Mở: `http://127.0.0.1:5000`

---

## 🔒 Security

- ✅ Password hashing (Werkzeug `generate_password_hash`/`check_password_hash`)
- ✅ Session-based authentication với secure cookies
- ✅ Role-based authorization (Student/Admin decorators)
- ✅ Admin route protection (`@admin_required`)
- ✅ OTP email verification (5min expiry, 60s resend cooldown)
- ✅ File validation: Extension (PDF/DOCX), Size (5MB), Secure filename
- ✅ Environment variables cho secrets (`.env` gitignored)
- ✅ Không export password/hash trong Admin Export
- ✅ SQL parameterized queries (psycopg2)

---

## ⚠️ Current Limitations

- Dataset ML nhỏ (275 samples), một số class ít data (AI/ML: 15, Cybersecurity: 19)
- Skill Extraction chủ yếu dictionary-based (chưa dùng NER/Transformer)
- Recommendation: Content-based only (chưa có Collaborative/Hybrid)
- Render Free tier: Cold start ~30-60s, sleep sau 15p idle
- Cần persistent storage cho file uploads & database khi production
- Chưa có automated testing / CI/CD pipeline

---

## 🔮 Future Development

- [ ] REST API cho frontend SPA / mobile
- [ ] Semantic Embeddings (Sentence Transformers / BERT)
- [ ] Transformer-based NLP cho skill extraction
- [ ] Collaborative Filtering + Hybrid Recommendation
- [ ] Job API Integration (LinkedIn, VietnamWorks, TopCV...)
- [ ] CV Scoring & ATS Optimization
- [ ] Learning Path Recommendation nâng cao
- [ ] Skill / Course Recommendation personalization
- [ ] Advanced Admin Analytics (charts, cohorts)
- [ ] Cloud File Storage (AWS S3, Cloudinary)
- [ ] Automated Testing (pytest) + CI/CD (GitHub Actions)
- [ ] Chatbot RAG (truy xuất real-time jobs/skills từ DB)

---

## 🎓 Project Purpose

Dự án được xây dựng nhằm nghiên cứu và áp dụng:
- **Machine Learning** (Classification, Similarity, Recommendation)
- **Natural Language Processing** (Text preprocessing, TF-IDF, Skill extraction)
- **Recommendation Systems** (Content-based, Skill Gap, Explanation)
- **Web Development** (Flask, Jinja2, Bootstrap, Modern CSS/JS)
- **Database Design** (PostgreSQL, Relational schema, Migrations)
- **Software Engineering** (Clean architecture, Blueprints, Modular AI)
- **Scrum & Deployment** (Docker, Render, Git workflow)

> **Gợi ý việc làm cá nhân hóa cho sinh viên Công nghệ Thông tin dựa trên CV, kỹ năng và Machine Learning.**

---

## 👨‍💻 Author

**Nhóm 4**  
GitHub: [Storqh](https://github.com/Storqh)

**IT Career Match — Personalized Job Recommendation System for IT Students**

---

## 📄 License

Dự án được xây dựng phục vụ mục đích học tập và nghiên cứu.