# 🎯 IT Career Match

## Personalized Job Recommendation System for IT Students

**IT Career Match** là hệ thống gợi ý việc làm cá nhân hóa dành cho sinh viên Công nghệ Thông tin.

Hệ thống kết hợp **Machine Learning**, **Natural Language Processing (NLP)** và **Recommendation System** để phân tích CV, trích xuất kỹ năng, dự đoán định hướng nghề nghiệp và đề xuất những công việc phù hợp với hồ sơ của sinh viên.

---

## 🌐 Live Demo

👉 https://it-career-match.onrender.com

> Website được triển khai trên Render Free. Lần truy cập đầu tiên có thể cần một khoảng thời gian ngắn để server khởi động.

---

# ✨ Main Features

## 👨‍🎓 Student

### Account
- Đăng ký tài khoản
- Xác thực email bằng OTP
- Gửi OTP bằng Brevo Transactional Email API
- OTP có thời gian hết hạn
- Đăng nhập / đăng xuất
- Quản lý hồ sơ cá nhân

### CV Analysis
- Upload CV định dạng PDF
- Upload CV định dạng DOCX
- Tự động đọc nội dung CV
- Text preprocessing
- Skill extraction
- Lưu thông tin kỹ năng sinh viên

### AI Career Prediction
- Phân tích nội dung CV
- Chuyển CV thành TF-IDF Vector
- Dự đoán nhóm nghề nghiệp bằng Logistic Regression

### Job Recommendation
- Content-Based Recommendation
- Cosine Similarity
- Match Score
- Skill Gap Analysis
- Recommendation Explanation
- Top-K Job Recommendations

### Job Search

Hệ thống Job đang được mở rộng với:

- 🔍 Search theo tên công việc
- 🏢 Search theo công ty
- 🧠 Search theo kỹ năng
- 📂 Filter theo Career Category
- 📍 Filter theo Location
- 💰 Filter theo Salary
- 💼 Filter theo Experience
- 🕒 Filter theo Job Type
- 🎯 Filter theo Job Level
- Pagination

---

# 💼 Job Information

Mỗi công việc trong hệ thống được thiết kế với các thông tin:

```text
Job Title
Company
Description
Requirements
Benefits
Required Skills
Location
Salary
Experience
Job Type
Job Level
Career Category
Application Deadline
Status
Source
Created At
```

Trang chi tiết công việc dự kiến hiển thị:

```text
Job Information
      ↓
Company
      ↓
Job Description
      ↓
Requirements
      ↓
Required Skills
      ↓
Benefits
      ↓
Salary / Location
      ↓
Application Deadline
      ↓
AI Match Score
      ↓
Skill Gap
      ↓
Recommendation Explanation
```

---

# 🏢 Job Categories

Hệ thống Job được mở rộng theo nhiều nhóm nghề CNTT:

- AI / Machine Learning
- Data
- Backend Development
- Frontend Development
- Full Stack Development
- DevOps / Cloud
- Cybersecurity
- Network / System
- Software Testing / QA
- Mobile Development
- Game Development
- Other IT

Mục tiêu dataset Job sau khi mở rộng là khoảng **60 công việc demo** thuộc nhiều nhóm nghề khác nhau.

> Career Prediction Model hiện tại được huấn luyện trên 7 nhóm nghề chính. Số lượng Job Category có thể lớn hơn số class của Machine Learning Model.

---

# 👨‍💼 Admin System

Admin Dashboard đang được mở rộng để hỗ trợ quản trị toàn bộ hệ thống.

## 📊 Admin Dashboard

Dashboard dự kiến hiển thị:

- Total Users
- Total Students
- Total Admins
- Total Jobs
- Total CVs
- Total Applications
- Total Recommendations
- Career Category Statistics
- Average Match Score

---

## 👥 User Management

Admin có thể:

- Xem danh sách người dùng
- Search User
- Filter User
- Xem chi tiết User
- Thêm User
- Sửa User
- Xóa User
- Thay đổi Role

Role hiện tại:

```text
student
admin
```

Admin có thể xem:

```text
User
 ├── Profile
 ├── Skills
 ├── CV
 ├── Recommendations
 └── Applications
```

Thông tin nhạy cảm như **password hash không được hiển thị hoặc export**.

---

## 💼 Job Management

Admin có thể:

- Add Job
- Edit Job
- Delete Job
- View Job
- Search Job
- Filter Job
- Active / Inactive Job
- Quản lý Category
- Quản lý Skills
- Export Job Data

Admin Search & Filter:

```text
Keyword
Company
Category
Location
Salary
Experience
Job Type
Level
Status
```

---

# 📥 Data Export

Admin Dashboard dự kiến hỗ trợ export dữ liệu.

### CSV

Có thể export:

- Users
- Jobs
- Applications
- Recommendations

### Excel

Excel Workbook có thể gồm:

```text
IT_Career_Match_Report.xlsx

├── Users
├── Jobs
├── Applications
└── Recommendations
```

Chức năng này giúp Admin dễ:

- Thống kê dữ liệu
- Tổng hợp kết quả
- Làm báo cáo
- Phân tích người dùng
- Phân tích việc làm

---

# 🤖 Machine Learning

## Career Prediction

Pipeline:

```text
CV
 ↓
Extract Text
 ↓
Text Preprocessing
 ↓
TF-IDF
 ↓
Logistic Regression
 ↓
Career Prediction
```

### Model

```text
Algorithm:
Logistic Regression

Feature Extraction:
TF-IDF

Maximum Features:
2000

N-gram:
(1, 2)

Train/Test:
80/20
```

---

## 📊 Model Results

| Metric | Score |
|---|---:|
| Accuracy | 83.64% |
| Precision | 83.94% |
| Recall | 83.64% |
| F1-Score | 83.43% |

---

# 🎯 ML Career Classes

Machine Learning Model hiện hỗ trợ 7 class:

1. AI / Machine Learning
2. Backend Development
3. Cybersecurity
4. Data
5. DevOps / Cloud
6. Network / System
7. Other IT

Training dataset cuối:

```text
275 samples
7 classes
2000 TF-IDF features
```

---

# 🧠 Recommendation System

Recommendation Engine sử dụng:

```text
Content-Based Filtering
        +
Cosine Similarity
        +
Career Category Bonus
```

Quy trình:

```text
Student CV
     ↓
Preprocessing
     ↓
Skill Extraction
     ↓
TF-IDF Vector
     ↓
Career Prediction
     ↓
Compare with Jobs
     ↓
Cosine Similarity
     ↓
Match Score
     ↓
Skill Gap
     ↓
Explanation
     ↓
Top-K Jobs
```

---

# ⭐ Match Score

Match Score được xây dựng từ:

```text
CV ↔ Job Similarity
        +
Predicted Career Category
```

Mục đích là ưu tiên những công việc:

- Có nội dung tương đồng với CV
- Có kỹ năng phù hợp
- Thuộc định hướng nghề nghiệp được ML dự đoán

---

# 🔎 Skill Gap Analysis

Hệ thống so sánh:

```text
CV Skills
    ↕
Job Required Skills
```

Sau đó xác định:

```text
Matched Skills
Missing Skills
```

Ví dụ:

```text
CV:
Python
Flask
SQL
Git

Job:
Python
Flask
PostgreSQL
Docker
Git
```

Kết quả:

```text
Matched:
Python
Flask
Git

Missing:
PostgreSQL
Docker
```

---

# 💡 Recommendation Explanation

Hệ thống tạo giải thích cho mỗi recommendation dựa trên:

- Career Prediction
- Match Score
- Matched Skills
- Missing Skills
- Job Category

Giúp sinh viên hiểu **vì sao công việc được đề xuất** thay vì chỉ nhận một danh sách Job.

---

# 🛠️ Technology Stack

## Backend

```text
Python
Flask
SQLite
```

## Machine Learning

```text
scikit-learn
pandas
NumPy
TF-IDF
Logistic Regression
Cosine Similarity
joblib
```

## Frontend

```text
HTML5
CSS3
Bootstrap
JavaScript
Jinja2
```

## Email

```text
Brevo Transactional Email API
OTP Verification
```

## Deployment

```text
GitHub
Render
Gunicorn
```

---

# 🏗️ System Architecture

```text
                     USER
                       │
                       ▼
                Flask Web App
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       SQLite       AI / ML       Brevo
          │            │            │
          │         TF-IDF          │
          │            │            │
          │      LogisticRegression │
          │            │            │
          │     Recommendation      │
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
                  Web Interface
```

---

# 📂 Project Structure

```text
IT-Career-Match/
│
├── ai/
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
│   └── jobs.csv
│
├── database/
│   ├── database.py
│   └── it_career_match.db
│
├── models/
│   ├── career_classifier.joblib
│   └── tfidf_vectorizer.joblib
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── verify_otp.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── upload_cv.html
│   ├── jobs.html
│   └── recommendations.html
│
├── uploads/
├── app.py
├── requirements.txt
└── README.md
```

---

# 🔐 Security

Hệ thống hiện áp dụng:

- Password Hashing
- OTP Email Verification
- OTP Expiration
- Flask Session
- Role-Based Access Control
- Environment Variables
- `.env` excluded from Git
- API keys are not stored in source code

Đang phát triển:

- OTP Resend Cooldown
- OTP Rate Limiting
- Improved Admin Authorization

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

Tạo:

```text
.env
```

Nội dung:

```env
SECRET_KEY=your_secret_key
BREVO_API_KEY=your_brevo_api_key
```

Không commit `.env` lên GitHub.

## 5. Run

```bash
python app.py
```

Mở:

```text
http://127.0.0.1:5000
```

---

# 🗺️ Development Roadmap

## ✅ Completed

- [x] User Registration
- [x] Email OTP Verification
- [x] Login / Logout
- [x] Student Profile
- [x] PDF CV Parser
- [x] DOCX CV Parser
- [x] Text Preprocessing
- [x] Skill Extraction
- [x] TF-IDF
- [x] Career Prediction
- [x] Logistic Regression Model
- [x] Content-Based Recommendation
- [x] Cosine Similarity
- [x] Match Score
- [x] Skill Gap Analysis
- [x] Recommendation Explanation
- [x] Basic Job Management
- [x] Render Deployment
- [x] Brevo Email Integration

## 🚧 In Development

- [ ] Expand Job Database (~60 jobs)
- [ ] Detailed Job Information
- [ ] Student Job Search
- [ ] Advanced Job Filters
- [ ] Job Detail Page
- [ ] Pagination
- [ ] Admin Dashboard
- [ ] User Management
- [ ] User CRUD
- [ ] User Role Management
- [ ] Admin Job Search / Filter
- [ ] Job Active / Inactive
- [ ] CSV Export
- [ ] Excel Export
- [ ] Application Management
- [ ] Statistics Dashboard
- [ ] OTP Resend Cooldown
- [ ] OTP Rate Limiting
- [ ] Responsive Mobile Improvements

## 🔮 Future

- [ ] PostgreSQL
- [ ] Real-time Job API
- [ ] Semantic Embeddings
- [ ] Advanced NLP
- [ ] Resume Scoring
- [ ] Learning Path Recommendation
- [ ] Skill Recommendation
- [ ] Favourite Jobs
- [ ] Application Tracking
- [ ] Improved Recommendation Model

---

# ⚠️ Current Limitations

- Dataset ML còn tương đối nhỏ.
- Career Prediction hiện hỗ trợ 7 nhóm nghề chính.
- Skill Extraction chủ yếu dựa trên danh sách kỹ năng định nghĩa trước.
- Job dataset hiện đang được mở rộng.
- SQLite phù hợp với demo nhưng chưa phải lựa chọn tối ưu cho production.
- Chưa sử dụng dữ liệu tuyển dụng thời gian thực.
- Recommendation chủ yếu dựa trên nội dung CV và Job Description.

---

# 📚 Job Data Reference

Cấu trúc thông tin tuyển dụng và hệ thống Search/Filter được xây dựng với tham khảo từ các nền tảng tuyển dụng, trong đó có TopCV.

Dữ liệu demo của project được xây dựng phục vụ mục đích học tập và nghiên cứu.

Project không nhằm sao chép hoặc đại diện chính thức cho TopCV.

---

# 🎓 Project Purpose

Đồ án nghiên cứu việc kết hợp:

```text
Machine Learning
       +
Natural Language Processing
       +
Recommendation System
       +
Web Application
```

để hỗ trợ sinh viên CNTT:

- Hiểu kỹ năng hiện tại
- Xác định định hướng nghề nghiệp
- Tìm công việc phù hợp
- Phát hiện kỹ năng còn thiếu
- Hiểu lý do AI đề xuất một công việc

---

# 👨‍💻 Author

**Trần Quốc Huy**

Information Technology Student

GitHub: https://github.com/Storqh

---

# 📄 License

This project is developed for educational and research purposes.