# 🎯 IT Career Match

## Personalized Job Recommendation System for IT Students

IT Career Match là hệ thống gợi ý việc làm cá nhân hóa dành cho sinh viên Công nghệ Thông tin.

Hệ thống sử dụng **Machine Learning** và **Natural Language Processing (NLP)** để phân tích CV, trích xuất kỹ năng, dự đoán nhóm nghề nghiệp phù hợp và đề xuất các công việc dựa trên nội dung hồ sơ của người dùng.

---

## 🌐 Live Demo

👉 https://it-career-match.onrender.com

> Website được deploy trên Render Free nên lần truy cập đầu tiên có thể mất một chút thời gian để khởi động.

---

## ✨ Chức năng chính

- Đăng ký tài khoản
- Xác thực email bằng OTP
- Đăng nhập / đăng xuất
- Quản lý hồ sơ sinh viên
- Upload CV PDF / DOCX
- Tự động đọc nội dung CV
- Trích xuất kỹ năng từ CV
- Dự đoán nhóm nghề nghiệp bằng Machine Learning
- Gợi ý việc làm phù hợp
- Tính Match Score giữa CV và công việc
- Phân tích Skill Gap
- Giải thích lý do đề xuất công việc
- Quản lý danh sách công việc

---

## 🤖 Machine Learning

### Career Prediction

Hệ thống sử dụng:

- **TF-IDF** để chuyển văn bản CV thành vector đặc trưng.
- **Logistic Regression** để dự đoán nhóm nghề nghiệp.

Các nhóm nghề hiện được mô hình hỗ trợ:

1. AI / Machine Learning
2. Backend Development
3. Cybersecurity
4. Data
5. DevOps / Cloud
6. Network / System
7. Other IT

### Kết quả mô hình

| Metric | Score |
|---|---:|
| Accuracy | 83.64% |
| Precision | 83.94% |
| Recall | 83.64% |
| F1-Score | 83.43% |

---

## 💼 Job Recommendation

Sau khi phân tích CV, hệ thống sử dụng:

**Content-Based Filtering + Cosine Similarity**

để tính độ tương đồng giữa CV và mô tả công việc.

Quy trình:

```text
Upload CV
    ↓
Extract Text
    ↓
Text Preprocessing
    ↓
Skill Extraction
    ↓
TF-IDF
    ↓
Career Prediction
    ↓
Cosine Similarity
    ↓
Match Score
    ↓
Skill Gap Analysis
    ↓
Top Job Recommendations
```

Match Score được tính dựa trên độ tương đồng nội dung CV và nhóm nghề nghiệp dự đoán.

---

## 🧠 AI Features

Hệ thống hiện có các chức năng AI/ML:

- CV Analysis
- Skill Extraction
- Career Prediction
- Job Recommendation
- Match Score
- Skill Gap Analysis
- Recommendation Explanation

---

## 🛠️ Technologies

### Backend

- Python
- Flask
- SQLite

### Machine Learning

- scikit-learn
- pandas
- NumPy
- TF-IDF
- Logistic Regression
- Cosine Similarity
- joblib

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript

### Email

- Brevo Transactional Email API
- OTP Email Verification

### Deployment

- GitHub
- Render
- Gunicorn

---

## 📂 Project Structure

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

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/Storqh/IT-Career-Match.git
cd IT-Career-Match
```

### 2. Tạo Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Cài thư viện

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Tạo file:

```text
.env
```

Thêm:

```env
SECRET_KEY=your_secret_key
BREVO_API_KEY=your_brevo_api_key
```

> Không commit file `.env` hoặc API key lên GitHub.

### 5. Chạy ứng dụng

```bash
python app.py
```

Sau đó truy cập:

```text
http://127.0.0.1:5000
```

---

## 🔐 OTP Email Verification

Khi người dùng đăng ký:

```text
Register
   ↓
Generate OTP
   ↓
Brevo API
   ↓
Send OTP Email
   ↓
Verify OTP
   ↓
Create Account
```

Mật khẩu người dùng được lưu dưới dạng **password hash**, không lưu mật khẩu gốc.

---

## 📊 Dataset

Dataset được tiền xử lý trước khi huấn luyện mô hình.

Mô hình Career Prediction cuối cùng sử dụng:

- **275 samples**
- **7 career classes**
- Train/Test Split: **80/20**
- TF-IDF: tối đa **2000 features**

---

## ⚠️ Current Limitations

Phiên bản hiện tại là phiên bản phục vụ mục đích học tập và demo.

Một số hạn chế:

- Dataset còn tương đối nhỏ.
- Career Prediction hiện hỗ trợ 7 nhóm nghề chính.
- Skill Extraction chủ yếu dựa trên danh sách kỹ năng định nghĩa trước.
- SQLite phù hợp cho demo nhưng chưa tối ưu cho production deployment.
- Hệ thống chưa sử dụng dữ liệu việc làm thời gian thực.

---

## 🔮 Future Development

Trong tương lai hệ thống có thể phát triển thêm:

- PostgreSQL
- Real-time Job API
- Advanced NLP
- Semantic Embeddings
- Resume Scoring
- Learning Path Recommendation
- Personalized Skill Recommendation
- Admin Dashboard
- Favourite Jobs
- Job Application Tracking

---

## 🎓 Project Purpose

Đây là đồ án Machine Learning với mục tiêu nghiên cứu cách ứng dụng:

- Natural Language Processing
- Machine Learning
- Recommendation System

vào bài toán hỗ trợ sinh viên CNTT tìm kiếm công việc phù hợp với kỹ năng và định hướng nghề nghiệp.

---

## 👨‍💻 Author

**Trần Quốc Huy**

Information Technology Student

GitHub: https://github.com/Storqh

---

## 📄 License

This project is developed for educational purposes.