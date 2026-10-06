import os
import resend
import random
import time
from ai.recommender import recommend_jobs, predict_career
from ai.text_preprocessing import preprocess_text
from ai.skill_extractor import extract_skills
from ai.cv_parser import read_pdf, read_docx
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import get_connection

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-this"
)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
resend.api_key = os.environ.get("RESEND_API_KEY")   
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        # =========================
        # VALIDATION
        # =========================

        if not full_name or not email or not password:
            return render_template(
                "register.html",
                message="Vui lòng nhập đầy đủ thông tin.",
                message_type="warning",
                full_name=full_name,
                email=email
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                message="Mật khẩu phải có ít nhất 6 ký tự.",
                message_type="danger",
                full_name=full_name,
                email=email
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                message="Xác nhận mật khẩu không khớp.",
                message_type="danger",
                full_name=full_name,
                email=email
            )

        # =========================
        # CHECK EMAIL
        # =========================

        connection = get_connection()

        existing_user = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if existing_user:
            return render_template(
                "register.html",
                message="Email này đã được đăng ký.",
                message_type="danger",
                full_name=full_name,
                email=email
            )

        # =========================
        # CREATE OTP
        # =========================

        otp = str(random.SystemRandom().randint(
            100000,
            999999
        ))

        # Lưu tạm thông tin đăng ký
        session["pending_register"] = {
            "full_name": full_name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "otp": otp,
            "otp_created_at": int(time.time())
        }

        # =========================
        # SEND EMAIL
        # =========================

        try:

            msg = Message(
                subject="Mã xác minh IT Career Match",
                recipients=[email]
            )

            msg.body = f"""
Xin chào {full_name},

Mã OTP xác minh tài khoản IT Career Match của bạn là:

{otp}

Mã OTP có hiệu lực trong 5 phút.

Nếu bạn không thực hiện đăng ký này,
hãy bỏ qua email.

IT Career Match
"""

            mail.send(msg)

        except Exception as error:

            print("MAIL ERROR:", error)

            session.pop(
                "pending_register",
                None
            )

            return render_template(
                "register.html",
                message="Không thể gửi OTP. Vui lòng thử lại.",
                message_type="danger",
                full_name=full_name,
                email=email
            )

        return redirect(
            url_for("verify_otp")
        )

    return render_template("register.html")
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    pending = session.get("pending_register")

    if not pending:
        return redirect(
            url_for("register")
        )

    if request.method == "POST":

        user_otp = request.form.get(
            "otp", ""
        ).strip()

        if not user_otp:
            return render_template(
                "verify_otp.html",
                message="Vui lòng nhập mã OTP.",
                message_type="warning",
                email=pending["email"]
            )

        # =========================
        # CHECK EXPIRED
        # =========================

        current_time = int(time.time())

        if (
            current_time -
            pending["otp_created_at"]
            > 300
        ):

            return render_template(
                "verify_otp.html",
                message="Mã OTP đã hết hạn. Vui lòng gửi lại mã.",
                message_type="danger",
                email=pending["email"]
            )

        # =========================
        # CHECK OTP
        # =========================

        if user_otp != pending["otp"]:

            return render_template(
                "verify_otp.html",
                message="Mã OTP không chính xác.",
                message_type="danger",
                email=pending["email"]
            )

        # =========================
        # CREATE USER
        # =========================

        connection = get_connection()

        try:

            cursor = connection.execute(
                """
                INSERT INTO users
                (email, password, role)
                VALUES (?, ?, ?)
                """,
                (
                    pending["email"],
                    pending["password_hash"],
                    "student"
                )
            )

            user_id = cursor.lastrowid

            connection.execute(
                """
                INSERT INTO student_profiles
                (user_id, full_name)
                VALUES (?, ?)
                """,
                (
                    user_id,
                    pending["full_name"]
                )
            )

            connection.commit()

        except Exception as error:

            connection.rollback()
            connection.close()

            print(
                "REGISTER ERROR:",
                error
            )

            return render_template(
                "verify_otp.html",
                message="Không thể tạo tài khoản.",
                message_type="danger",
                email=pending["email"]
            )

        connection.close()

        session.pop(
            "pending_register",
            None
        )

        return render_template(
            "login.html",
            message="Xác minh email thành công. Bạn có thể đăng nhập.",
            message_type="success"
        )

    return render_template(
        "verify_otp.html",
        email=pending["email"]
    )
@app.route("/resend-otp", methods=["POST"])
def resend_otp():

    pending = session.get(
        "pending_register"
    )

    if not pending:
        return redirect(
            url_for("register")
        )

    otp = str(
        random.SystemRandom().randint(
            100000,
            999999
        )
    )

    pending["otp"] = otp
    pending["otp_created_at"] = int(
        time.time()
    )

    session["pending_register"] = pending

    try:

        msg = Message(
            subject="Mã OTP mới - IT Career Match",
            recipients=[
                pending["email"]
            ]
        )

        msg.body = f"""
Xin chào {pending['full_name']},

Mã OTP mới của bạn là:

{otp}

Mã có hiệu lực trong 5 phút.

IT Career Match
"""

        mail.send(msg)

    except Exception as error:

        print(
            "RESEND OTP ERROR:",
            error
        )

        return render_template(
            "verify_otp.html",
            message="Không thể gửi lại OTP.",
            message_type="danger",
            email=pending["email"]
        )

    return render_template(
        "verify_otp.html",
        message="Mã OTP mới đã được gửi đến email của bạn.",
        message_type="success",
        email=pending["email"]
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    # Nếu đã đăng nhập thì chuyển về Dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        # Lấy dữ liệu từ form
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Kiểm tra dữ liệu rỗng
        if not email or not password:
            return render_template(
                "login.html",
                message="Vui lòng nhập đầy đủ email và mật khẩu.",
                message_type="warning",
                email=email
            )

        # Tìm tài khoản trong Database
        connection = get_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        # Email không tồn tại
        if user is None:
            return render_template(
                "login.html",
                message="Không tìm thấy tài khoản với email này.",
                message_type="danger",
                email=email
            )

        # Sai mật khẩu
        if not check_password_hash(user["password"], password):
            return render_template(
                "login.html",
                message="Mật khẩu không chính xác. Vui lòng thử lại.",
                message_type="danger",
                email=email
            )

        # Đăng nhập thành công
        session["user_id"] = user["user_id"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        return redirect(url_for("dashboard"))

    return render_template("login.html")
@app.route("/dashboard")
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        email=session["email"]
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_connection()

    if request.method == "POST":

        full_name = request.form["full_name"]
        date_of_birth = request.form["date_of_birth"]
        major = request.form["major"]
        bio = request.form["bio"]

        connection.execute(
            """
            UPDATE student_profiles
            SET full_name = ?,
                date_of_birth = ?,
                major = ?,
                bio = ?
            WHERE user_id = ?
            """,
            (
                full_name,
                date_of_birth,
                major,
                bio,
                user_id
            )
        )
        connection.commit()
    print("Đã cập nhật profile:", user_id)
    profile_data = connection.execute(
        """
        SELECT *
        FROM student_profiles
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "profile.html",
        profile=profile_data
    )
@app.route("/jobs")
def jobs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    jobs_data = connection.execute(
        "SELECT * FROM jobs ORDER BY created_at DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs_data
    )


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():

    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "admin":
        return "Bạn không có quyền thêm công việc.", 403
    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        job_type = request.form["job_type"]
        category = request.form["category"]
        description = request.form["description"]

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO jobs
            (title, description, company, location, job_type, category)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                company,
                location,
                job_type,
                category
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("jobs"))

    return render_template("add_jobs.html")
@app.route("/jobs/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "admin":
        return "Bạn không có quyền sửa công việc.", 403
    connection = get_connection()

    job = connection.execute(
        "SELECT * FROM jobs WHERE job_id = ?",
        (job_id,)
    ).fetchone()

    if job is None:
        connection.close()
        return "Không tìm thấy công việc", 404

    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        job_type = request.form["job_type"]
        category = request.form["category"]
        description = request.form["description"]

        connection.execute(
            """
            UPDATE jobs
            SET title = ?,
                description = ?,
                company = ?,
                location = ?,
                job_type = ?,
                category = ?
            WHERE job_id = ?
            """,
            (
                title,
                description,
                company,
                location,
                job_type,
                category,
                job_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("jobs"))

    connection.close()

    return render_template(
        "edit_job.html",
        job=job
    )
@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "admin":
        return "Bạn không có quyền xóa công việc.", 403
    connection = get_connection()

    job = connection.execute(
        "SELECT * FROM jobs WHERE job_id = ?",
        (job_id,)
    ).fetchone()

    if job is None:
        connection.close()
        return "Không tìm thấy công việc", 404

    connection.execute(
        "DELETE FROM jobs WHERE job_id = ?",
        (job_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("jobs"))
@app.route("/upload-cv", methods=["GET", "POST"])
def upload_cv():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        if "cv" not in request.files:
            return render_template(
                "upload_cv.html",
                message="Không tìm thấy file."
            )

        file = request.files["cv"]

        if file.filename == "":
            return render_template(
                "upload_cv.html",
                message="Bạn chưa chọn CV."
            )

        if not allowed_file(file.filename):
            return render_template(
                "upload_cv.html",
                message="Chỉ hỗ trợ file PDF hoặc DOCX."
            )

        filename = secure_filename(file.filename)

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(file_path)
        parsed_text = None

        if filename.lower().endswith(".pdf"):
            parsed_text = read_pdf(file_path)
        elif filename.lower().endswith(".docx"):
            parsed_text = read_docx(file_path)
            
        cleaned_text = preprocess_text(parsed_text)
        found_skills = extract_skills(cleaned_text)

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO cvs
            (user_id, file_name, file_path, parsed_text)
            VALUES (?, ?, ?, ?)
            """,
            (
                session["user_id"],
                filename,
                file_path,
                parsed_text 
            )
        )
        for skill_name in found_skills:
            connection.execute(
            """
            INSERT OR IGNORE INTO skills (name)
            VALUES (?)
            """,
            (skill_name,)
        )

            skill = connection.execute(
                """
                SELECT skill_id
                FROM skills
                WHERE name = ?
                """,
                (skill_name,)
            ).fetchone()

            if skill:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO student_skills
                    (user_id, skill_id)
                    VALUES (?, ?)
                    """,
                    (
                        session["user_id"],
                        skill["skill_id"]
                    )
                )
        connection.commit()
        connection.close()

        return redirect(
            url_for("recommendations")
        )

    return render_template("upload_cv.html")
@app.route("/recommendations")
def recommendations():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    # Lấy CV mới nhất của user
    cv = connection.execute(
        """
        SELECT parsed_text
        FROM cvs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    if not cv or not cv["parsed_text"]:
        return redirect(url_for("upload_cv"))

    cv_text = cv["parsed_text"]

    # Dự đoán nhóm nghề
    predicted_career = predict_career(cv_text)

    # Lấy Top 5 Job
    recommended_jobs = recommend_jobs(
        cv_text,
        top_k=5
    )

    return render_template(
        "recommendations.html",
        predicted_career=predicted_career,
        jobs=recommended_jobs
    )
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )