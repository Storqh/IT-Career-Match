import os
import random
import time
import requests
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from database.database import get_connection

from ai.recommender import (
    recommend_jobs,
    predict_career
)

from ai.text_preprocessing import preprocess_text
from ai.skill_extractor import extract_skills
from ai.cv_parser import read_pdf, read_docx


# =========================================================
# FLASK CONFIG
# =========================================================
load_dotenv()
app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-this"
)
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Giới hạn CV tối đa 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Tự tạo thư mục uploads nếu chưa tồn tại
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)
# =========================================================
# HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def send_otp_email(receiver_email, otp):
    if not BREVO_API_KEY:
        print("BREVO_API_KEY chưa được cấu hình.")
        return False

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    data = {
        "sender": {
            "name": "IT Career Match",
            "email": "tranquochuy8645@gmail.com"
        },
        "to": [
            {
                "email": receiver_email
            }
        ],
        "subject": "Mã OTP đăng ký IT Career Match",
        "htmlContent": f"""
        <html>
            <body>
                <h2>IT Career Match</h2>

                <p>Mã OTP đăng ký tài khoản của bạn là:</p>

                <h1>{otp}</h1>

                <p>Mã OTP có hiệu lực trong 5 phút.</p>

                <p>Nếu bạn không thực hiện đăng ký, hãy bỏ qua email này.</p>
            </body>
        </html>
        """
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=15
        )

        if response.status_code in (200, 201, 202):
            print("OTP đã gửi tới:", receiver_email)
            return True

        print("BREVO ERROR:", response.status_code)
        print(response.text)
        return False

    except requests.RequestException as e:
        print("BREVO REQUEST ERROR:", e)
        return False

# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template(
        "index.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    # Nếu đã login
    if "user_id" in session:
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        # -----------------------------
        # GET FORM DATA
        # -----------------------------

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if (
            not full_name
            or not email
            or not password
            or not confirm_password
        ):
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

        # -----------------------------
        # CHECK EXISTING EMAIL
        # -----------------------------

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

        # -----------------------------
        # CREATE OTP
        # -----------------------------

        otp = str(
            random.SystemRandom().randint(
                100000,
                999999
            )
        )

        # -----------------------------
        # SAVE TEMP REGISTER DATA
        # -----------------------------

        session["pending_register"] = {
            "full_name": full_name,
            "email": email,
            "password_hash":
                generate_password_hash(password),
            "otp": otp,
            "otp_created_at": int(time.time())
        }

        # -----------------------------
        # SEND OTP
        # -----------------------------

        try:

            send_otp_email(
                email,
                otp
            )

        except Exception as error:

            print(
                "EMAIL API ERROR:",
                repr(error)
            )

            session.pop(
                "pending_register",
                None
            )

            return render_template(
                "register.html",
                message=(
                    "Không thể gửi OTP. "
                    "Vui lòng thử lại."
                ),
                message_type="danger",
                full_name=full_name,
                email=email
            )

        return redirect(
            url_for("verify_otp")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# VERIFY OTP
# =========================================================

@app.route(
    "/verify-otp",
    methods=["GET", "POST"]
)
def verify_otp():

    pending = session.get(
        "pending_register"
    )

    if not pending:
        return redirect(
            url_for("register")
        )

    if request.method == "POST":

        user_otp = request.form.get(
            "otp",
            ""
        ).strip()

        # -----------------------------
        # EMPTY OTP
        # -----------------------------

        if not user_otp:
            return render_template(
                "verify_otp.html",
                message="Vui lòng nhập mã OTP.",
                message_type="warning",
                email=pending["email"]
            )

        # -----------------------------
        # CHECK OTP FORMAT
        # -----------------------------

        if (
            not user_otp.isdigit()
            or len(user_otp) != 6
        ):
            return render_template(
                "verify_otp.html",
                message="OTP phải gồm 6 chữ số.",
                message_type="danger",
                email=pending["email"]
            )

        # -----------------------------
        # CHECK EXPIRED
        # -----------------------------

        current_time = int(
            time.time()
        )

        if (
            current_time
            - pending["otp_created_at"]
            > 300
        ):
            return render_template(
                "verify_otp.html",
                message=(
                    "Mã OTP đã hết hạn. "
                    "Vui lòng gửi lại mã."
                ),
                message_type="danger",
                email=pending["email"]
            )

        # -----------------------------
        # CHECK OTP
        # -----------------------------

        if user_otp != pending["otp"]:
            return render_template(
                "verify_otp.html",
                message="Mã OTP không chính xác.",
                message_type="danger",
                email=pending["email"]
            )

        # -----------------------------
        # CREATE USER
        # -----------------------------

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

            # -------------------------
            # CREATE PROFILE
            # -------------------------

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
                repr(error)
            )

            return render_template(
                "verify_otp.html",
                message=(
                    "Không thể tạo tài khoản. "
                    "Vui lòng thử lại."
                ),
                message_type="danger",
                email=pending["email"]
            )

        connection.close()

        # Xóa pending register
        session.pop(
            "pending_register",
            None
        )

        return render_template(
            "login.html",
            message=(
                "Xác minh email thành công. "
                "Bạn có thể đăng nhập."
            ),
            message_type="success"
        )

    return render_template(
        "verify_otp.html",
        email=pending["email"]
    )


# =========================================================
# RESEND OTP
# =========================================================

@app.route(
    "/resend-otp",
    methods=["POST"]
)
def resend_otp():

    pending = session.get(
        "pending_register"
    )

    if not pending:
        return redirect(
            url_for("register")
        )

    # -----------------------------
    # COOLDOWN
    # -----------------------------

    current_time = int(
        time.time()
    )

    last_sent = pending.get(
        "otp_created_at",
        0
    )

    # Không cho gửi lại quá nhanh
    if current_time - last_sent < 60:

        remaining = (
            60
            - (current_time - last_sent)
        )

        return render_template(
            "verify_otp.html",
            message=(
                f"Vui lòng chờ {remaining} giây "
                "trước khi gửi lại OTP."
            ),
            message_type="warning",
            email=pending["email"]
        )

    # -----------------------------
    # NEW OTP
    # -----------------------------

    otp = str(
        random.SystemRandom().randint(
            100000,
            999999
        )
    )

    # Lưu OTP cũ để phục hồi nếu gửi thất bại
    old_otp = pending.get("otp")
    old_created_at = pending.get(
        "otp_created_at"
    )

    pending["otp"] = otp
    pending["otp_created_at"] = current_time

    session["pending_register"] = pending

    # -----------------------------
    # SEND NEW OTP
    # -----------------------------

    try:

        send_otp_email(
            pending["email"],
            otp
        )

    except Exception as error:

        print(
            "EMAIL API ERROR:",
            repr(error)
        )

        # Phục hồi OTP cũ nếu API gửi thất bại
        pending["otp"] = old_otp
        pending["otp_created_at"] = old_created_at

        session["pending_register"] = pending

        return render_template(
            "verify_otp.html",
            message="Không thể gửi lại OTP.",
            message_type="danger",
            email=pending["email"]
        )

    return render_template(
        "verify_otp.html",
        message=(
            "Mã OTP mới đã được gửi "
            "đến email của bạn."
        ),
        message_type="success",
        email=pending["email"]
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if "user_id" in session:
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not email or not password:
            return render_template(
                "login.html",
                message=(
                    "Vui lòng nhập đầy đủ "
                    "email và mật khẩu."
                ),
                message_type="warning",
                email=email
            )

        # -----------------------------
        # FIND USER
        # -----------------------------

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

        if user is None:
            return render_template(
                "login.html",
                message=(
                    "Không tìm thấy tài khoản "
                    "với email này."
                ),
                message_type="danger",
                email=email
            )

        # -----------------------------
        # CHECK PASSWORD
        # -----------------------------

        if not check_password_hash(
            user["password"],
            password
        ):
            return render_template(
                "login.html",
                message=(
                    "Mật khẩu không chính xác. "
                    "Vui lòng thử lại."
                ),
                message_type="danger",
                email=email
            )

        # -----------------------------
        # LOGIN SUCCESS
        # -----------------------------

        session["user_id"] = user["user_id"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html",
        email=session.get("email")
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    connection = get_connection()

    # -----------------------------
    # UPDATE PROFILE
    # -----------------------------

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth",
            ""
        ).strip()

        major = request.form.get(
            "major",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

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

        print(
            "Đã cập nhật profile:",
            user_id
        )

    # -----------------------------
    # GET PROFILE
    # -----------------------------

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


# =========================================================
# JOB LIST
# =========================================================

@app.route("/jobs")
def jobs():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    connection = get_connection()

    jobs_data = connection.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs_data
    )


# =========================================================
# ADD JOB
# =========================================================

@app.route(
    "/jobs/add",
    methods=["GET", "POST"]
)
def add_job():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    if session.get("role") != "admin":
        return (
            "Bạn không có quyền thêm công việc.",
            403
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        job_type = request.form.get(
            "job_type",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO jobs
            (
                title,
                description,
                company,
                location,
                job_type,
                category
            )
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

        return redirect(
            url_for("jobs")
        )

    return render_template(
        "add_jobs.html"
    )


# =========================================================
# EDIT JOB
# =========================================================

@app.route(
    "/jobs/edit/<int:job_id>",
    methods=["GET", "POST"]
)
def edit_job(job_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    if session.get("role") != "admin":
        return (
            "Bạn không có quyền sửa công việc.",
            403
        )

    connection = get_connection()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        """,
        (job_id,)
    ).fetchone()

    if job is None:
        connection.close()

        return (
            "Không tìm thấy công việc",
            404
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        job_type = request.form.get(
            "job_type",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

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

        return redirect(
            url_for("jobs")
        )

    connection.close()

    return render_template(
        "edit_job.html",
        job=job
    )


# =========================================================
# DELETE JOB
# =========================================================

@app.route(
    "/jobs/delete/<int:job_id>",
    methods=["POST"]
)
def delete_job(job_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    if session.get("role") != "admin":
        return (
            "Bạn không có quyền xóa công việc.",
            403
        )

    connection = get_connection()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        """,
        (job_id,)
    ).fetchone()

    if job is None:
        connection.close()

        return (
            "Không tìm thấy công việc",
            404
        )

    connection.execute(
        """
        DELETE FROM jobs
        WHERE job_id = ?
        """,
        (job_id,)
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("jobs")
    )


# =========================================================
# UPLOAD CV
# =========================================================

@app.route(
    "/upload-cv",
    methods=["GET", "POST"]
)
def upload_cv():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        # -----------------------------
        # CHECK FILE
        # -----------------------------

        if "cv" not in request.files:
            return render_template(
                "upload_cv.html",
                message="Không tìm thấy file."
            )

        file = request.files["cv"]

        if not file.filename:
            return render_template(
                "upload_cv.html",
                message="Bạn chưa chọn CV."
            )

        if not allowed_file(
            file.filename
        ):
            return render_template(
                "upload_cv.html",
                message=(
                    "Chỉ hỗ trợ file PDF hoặc DOCX."
                )
            )

        # -----------------------------
        # SAFE FILE NAME
        # -----------------------------

        original_filename = secure_filename(
            file.filename
        )

        # Tránh ghi đè CV giữa các user
        filename = (
            f"{session['user_id']}_"
            f"{int(time.time())}_"
            f"{original_filename}"
        )

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            file_path
        )

        # -----------------------------
        # READ CV
        # -----------------------------

        try:

            if filename.lower().endswith(
                ".pdf"
            ):
                parsed_text = read_pdf(
                    file_path
                )

            elif filename.lower().endswith(
                ".docx"
            ):
                parsed_text = read_docx(
                    file_path
                )

            else:
                parsed_text = ""

        except Exception as error:

            print(
                "CV PARSER ERROR:",
                repr(error)
            )

            return render_template(
                "upload_cv.html",
                message=(
                    "Không thể đọc nội dung CV."
                )
            )

        if not parsed_text:
            return render_template(
                "upload_cv.html",
                message=(
                    "Không tìm thấy nội dung "
                    "văn bản trong CV."
                )
            )

        # -----------------------------
        # NLP
        # -----------------------------

        cleaned_text = preprocess_text(
            parsed_text
        )

        found_skills = extract_skills(
            cleaned_text
        )

        # -----------------------------
        # SAVE CV DATABASE
        # -----------------------------

        connection = get_connection()

        try:

            connection.execute(
                """
                INSERT INTO cvs
                (
                    user_id,
                    file_name,
                    file_path,
                    parsed_text
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    filename,
                    file_path,
                    parsed_text
                )
            )

            # -------------------------
            # SAVE SKILLS
            # -------------------------

            for skill_name in found_skills:

                connection.execute(
                    """
                    INSERT OR IGNORE
                    INTO skills (name)
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
                        INSERT OR IGNORE
                        INTO student_skills
                        (
                            user_id,
                            skill_id
                        )
                        VALUES (?, ?)
                        """,
                        (
                            session["user_id"],
                            skill["skill_id"]
                        )
                    )

            connection.commit()

        except Exception as error:

            connection.rollback()
            connection.close()

            print(
                "CV DATABASE ERROR:",
                repr(error)
            )

            return render_template(
                "upload_cv.html",
                message=(
                    "Không thể lưu dữ liệu CV."
                )
            )

        connection.close()

        # -----------------------------
        # RECOMMEND
        # -----------------------------

        return redirect(
            url_for("recommendations")
        )

    return render_template(
        "upload_cv.html"
    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

@app.route("/recommendations")
def recommendations():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    connection = get_connection()

    # CV mới nhất
    cv = connection.execute(
        """
        SELECT parsed_text
        FROM cvs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (
            session["user_id"],
        )
    ).fetchone()

    connection.close()

    # Chưa upload CV
    if (
        not cv
        or not cv["parsed_text"]
    ):
        return redirect(
            url_for("upload_cv")
        )

    cv_text = cv["parsed_text"]

    # -----------------------------
    # ML CAREER PREDICTION
    # -----------------------------

    try:

        predicted_career = predict_career(
            cv_text
        )

        recommended_jobs = recommend_jobs(
            cv_text,
            top_k=5
        )

    except Exception as error:

        print(
            "RECOMMENDATION ERROR:",
            repr(error)
        )

        return render_template(
            "upload_cv.html",
            message=(
                "Không thể phân tích CV. "
                "Vui lòng thử lại."
            )
        )

    return render_template(
        "recommendations.html",
        predicted_career=predicted_career,
        jobs=recommended_jobs
    )


# =========================================================
# RUN LOCAL
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )