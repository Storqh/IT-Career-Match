# 🎯 IT Career Match

## Personalized Job Recommendation System for IT Students

IT Career Match là hệ thống web hỗ trợ sinh viên Công nghệ Thông tin phân tích CV, xác định nhóm nghề nghiệp phù hợp và gợi ý công việc IT dựa trên kỹ năng, nội dung CV và Machine Learning. Hệ thống kết hợp **Natural Language Processing (NLP)**, **Machine Learning** và **Content-Based Recommendation**.

## 🌐 Live Demo

**Website:** https://it-career-match.onrender.com

> Website được triển khai trên Render Free nên lần truy cập đầu tiên có thể cần thời gian để server khởi động.

---

## ✨ Chức năng chính

### Student
- **Authentication:** đăng ký, đăng nhập/đăng xuất, password hashing, xác thực OTP qua email (OTP có thời hạn 5 phút và giới hạn gửi lại).
- **Profile Management:** xem và cập nhật họ tên, ngày sinh, ngành học, giới thiệu bản thân.
- **CV Analysis:** upload CV PDF/DOCX, kiểm tra định dạng, trích xuất nội dung, tiền xử lý văn bản, trích xuất kỹ năng và lưu thông tin CV.
- **Career Prediction:** phân loại CV thành 7 nhóm nghề: AI / Machine Learning, Backend Development, Cybersecurity, Data, DevOps / Cloud, Network / System và Other IT.
- **Job Recommendation:** Content-Based Filtering + Cosine Similarity; hiển thị Career Prediction, Top-K Jobs, Match Score, Matched Skills, Missing Skills, Skill Gap Analysis và Recommendation Explanation.
- **Chatbot:** hỗ trợ tìm hiểu nhóm nghề IT, kỹ năng thường cần cho từng vị trí và định hướng học tập. Nội dung chỉ mang tính tham khảo.
- **Job Search:** tìm kiếm theo từ khóa; lọc theo nhóm nghề, địa điểm, loại công việc, kinh nghiệm, cấp độ, mức lương; sắp xếp và phân trang.

### Admin Management
- **Dashboard:** thống kê người dùng, sinh viên, Admin, công việc, CV, Application và người dùng đăng ký gần đây.
- **User Management:** xem, tìm kiếm, lọc, xem chi tiết, tạo, sửa, đổi role Student/Admin và xóa tài khoản. Admin không thể tự xóa tài khoản hoặc tự hạ quyền của mình.
- **Job Management:** thêm, sửa, xóa, xem chi tiết và quản lý trạng thái công việc.
- **Export Data:** xuất Excel `IT_Career_Match_Admin_Data.xlsx` gồm Users, Jobs, Applications và Recommendations. Password và password hash không được xuất.

---

## 🧠 Machine Learning

### Dataset

Dataset ban đầu có 289 job-role samples. Sau xử lý, dataset dùng để train gồm **275 samples, 7 classes**.

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

**TF-IDF**
```python
max_features = 2000
ngram_range = (1, 2)
```

**Logistic Regression**
```python
class_weight = "balanced"
max_iter = 1000
```

**Train/Test Split:** 80% Training, 20% Testing.

### Model Performance

| Metric | Score |
|---|---:|
| Accuracy | 83.64% |
| Precision (Weighted) | 83.94% |
| Recall (Weighted) | 83.64% |
| F1-Score (Weighted) | 83.43% |

Accuracy tương ứng **46 / 55 test samples = 83.64%**.

---

## 🎯 Recommendation Algorithm

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

Match Score hiện sử dụng độ tương đồng nội dung và điểm cộng theo nhóm nghề. Nếu Career Category của công việc trùng với Career Prediction, hệ thống cộng bonus 30 điểm.

### Skill Gap Analysis

Hệ thống so sánh Student Skills với Job Required Skills để xác định:
- **Matched Skills:** kỹ năng đã phù hợp.
- **Missing Skills:** kỹ năng còn thiếu.

Recommendation Explanation giúp người dùng hiểu lý do công việc được đề xuất dựa trên nhóm nghề dự đoán, kỹ năng phù hợp/còn thiếu, độ tương đồng CV và nội dung công việc.

---

## 🏗️ System Architecture

```text
Web Browser (HTML / CSS / Bootstrap / JavaScript)
                         |
                         v
                   Flask Backend
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      PostgreSQL    CV Processing    AI / ML Module
      Database      PDF / DOCX       TF-IDF
                    Text Processing  Logistic Regression
                    Skill Extraction Career Classification
                                          |
                                          v
                                 Recommendation Engine
                                 Content-Based Filtering
                                 Cosine Similarity
                                 Match Score / Skill Gap
                                 Recommendation Explanation
```

---

## 🗄️ Database

Hệ thống sử dụng **PostgreSQL**. Các bảng nghiệp vụ chính gồm:

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

Database lưu trữ tài khoản, hồ sơ sinh viên, CV, kỹ năng, công việc, recommendation, favourite và application. Tên bảng thực tế phụ thuộc schema hiện tại của dự án.

---

## 🐳 Docker & Docker Compose

Dự án sử dụng Docker để các thành viên có thể chạy ứng dụng và PostgreSQL trong container, hạn chế việc phải cài đặt/cấu hình database thủ công trên từng máy.

### Requirements
- Git
- Docker Desktop đã khởi động Docker Engine
- Docker Compose (được tích hợp trong Docker Desktop)

### Run with Docker Compose

**1. Clone repository**

```bash
git clone https://github.com/Storqh/IT-Career-Match.git
cd IT-Career-Match
```

**2. Tạo file môi trường**

Nếu repository có `.env.example`, tạo file `.env`:

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

macOS / Linux:
```bash
cp .env.example .env
```

Mở `.env` và điền các giá trị theo cấu hình dự án. Tên biến môi trường phải khớp với file Compose và cách ứng dụng đọc cấu hình. Không dùng mật khẩu/API key mẫu cho môi trường thật.

**3. Build và khởi chạy**

```bash
docker compose up -d --build
```

**4. Kiểm tra container**

```bash
docker compose ps
```

**5. Xem log**

```bash
docker compose logs -f
```

Xem log một service:
```bash
docker compose logs -f <service>
```

**6. Truy cập ứng dụng**

Mở port được ánh xạ trong `ports` của service ứng dụng ở file Compose. Ví dụ, nếu cấu hình `5000:5000`:

```text
http://localhost:5000
```

### Docker commands

```bash
# Khởi động
docker compose up -d

# Build lại image và khởi động
docker compose up -d --build

# Kiểm tra container
docker compose ps

# Xem log
docker compose logs -f

# Dừng và xóa container/network do Compose tạo
docker compose down
```

> **Lưu ý dữ liệu:** PostgreSQL thường được lưu trong Docker volume. `docker compose down` không xóa volume. Không chạy `docker compose down -v` nếu muốn giữ dữ liệu database, vì lệnh này có thể xóa volume PostgreSQL.

### Chia sẻ môi trường cho thành viên

Mỗi thành viên clone repository, tạo file `.env` riêng và chạy `docker compose up -d --build`. Mỗi máy có container và volume database riêng; dữ liệu trong database trên máy của bạn **không tự động** được chuyển sang máy thành viên. Nếu cần dữ liệu mẫu chung, dự án cần có migration hoặc seed script.

---

## 📁 Project Structure

Cấu trúc minh họa các thành phần chính; tên file/thư mục có thể thay đổi theo phiên bản repository.

```text
IT-Career-Match/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .env.example
├── .gitignore
├── ai/
│   ├── career_classifier.py
│   ├── cv_parser.py
│   ├── explanation.py
│   ├── match_score.py
│   ├── recommender.py
│   ├── skill_extractor.py
│   ├── skill_gap.py
│   └── text_preprocessing.py
├── data/
│   ├── career_dataset.csv
│   ├── career_ml_dataset.csv
│   ├── career_preprocessed.csv
│   ├── jobs.csv
│   └── seed_jobs.py
├── database/
│   └── database.py
├── models/
│   ├── career_classifier.joblib
│   └── tfidf_vectorizer.joblib
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── admin/
│   └── ...
└── uploads/
    └── .gitkeep
```

---

## 🛠️ Technologies

- **Backend:** Python, Flask, PostgreSQL, psycopg.
- **Machine Learning:** scikit-learn, pandas, NumPy, TF-IDF, Logistic Regression, Cosine Similarity.
- **CV Processing:** pypdf, python-docx.
- **Frontend:** HTML5, CSS3, Bootstrap, JavaScript, Jinja2.
- **Other:** Werkzeug, joblib, openpyxl, requests, python-dotenv, Gunicorn, Brevo Email API.
- **Deployment & Development:** Git, GitHub, Docker, Docker Compose, Render.

---

## 🚀 Run Locally Without Docker

Nếu chạy Flask trực tiếp trên máy, cần có Python và PostgreSQL đang hoạt động.

**1. Clone repository**
```bash
git clone https://github.com/Storqh/IT-Career-Match.git
cd IT-Career-Match
```

**2. Tạo virtual environment**

Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Cài dependencies**
```bash
pip install -r requirements.txt
```

**4. Tạo `.env`**

Tham khảo `.env.example` và khai báo các biến mà ứng dụng yêu cầu. Ví dụ:

```env
SECRET_KEY=your_generated_secret_key
DATABASE_URL=your_postgresql_connection_string
BREVO_API_KEY=your_brevo_api_key
```

Tên biến phải khớp với mã nguồn/cấu hình thực tế. Có thể tạo Flask secret key bằng:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Không commit file `.env` lên Git.

**5. Chạy ứng dụng**
```bash
python app.py
```

Mở địa chỉ/port Flask hiển thị trong terminal. Với cấu hình mặc định thường dùng:

```text
http://127.0.0.1:5000
```

---

## 🔒 Security

Hệ thống hiện áp dụng:
- Password hashing.
- Session-based authentication.
- Role-based authorization.
- Admin route protection.
- OTP email verification, expiration và resend cooldown.
- File extension validation.
- File upload size limit.
- Secure filename handling.
- Environment variables cho Secret/API Key.
- Không export password hash.

Không commit `.env`, `SECRET_KEY`, `BREVO_API_KEY`, mật khẩu database, CV người dùng hoặc dữ liệu cá nhân. Kiểm tra `.gitignore` trước khi push.

---

## ⚠️ Current Limitations

- Dataset Machine Learning còn tương đối nhỏ.
- Một số nhóm nghề có ít dữ liệu nên chưa được đưa vào classifier chính.
- Skill Extraction chủ yếu dựa trên danh sách kỹ năng đã định nghĩa.
- Recommendation chủ yếu dựa trên nội dung CV và thông tin công việc.
- Render Free có thể sleep khi không có request.
- Cần cấu hình lưu trữ bền vững phù hợp cho file upload và database khi triển khai production.

---

## 🔮 Future Development

- REST API.
- Semantic Embeddings / Sentence Transformers.
- Transformer-based NLP.
- Collaborative Filtering và Hybrid Recommendation.
- Job API Integration.
- CV Scoring.
- Learning Path Recommendation.
- Skill / Course Recommendation.
- Advanced Admin Analytics.
- Cloud File Storage.
- Automated Testing và CI/CD.
- Chatbot tư vấn nghề nghiệp có khả năng truy xuất thông tin việc làm và kỹ năng.

---

## 🎓 Project Purpose

Dự án được xây dựng nhằm nghiên cứu và áp dụng Machine Learning, Natural Language Processing, Recommendation System, Web Development, Database Design, Software Engineering, Scrum và Deployment.

> **Gợi ý việc làm cá nhân hóa cho sinh viên Công nghệ Thông tin dựa trên CV, kỹ năng và Machine Learning.**

---

## 👨‍💻 Author

**Nhóm 4**  
GitHub: [Storqh](https://github.com/Storqh)

**IT Career Match — Personalized Job Recommendation System for IT Students**

---

## 📄 License

Dự án được xây dựng phục vụ mục đích học tập và nghiên cứu.
