# 🛠️ Hướng Dẫn Phát Triển & Chạy Dự Án

Tài liệu này hướng dẫn các thành viên trong team cài đặt, cấu hình và chạy **IT Career Match** cục bộ.

---

## 📋 Yêu Cầu Hệ Thống

| Công cụ | Phiên bản khuyến nghị |
|---|---|
| **Git** | 2.40+ |
| **Docker Desktop** | 4.25+ (có Docker Engine + Compose) |
| **Python** | 3.10 - 3.11 (nếu chạy không Docker) |
| **PostgreSQL** | 14+ (nếu chạy không Docker) |
| **Node.js** | Không bắt buộc (chỉ nếu build frontend assets) |

> **Khuyến nghị**: Dùng **Docker Compose** để đảm bảo môi trường nhất quán toàn team.

---

## 🚀 Chạy Nhanh Với Docker (Khuyến Nghị)

### 1. Clone repository
```bash
git clone https://github.com/Storqh/IT-Career-Match.git
cd IT-Career-Match
```

### 2. Tạo file môi trường từ mẫu
```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux / Git Bash
cp .env.example .env
```

### 3. Cấu hình `.env` (BẮT BUỘC)
Mở file `.env` và điền các giá trị thực tế:

```ini
# Flask
SECRET_KEY=your-super-secret-key-generate-with-python
FLASK_ENV=development
FLASK_DEBUG=1

# Database (Docker Compose sẽ dùng service name 'db')
DATABASE_URL=postgresql://postgres:postgres@db:5432/itcareermatch

# Email - Brevo (Sendinblue) - Lấy từ https://app.brevo.com/settings/keys
BREVO_API_KEY=xkeysib-xxxxxxxxxxxxxxxxxxxxxxxx
BREVO_SENDER_EMAIL=your-email@domain.com
BREVO_SENDER_NAME=IT Career Match

# Upload
MAX_CONTENT_LENGTH=5242880  # 5MB

# AI/ML (tùy chọn - dùng model có sẵn nếu không set)
MODEL_VERSION=v1.0
CONFIDENCE_THRESHOLD=0.3
TOP_K_RECOMMENDATIONS=10
ENABLE_CAREER_BONUS=true
CAREER_BONUS_POINTS=30
```

> **Tạo SECRET_KEY nhanh**:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Build và khởi chạy
```bash
docker compose up -d --build
```

### 5. Kiểm tra trạng thái
```bash
docker compose ps
# Kết quả mong đợi: web (healthy), db (healthy)

docker compose logs -f web   # Xem log Flask real-time
```

### 6. Truy cập ứng dụng
```
http://localhost:5000
```

---

## 💻 Chạy Local Không Docker (Development)

> Chỉ dùng khi cần debug Python code trực tiếp hoặc không muốn dùng Docker.

### 1. Cài đặt PostgreSQL local
- Windows: Tải từ https://www.postgresql.org/download/windows/
- macOS: `brew install postgresql@14 && brew services start postgresql@14`
- Linux: `sudo apt install postgresql-14`

### 2. Tạo database & user
```bash
psql -U postgres
CREATE DATABASE itcareermatch;
CREATE USER appuser WITH PASSWORD 'apppassword';
GRANT ALL PRIVILEGES ON DATABASE itcareermatch TO appuser;
\q
```

### 3. Virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 4. Cài dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Cấu hình `.env` cho local
```ini
DATABASE_URL=postgresql://appuser:apppassword@localhost:5432/itcareermatch
# Các biến khác giữ nguyên như Docker
```

### 6. Khởi tạo database (tạo bảng, seed data)
```bash
# Chạy migrations (nếu dùng Flask-Migrate)
flask db upgrade

# Hoặc chạy script seed trực tiếp
python -c "from database.database import init_db; init_db()"
python data/seed_jobs.py
```

### 7. Chạy server development
```bash
python app.py
# hoặc
flask run --host=0.0.0.0 --port=5000 --debug
```

Mở: http://127.0.0.1:5000

---

## 🔧 Các Lệnh Docker Thường Dùng

| Lệnh | Mô tả |
|---|---|
| `docker compose up -d` | Khởi động nền (detached) |
| `docker compose up -d --build` | Build lại image + chạy |
| `docker compose ps` | Xem trạng thái container |
| `docker compose logs -f` | Xem log tất cả service |
| `docker compose logs -f web` | Xem log chỉ Flask app |
| `docker compose down` | Dừng container (giữ volume data) |
| `docker compose down -v` | **Dừng VÀ xóa volume** (MẤT DATA DB) |
| `docker compose exec web bash` | Vào shell container web |
| `docker compose exec db psql -U postgres -d itcareermatch` | Vào PostgreSQL CLI |

---

## 🗂️ Cấu Trúc Dự Án (Tóm Tắt)

```
IT-Career-Match/
├── app.py                 # Entry point Flask
├── compose.yaml           # Docker Compose config
├── Dockerfile             # Build image Flask
├── requirements.txt       # Python dependencies
├── .env.example           # Mẫu biến môi trường
├── ai/                    # ML modules (career_classifier, recommender, learning_resources...)
├── app/routes/            # Flask Blueprints (auth, admin, jobs, cv, chatbot, profile)
├── database/              # PostgreSQL connection pool
├── models/                # Model files (.joblib, .npy)
├── static/                # CSS, JS, images
├── templates/             # Jinja2 templates (layouts, components, admin, pages)
├── uploads/               # CV uploads (gitignored)
└── tests/                 # Unit tests
```

---

## 🌿 Git Workflow Cho Team

### Branch Strategy
```
main          ← Production ready (protected)
  ↑
  └── current ← Development branch (tất cả PR merge vào đây)
       ↑
       └── feature/xxx  ← Feature branches (tách từ current)
```

### Quy Trình Làm Việc
```bash
# 1. Cập nhật current mới nhất
git checkout current
git pull origin current

# 2. Tạo feature branch
git checkout -b feature/ten-tinh-nang

# 3. Code, commit thường xuyên
git add .
git commit -m "feat: mô tả ngắn gọn"

# 4. Push feature branch
git push -u origin feature/ten-tinh-nang

# 5. Tạo Pull Request trên GitHub: feature/ten-tinh-nang → current
#    - Yêu cầu review ít nhất 1 thành viên
#    - Pass CI (nếu có)

# 6. Sau khi merge: xóa feature branch local & remote
git checkout current
git pull origin current
git branch -d feature/ten-tinh-nang
git push origin --delete feature/ten-tinh-nang
```

### Commit Message Convention
```
feat:     Tính năng mới
fix:      Sửa bug
docs:     Cập nhật tài liệu
style:    Format code (prettier, lint)
refactor: Tái cấu trúc code (không đổi behavior)
test:     Thêm/sửa test
chore:    Cập nhật build, deps, config
```

Ví dụ:
- `feat: add learning resources recommendation`
- `fix: sidebar toggle button clipping on collapsed state`
- `docs: update README with Docker instructions`

---

## 🧪 Testing & Kiểm Tra

### Chạy test (nếu có pytest)
```bash
# Trong container
docker compose exec web pytest tests/ -v

# Local
pytest tests/ -v
```

### Kiểm tra syntax Jinja2 templates
```bash
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
for name in env.list_templates():
    try: env.get_template(name)
    except Exception as e: print(f'ERROR {name}: {e}')
print('All templates OK')
"
```

### Kiểm tra CSS/JS (manual)
- Mở DevTools → Console: không có lỗi JS
- Resize màn hình: Sidebar responsive, Chatbot mobile OK

---

## 🐛 Debug Thường Gặp

### Database connection failed
```bash
# Kiểm tra container db đang chạy
docker compose ps db

# Xem log db
docker compose logs db

# Restart db
docker compose restart db
```

### Model ML không load được
- Kiểm tra file `.joblib` trong `models/` có tồn tại không
- Chạy training lại: `python -m ai.career_classifier` (nếu có script train)

### Email OTP không gửi được
- Kiểm tra `BREVO_API_KEY` trong `.env`
- Xem log Flask: `docker compose logs -f web | grep -i email`

### Port 5000 bị chiếm
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

---

## 📦 Deploy Production (Render)

### Cấu hình Render
1. Tạo **Web Service** từ GitHub repo `Storqh/IT-Career-Match`
2. Branch: `current`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:\$PORT --workers 2 --timeout 120`
5. Environment Variables: Thêm tất cả từ `.env` (trừ `FLASK_DEBUG=0`)

### Database Render
- Tạo **PostgreSQL** database trên Render
- Lấy `External Database URL` → gán vào `DATABASE_URL` env var

### Persistent Disk (Uploads)
- Tạo Disk 1GB → Mount path: `/app/uploads`
- Cập nhật `UPLOAD_FOLDER=/app/uploads` trong env

---

## 📚 Tài Liệu Tham Khảo

- [README.md](README.md) - Tổng quan dự án, tính năng, kiến trúc
- [Flask Docs](https://flask.palletsprojects.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Brevo API](https://developers.brevo.com/)

---

## ✅ Checklist Onboarding Thành Viên Mới

- [ ] Clone repo & checkout branch `current`
- [ ] Cài Docker Desktop & chạy `docker compose up -d --build`
- [ ] Truy cập http://localhost:5000 thành công
- [ ] Đăng ký tài khoản, verify OTP, đăng nhập
- [ ] Upload CV test, xem recommendations
- [ ] Mở chatbot, test quick replies
- [ ] Hiểu luồng Git workflow & commit convention
- [ ] Đọc xong `README.md` và `DEVELOPMENT.md`

---

## 🤝 Hỗ Trợ

Nếu gặp vấn đề không giải quyết được:
1. Kiểm tra **Issues** trên GitHub
2. Hỏi trong group chat team
3. Tạo Issue mới với label `bug` / `question` / `help wanted`

---

**Cập nhật:** 2025-11-16  
**Phiên bản:** 1.0  
**Dành cho:** Team IT Career Match