# 🎯 IT Career Match
## Personalized Job Recommendation System for IT Students

IT Career Match là hệ thống web hỗ trợ sinh viên Công nghệ Thông tin phân tích CV, xác định nhóm nghề nghiệp phù hợp và gợi ý các công việc IT dựa trên kỹ năng, nội dung CV và Machine Learning.

Hệ thống kết hợp **Natural Language Processing (NLP)**, **Machine Learning** và **Content-Based Recommendation** để phân tích hồ sơ sinh viên và đưa ra các gợi ý việc làm phù hợp.

---

## 🌐 Live Demo

**Website:**  
https://it-career-match.onrender.com

> Website được triển khai trên Render Free nên lần truy cập đầu tiên có thể cần một khoảng thời gian để server khởi động.

---

# ✨ Chức năng chính

## 👨‍🎓 Student

### 🔐 Authentication

- Đăng ký tài khoản
- Đăng nhập / đăng xuất
- Mã hóa mật khẩu
- Xác thực OTP qua email
- OTP có thời hạn 5 phút
- Giới hạn thời gian gửi lại OTP

### 👤 Profile Management

Sinh viên có thể:

- Xem hồ sơ cá nhân
- Cập nhật họ tên
- Cập nhật ngày sinh
- Cập nhật ngành học
- Cập nhật giới thiệu bản thân

### 📄 CV Analysis

Hệ thống hỗ trợ:

- Upload CV PDF
- Upload CV DOCX
- Kiểm tra định dạng file
- Trích xuất nội dung CV
- Tiền xử lý văn bản
- Trích xuất kỹ năng
- Lưu thông tin CV

### 🤖 Career Prediction

Quy trình:

```text
CV
↓
Text Preprocessing
↓
TF-IDF
↓
Logistic Regression
↓
Career Category
```

Mô hình hiện phân loại **7 nhóm nghề chính**:

1. AI / Machine Learning
2. Backend Development
3. Cybersecurity
4. Data
5. DevOps / Cloud
6. Network / System
7. Other IT

### 💼 Job Recommendation

Hệ thống sử dụng:

**Content-Based Filtering + Cosine Similarity**

để so sánh hồ sơ sinh viên với dữ liệu công việc.

Kết quả bao gồm:

- Career Prediction
- Top-K công việc phù hợp
- Match Score
- Matched Skills
- Missing Skills
- Skill Gap Analysis
- Recommendation Explanation

### 🔎 Job Search

Sinh viên có thể:

- Xem danh sách việc làm
- Xem chi tiết công việc
- Tìm kiếm theo từ khóa
- Lọc theo nhóm nghề
- Lọc theo địa điểm
- Lọc theo loại công việc
- Lọc theo kinh nghiệm
- Lọc theo cấp độ
- Lọc theo mức lương
- Sắp xếp kết quả
- Phân trang

---

# 🛡️ Admin Management

Hệ thống có khu vực quản trị riêng dành cho tài khoản có role `admin`.

## 📊 Admin Dashboard

Admin có thể theo dõi:

- Tổng số người dùng
- Tổng số sinh viên
- Tổng số Admin
- Tổng số công việc
- Tổng số CV
- Tổng số Application
- Người dùng đăng ký gần đây

## 👥 User Management

Admin có thể:

- Xem danh sách người dùng
- Tìm kiếm người dùng
- Lọc theo role
- Xem chi tiết tài khoản
- Tạo tài khoản mới
- Sửa thông tin người dùng
- Thay đổi role Student / Admin
- Xóa tài khoản
- Không cho Admin tự xóa tài khoản đang đăng nhập
- Không cho Admin tự hạ quyền chính mình

Tài khoản được Admin tạo trực tiếp không cần xác thực OTP.

## 💼 Job Management

Admin có thể:

- Thêm công việc
- Sửa công việc
- Xóa công việc
- Xem chi tiết công việc
- Quản lý trạng thái công việc

Thông tin Job bao gồm:

- Job Title
- Company
- Location
- Job Type
- Career Category
- Description
- Requirements
- Benefits
- Skills
- Salary
- Experience
- Level
- Deadline
- Source
- Status

## 📊 Export Data

Admin có thể xuất dữ liệu hệ thống thành file Excel:

```text
IT_Career_Match_Admin_Data.xlsx
```

File Excel gồm các sheet:

- Users
- Jobs
- Applications
- Recommendations

Password và password hash **không được xuất**.

---

# 🧠 Machine Learning

## Dataset

Dataset ban đầu:

```text
289 job-role samples
```

Sau quá trình xử lý và loại bỏ các nhóm nghề có quá ít dữ liệu, dataset dùng để train gồm:

```text
275 samples
7 classes
```

| Career Category | Samples |
|---|---:|
| Other IT | 99 |
| DevOps / Cloud | 49 |
| Network / System | 36 |
| Data | 35 |
| Backend | 22 |
| Cybersecurity | 19 |
| AI / ML | 15 |

---

# ⚙️ Machine Learning Pipeline

```text
Career Dataset
↓
Text Preprocessing
↓
TF-IDF Vectorization
↓
Train / Test Split
↓
Logistic Regression
↓
Career Classification
↓
Model Evaluation
```

### TF-IDF

```python
max_features = 2000
ngram_range = (1, 2)
```

### Logistic Regression

```text
class_weight = balanced
max_iter = 1000
```

### Train / Test Split

```text
80% Training
20% Testing
```

---

# 📈 Model Performance

| Metric | Score |
|---|---:|
| Accuracy | 83.64% |
| Precision (Weighted) | 83.94% |
| Recall (Weighted) | 83.64% |
| F1-Score (Weighted) | 83.43% |

Kết quả Accuracy:

```text
46 / 55 test samples
= 83.64%
```

---

# 🎯 Recommendation Algorithm

Sau khi dự đoán nhóm nghề, hệ thống sử dụng Recommendation Engine để xếp hạng công việc.

```text
Student CV
↓
Extract Skills
↓
Career Prediction
↓
Load Job Database
↓
TF-IDF Vectorization
↓
Cosine Similarity
↓
Career Category Bonus
↓
Match Score
↓
Job Ranking
↓
Top-K Jobs
```

## Match Score

Công thức hiện tại:

```text
Match Score =
Cosine Similarity × 70
+
Career Category Bonus × 30
```

Nếu Career Category của công việc trùng với Career Prediction:

```text
Career Category Bonus = 30
```

---

# 🧩 Skill Gap Analysis

Hệ thống so sánh:

```text
Student Skills
VS
Job Required Skills
```

để tìm:

```text
Matched Skills
Missing Skills
```

Ví dụ:

```text
Student Skills:
Python
Flask
SQL
Git

Job Required Skills:
Python
Flask
SQL
Docker
AWS

Matched Skills:
Python
Flask
SQL

Missing Skills:
Docker
AWS
```

Nhờ đó sinh viên có thể biết những kỹ năng còn thiếu để cải thiện hồ sơ.

---

# 💡 Recommendation Explanation

Ngoài Match Score, hệ thống tạo giải thích recommendation dựa trên:

- Nhóm nghề được dự đoán
- Kỹ năng phù hợp
- Kỹ năng còn thiếu
- Độ tương đồng giữa CV và Job
- Nội dung công việc

Điều này giúp người dùng hiểu **vì sao một công việc được đề xuất** thay vì chỉ nhận một con số Match Score.

---

# 🏗️ System Architecture

```text
┌─────────────────────────────┐
│         Web Browser         │
│ HTML / CSS / Bootstrap / JS │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        Flask Backend        │
│                             │
│ Authentication              │
│ Profile Management          │
│ CV Management               │
│ Job Management              │
│ Admin Management            │
└───────┬─────────┬───────────┘
        │         │
        │         ▼
        │   ┌─────────────────┐
        │   │ SQLite Database │
        │   └─────────────────┘
        │
        ▼
┌─────────────────────────────┐
│     CV Processing Module    │
│ PDF / DOCX Parser           │
│ Text Preprocessing          │
│ Skill Extraction            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        AI / ML Module       │
│ TF-IDF                      │
│ Logistic Regression         │
│ Career Classification       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Recommendation Engine     │
│ Content-Based Filtering     │
│ Cosine Similarity           │
│ Match Score                 │
│ Skill Gap                   │
│ Explanation                 │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Recommendation Results    │
│ Career Prediction           │
│ Top-K Jobs                  │
│ Match Score                 │
│ Skill Gap                   │
│ Explanation                 │
└─────────────────────────────┘
```

---

# 🗄️ Database

Hệ thống sử dụng **SQLite**.

Các bảng chính:

```text
users
student_profiles
cvs
skills
student_skills
jobs
job_skills
recommendations
favourites
applications
```

Database lưu trữ:

- Tài khoản
- Hồ sơ sinh viên
- CV
- Kỹ năng
- Công việc
- Recommendation
- Favourite
- Application

---

# 📁 Project Structure

```text
IT-Career-Match/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── ai/
│   ├── __init__.py
│   ├── career_classifier.py
│   ├── cv_parser.py
│   ├── explanation.py
│   ├── match_score.py
│   ├── recommender.py
│   ├── skill_extractor.py
│   ├── skill_gap.py
│   └── text_preprocessing.py
│
├── data/
│   ├── career_dataset.csv
│   ├── career_ml_dataset.csv
│   ├── career_preprocessed.csv
│   ├── jobs.csv
│   ├── seed_jobs.py
│   └── upgrade_jobs_database.py
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── it_career_match.db
│
├── models/
│   ├── career_classifier.joblib
│   └── tfidf_vectorizer.joblib
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── user_detail.html
│   │   ├── add_user.html
│   │   └── edit_user.html
│   │
│   ├── base.html
│   ├── dashboard.html
│   ├── index.html
│   ├── jobs.html
│   ├── job_detail.html
│   ├── login.html
│   ├── profile.html
│   ├── recommendations.html
│   ├── register.html
│   ├── result.html
│   ├── upload_cv.html
│   └── verify_otp.html
│
└── uploads/
    └── .gitkeep
```

---

# 🛠️ Technologies

## Backend

- Python
- Flask
- SQLite

## Machine Learning

- scikit-learn
- pandas
- NumPy
- TF-IDF
- Logistic Regression
- Cosine Similarity

## CV Processing

- pypdf
- python-docx

## Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript
- Jinja2

## Other

- Werkzeug
- joblib
- openpyxl
- requests
- python-dotenv
- Gunicorn
- Brevo Email API

## Deployment

- Git
- GitHub
- Render

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/Storqh/IT-Career-Match.git

cd IT-Career-Match
```

## 2. Create Virtual Environment

Windows:

```bash
python -m venv .venv

.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Environment Variables

Tạo file:

```text
.env
```

Nội dung:

```env
SECRET_KEY=your_secret_key
BREVO_API_KEY=your_brevo_api_key
```

> Không commit `.env`, API key hoặc Secret Key lên GitHub.

## 5. Run Application

```bash
python app.py
```

Truy cập:

```text
http://127.0.0.1:5000
```

---

# 📦 Main Dependencies

```text
Flask
pandas
numpy
scikit-learn
pypdf
python-docx
joblib
gunicorn
requests
python-dotenv
openpyxl
```

---

# 🔒 Security

Hệ thống hiện áp dụng:

- Password hashing
- Session-based authentication
- Role-based authorization
- Admin route protection
- OTP email verification
- OTP expiration
- OTP resend cooldown
- File extension validation
- File upload size limit
- Secure filename handling
- Environment variables cho Secret/API Key
- Không export password hash

---

# ⚠️ Current Limitations

Phiên bản hiện tại vẫn có một số giới hạn:

- Dataset Machine Learning còn tương đối nhỏ
- Một số nhóm nghề có quá ít dữ liệu nên chưa được đưa vào classifier chính
- Skill Extraction chủ yếu dựa trên danh sách kỹ năng đã định nghĩa
- Recommendation chủ yếu dựa trên nội dung CV và thông tin công việc
- SQLite phù hợp với demo/đồ án hơn hệ thống production lớn
- Render Free có thể sleep khi không có request
- File/database local trên môi trường deploy miễn phí chưa phù hợp cho lưu trữ production lâu dài

---

# 🔮 Future Development

Hệ thống có thể tiếp tục phát triển:

- PostgreSQL
- REST API
- Semantic Embeddings
- Sentence Transformers
- Transformer-based NLP
- Collaborative Filtering
- Hybrid Recommendation
- Job API Integration
- CV Scoring
- Learning Path Recommendation
- Skill/Course Recommendation
- Advanced Admin Analytics
- Cloud File Storage
- Docker
- Automated Testing
- CI/CD

---

# 🎓 Project Purpose

Dự án được xây dựng nhằm nghiên cứu và áp dụng:

- Machine Learning
- Natural Language Processing
- Recommendation System
- Web Development
- Database Design
- Software Engineering
- Scrum
- Deployment

Đề tài tập trung giải quyết bài toán:

> **Gợi ý việc làm cá nhân hóa cho sinh viên Công nghệ Thông tin dựa trên CV, kỹ năng và Machine Learning.**

---

# 👨‍💻 Author

**Trần Quốc Huy**

GitHub: **Storqh**

Project:

**IT Career Match – Personalized Job Recommendation System for IT Students**

---

# 📄 License

Dự án được xây dựng phục vụ mục đích **học tập và nghiên cứu**.