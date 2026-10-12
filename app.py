import os
import random
import time
import requests
import re
import unicodedata
from io import BytesIO
from flask import send_file
from openpyxl import Workbook   
from openpyxl.styles import Font, Alignment
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    jsonify,
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

def is_admin():
    return (
        "user_id" in session
        and session.get("role") == "admin"
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
# JOB LIST - SEARCH / FILTER / SORT / PAGINATION
# =========================================================

@app.route("/jobs")
def jobs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # -----------------------------------------------------
    # GET FILTER VALUES
    # -----------------------------------------------------

    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()
    experience = request.args.get("experience", "").strip()
    level = request.args.get("level", "").strip()
    salary = request.args.get("salary", "").strip()
    sort = request.args.get("sort", "newest").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    per_page = 9
    offset = (page - 1) * per_page

    connection = get_connection()

    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    where_conditions = []
    params = []

    # Student chỉ thấy job active.
    # Admin có thể thấy tất cả để tiện quản lý.
    if session.get("role") != "admin":
        where_conditions.append(
            "(status = 'active' OR status IS NULL)"
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if keyword:
        search_value = f"%{keyword}%"

        where_conditions.append("""
            (
                title LIKE ?
                OR company LIKE ?
                OR skills LIKE ?
                OR description LIKE ?
                OR category LIKE ?
            )
        """)

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    if category:
        where_conditions.append("category = ?")
        params.append(category)

    if location:
        where_conditions.append("location LIKE ?")
        params.append(f"%{location}%")

    if job_type:
        where_conditions.append("job_type = ?")
        params.append(job_type)

    if experience:
        where_conditions.append("experience = ?")
        params.append(experience)

    if level:
        where_conditions.append("level = ?")
        params.append(level)

    # -----------------------------------------------------
    # SALARY FILTER
    # -----------------------------------------------------

    if salary == "under_10":
        where_conditions.append(
            "salary_min < 10000000"
        )

    elif salary == "10_15":
        where_conditions.append("""
            salary_max >= 10000000
            AND salary_min <= 15000000
        """)

    elif salary == "15_20":
        where_conditions.append("""
            salary_max >= 15000000
            AND salary_min <= 20000000
        """)

    elif salary == "20_plus":
        where_conditions.append(
            "salary_max >= 20000000"
        )

    # -----------------------------------------------------
    # BUILD WHERE
    # -----------------------------------------------------

    where_sql = ""

    if where_conditions:
        where_sql = (
            " WHERE "
            + " AND ".join(where_conditions)
        )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    order_sql = " ORDER BY created_at DESC"

    if sort == "salary_high":
        order_sql = """
            ORDER BY
                salary_max DESC,
                created_at DESC
        """

    elif sort == "salary_low":
        order_sql = """
            ORDER BY
                CASE
                    WHEN salary_min IS NULL
                         OR salary_min = 0
                    THEN 1
                    ELSE 0
                END,
                salary_min ASC,
                created_at DESC
        """

    elif sort == "title":
        order_sql = " ORDER BY title ASC"

    # -----------------------------------------------------
    # COUNT RESULTS
    # -----------------------------------------------------

    count_sql = (
        "SELECT COUNT(*) AS total "
        "FROM jobs"
        + where_sql
    )

    total_row = connection.execute(
        count_sql,
        params
    ).fetchone()

    total_jobs = total_row["total"]

    total_pages = (
        total_jobs + per_page - 1
    ) // per_page

    # -----------------------------------------------------
    # GET JOBS
    # -----------------------------------------------------

    query = (
        "SELECT * FROM jobs"
        + where_sql
        + order_sql
        + " LIMIT ? OFFSET ?"
    )

    query_params = params + [
        per_page,
        offset
    ]

    jobs_data = connection.execute(
        query,
        query_params
    ).fetchall()

    # -----------------------------------------------------
    # FILTER OPTIONS
    # -----------------------------------------------------

    categories = connection.execute("""
        SELECT DISTINCT category
        FROM jobs
        WHERE category IS NOT NULL
          AND TRIM(category) != ''
        ORDER BY category
    """).fetchall()

    locations = connection.execute("""
        SELECT DISTINCT location
        FROM jobs
        WHERE location IS NOT NULL
          AND TRIM(location) != ''
        ORDER BY location
    """).fetchall()

    job_types = connection.execute("""
        SELECT DISTINCT job_type
        FROM jobs
        WHERE job_type IS NOT NULL
          AND TRIM(job_type) != ''
        ORDER BY job_type
    """).fetchall()

    experiences = connection.execute("""
        SELECT DISTINCT experience
        FROM jobs
        WHERE experience IS NOT NULL
          AND TRIM(experience) != ''
        ORDER BY experience
    """).fetchall()

    levels = connection.execute("""
        SELECT DISTINCT level
        FROM jobs
        WHERE level IS NOT NULL
          AND TRIM(level) != ''
        ORDER BY level
    """).fetchall()

    connection.close()

    # -----------------------------------------------------
    # PAGE RANGE
    # -----------------------------------------------------

    start_page = max(
        1,
        page - 2
    )

    end_page = min(
        total_pages,
        page + 2
    )

    page_numbers = range(
        start_page,
        end_page + 1
    )

    return render_template(
        "jobs.html",

        jobs=jobs_data,

        keyword=keyword,
        selected_category=category,
        selected_location=location,
        selected_job_type=job_type,
        selected_experience=experience,
        selected_level=level,
        selected_salary=salary,
        selected_sort=sort,

        categories=categories,
        locations=locations,
        job_types=job_types,
        experiences=experiences,
        levels=levels,

        page=page,
        total_pages=total_pages,
        total_jobs=total_jobs,
        page_numbers=page_numbers
    )
# =========================================================
# JOB DETAIL
# =========================================================

@app.route("/jobs/<int:job_id>")
def job_detail(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        """,
        (job_id,)
    ).fetchone()

    connection.close()

    if job is None:
        return "Không tìm thấy công việc.", 404

    return render_template(
        "job_detail.html",
        job=job
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
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    connection = get_connection()

    total_users = connection.execute(
        "SELECT COUNT(*) AS total FROM users"
    ).fetchone()["total"]

    total_students = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'student'
        """
    ).fetchone()["total"]

    total_admins = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'admin'
        """
    ).fetchone()["total"]

    total_jobs = connection.execute(
        "SELECT COUNT(*) AS total FROM jobs"
    ).fetchone()["total"]

    total_cvs = connection.execute(
        "SELECT COUNT(*) AS total FROM cvs"
    ).fetchone()["total"]

    total_applications = connection.execute(
        "SELECT COUNT(*) AS total FROM applications"
    ).fetchone()["total"]

    recent_users = connection.execute(
        """
        SELECT
            u.user_id,
            u.email,
            u.role,
            u.created_at,
            p.full_name
        FROM users u
        LEFT JOIN student_profiles p
            ON u.user_id = p.user_id
        ORDER BY u.created_at DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_students=total_students,
        total_admins=total_admins,
        total_jobs=total_jobs,
        total_cvs=total_cvs,
        total_applications=total_applications,
        recent_users=recent_users
    )


# =========================================================
# ADMIN USER LIST
# =========================================================

@app.route("/admin/users")
def admin_users():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    role = request.args.get(
        "role",
        ""
    ).strip()

    connection = get_connection()

    sql = """
        SELECT
            u.user_id,
            u.email,
            u.role,
            u.created_at,
            p.full_name,
            p.major
        FROM users u
        LEFT JOIN student_profiles p
            ON u.user_id = p.user_id
        WHERE 1 = 1
    """

    params = []

    if keyword:
        sql += """
            AND (
                u.email LIKE ?
                OR p.full_name LIKE ?
                OR p.major LIKE ?
            )
        """

        search = f"%{keyword}%"

        params.extend([
            search,
            search,
            search
        ])

    if role:
        sql += " AND u.role = ?"
        params.append(role)

    sql += " ORDER BY u.created_at DESC"

    users = connection.execute(
        sql,
        params
    ).fetchall()

    connection.close()

    return render_template(
        "admin/users.html",
        users=users,
        keyword=keyword,
        selected_role=role
    )


# =========================================================
# ADMIN USER DETAIL
# =========================================================

@app.route("/admin/users/<int:user_id>")
def admin_user_detail(user_id):

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            u.user_id,
            u.email,
            u.role,
            u.created_at,
            p.full_name,
            p.date_of_birth,
            p.major,
            p.bio
        FROM users u
        LEFT JOIN student_profiles p
            ON u.user_id = p.user_id
        WHERE u.user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        return "Không tìm thấy tài khoản.", 404

    skills = connection.execute(
        """
        SELECT s.name
        FROM student_skills ss
        JOIN skills s
            ON ss.skill_id = s.skill_id
        WHERE ss.user_id = ?
        ORDER BY s.name
        """,
        (user_id,)
    ).fetchall()

    cvs = connection.execute(
        """
        SELECT
            cv_id,
            file_name,
            created_at
        FROM cvs
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "admin/user_detail.html",
        user=user,
        skills=skills,
        cvs=cvs
    )


# =========================================================
# ADMIN CHANGE USER ROLE
# =========================================================

@app.route(
    "/admin/users/<int:user_id>/role",
    methods=["POST"]
)
def admin_change_user_role(user_id):

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    new_role = request.form.get(
        "role",
        ""
    ).strip()

    if new_role not in (
        "student",
        "admin"
    ):
        return "Role không hợp lệ.", 400

    # Không cho admin tự hạ quyền chính mình
    if user_id == session["user_id"]:
        return (
            "Bạn không thể tự thay đổi quyền "
            "của tài khoản đang đăng nhập.",
            400
        )

    connection = get_connection()

    user = connection.execute(
        """
        SELECT user_id
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        return "Không tìm thấy tài khoản.", 404

    connection.execute(
        """
        UPDATE users
        SET role = ?
        WHERE user_id = ?
        """,
        (
            new_role,
            user_id
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for(
            "admin_user_detail",
            user_id=user_id
        )
    )


# =========================================================
# ADMIN DELETE USER
# =========================================================

@app.route(
    "/admin/users/<int:user_id>/delete",
    methods=["POST"]
)
def admin_delete_user(user_id):

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    # Không cho xóa chính mình
    if user_id == session["user_id"]:
        return (
            "Bạn không thể xóa tài khoản "
            "đang đăng nhập.",
            400
        )

    connection = get_connection()

    user = connection.execute(
        """
        SELECT user_id
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        return "Không tìm thấy tài khoản.", 404

    try:

        # Các bảng liên quan
        connection.execute(
            "DELETE FROM recommendations WHERE user_id = ?",
            (user_id,)
        )

        connection.execute(
            "DELETE FROM applications WHERE user_id = ?",
            (user_id,)
        )

        connection.execute(
            "DELETE FROM favourites WHERE user_id = ?",
            (user_id,)
        )

        connection.execute(
            "DELETE FROM student_skills WHERE user_id = ?",
            (user_id,)
        )

        connection.execute(
            "DELETE FROM cvs WHERE user_id = ?",
            (user_id,)
        )

        connection.execute(
            "DELETE FROM student_profiles WHERE user_id = ?",
            (user_id,)
        )

        connection.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )

        connection.commit()

    except Exception as error:

        connection.rollback()
        connection.close()

        print(
            "DELETE USER ERROR:",
            repr(error)
        )

        return "Không thể xóa tài khoản.", 500

    connection.close()

    return redirect(
        url_for("admin_users")
    )
# =========================================================
# ADMIN - ADD USER
# =========================================================

@app.route("/admin/users/add", methods=["GET", "POST"])
def admin_add_user():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

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

        major = request.form.get(
            "major", ""
        ).strip()

        role = request.form.get(
            "role", "student"
        ).strip()

        if not full_name or not email or not password:
            return render_template(
                "admin/add_user.html",
                message="Vui lòng nhập đầy đủ thông tin."
            )

        if len(password) < 6:
            return render_template(
                "admin/add_user.html",
                message="Mật khẩu phải có ít nhất 6 ký tự."
            )

        if role not in ("student", "admin"):
            role = "student"

        connection = get_connection()

        existing_user = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()

            return render_template(
                "admin/add_user.html",
                message="Email này đã tồn tại."
            )

        try:

            cursor = connection.execute(
                """
                INSERT INTO users
                    (email, password, role)
                VALUES (?, ?, ?)
                """,
                (
                    email,
                    generate_password_hash(password),
                    role
                )
            )

            user_id = cursor.lastrowid

            connection.execute(
                """
                INSERT INTO student_profiles
                    (user_id, full_name, major)
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    full_name,
                    major
                )
            )

            connection.commit()

        except Exception as error:

            connection.rollback()
            connection.close()

            print(
                "ADMIN ADD USER ERROR:",
                repr(error)
            )

            return render_template(
                "admin/add_user.html",
                message="Không thể tạo tài khoản."
            )

        connection.close()

        return redirect(
            url_for("admin_users")
        )

    return render_template(
        "admin/add_user.html"
    )
@app.route(
    "/admin/users/<int:user_id>/edit",
    methods=["GET", "POST"]
)
def admin_edit_user(user_id):

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            u.user_id,
            u.email,
            u.role,
            p.full_name,
            p.major,
            p.date_of_birth,
            p.bio
        FROM users u
        LEFT JOIN student_profiles p
            ON u.user_id = p.user_id
        WHERE u.user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        return "Không tìm thấy tài khoản.", 404

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        major = request.form.get(
            "major", ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth", ""
        ).strip()

        bio = request.form.get(
            "bio", ""
        ).strip()

        role = request.form.get(
            "role", user["role"]
        ).strip()

        if not full_name or not email:
            connection.close()

            return "Họ tên và email không được để trống.", 400

        if role not in ("student", "admin"):
            role = user["role"]

        # Không cho tự hạ quyền chính mình
        if (
            user_id == session["user_id"]
            and role != "admin"
        ):
            connection.close()

            return (
                "Bạn không thể tự hạ quyền "
                "tài khoản Admin đang đăng nhập.",
                400
            )

        duplicate = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = ?
              AND user_id != ?
            """,
            (email, user_id)
        ).fetchone()

        if duplicate:
            connection.close()
            return "Email đã được tài khoản khác sử dụng.", 400

        try:

            connection.execute(
                """
                UPDATE users
                SET email = ?,
                    role = ?
                WHERE user_id = ?
                """,
                (
                    email,
                    role,
                    user_id
                )
            )

            connection.execute(
                """
                INSERT INTO student_profiles
                (
                    user_id,
                    full_name,
                    major,
                    date_of_birth,
                    bio
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(user_id)
                DO UPDATE SET
                    full_name = excluded.full_name,
                    major = excluded.major,
                    date_of_birth = excluded.date_of_birth,
                    bio = excluded.bio
                """,
                (
                    user_id,
                    full_name,
                    major,
                    date_of_birth or None,
                    bio
                )
            )

            connection.commit()

        except Exception as error:

            connection.rollback()
            connection.close()

            print("EDIT USER ERROR:", repr(error))

            return "Không thể cập nhật tài khoản.", 500

        connection.close()

        # Nếu sửa chính mình thì cập nhật session
        if user_id == session["user_id"]:
            session["email"] = email
            session["role"] = role

        return redirect(
            url_for(
                "admin_user_detail",
                user_id=user_id
            )
        )

    connection.close()

    return render_template(
        "admin/edit_user.html",
        user=user
    )
@app.route("/admin/export/excel")
def admin_export_excel():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    connection = get_connection()

    wb = Workbook()

    # ==========================
    # 1. USERS
    # ==========================
    ws_users = wb.active
    ws_users.title = "Users"

    ws_users.append([
        "User ID",
        "Full Name",
        "Email",
        "Role",
        "Major",
        "Date of Birth",
        "Created At"
    ])

    users = connection.execute("""
        SELECT
            u.user_id,
            p.full_name,
            u.email,
            u.role,
            p.major,
            p.date_of_birth,
            u.created_at
        FROM users u
        LEFT JOIN student_profiles p
            ON u.user_id = p.user_id
        ORDER BY u.user_id
    """).fetchall()

    for user in users:
        ws_users.append([
            user["user_id"],
            user["full_name"],
            user["email"],
            user["role"],
            user["major"],
            user["date_of_birth"],
            user["created_at"]
        ])

    # ==========================
    # 2. JOBS
    # ==========================
    ws_jobs = wb.create_sheet("Jobs")

    ws_jobs.append([
        "Job ID",
        "Title",
        "Company",
        "Category",
        "Location",
        "Job Type",
        "Level",
        "Experience",
        "Salary Min",
        "Salary Max",
        "Status",
        "Created At"
    ])

    jobs = connection.execute("""
        SELECT
            job_id,
            title,
            company,
            category,
            location,
            job_type,
            level,
            experience,
            salary_min,
            salary_max,
            status,
            created_at
        FROM jobs
        ORDER BY job_id
    """).fetchall()

    for job in jobs:
        ws_jobs.append(list(job))

    # ==========================
    # 3. APPLICATIONS
    # ==========================
    ws_app = wb.create_sheet("Applications")

    ws_app.append([
        "Application ID",
        "User ID",
        "Job ID",
        "Status",
        "Applied At",
        "Note"
    ])

    applications = connection.execute("""
        SELECT
            id,
            user_id,
            job_id,
            status,
            applied_at,
            note
        FROM applications
        ORDER BY id
    """).fetchall()

    for application in applications:
        ws_app.append(list(application))

    # ==========================
    # 4. RECOMMENDATIONS
    # ==========================
    ws_rec = wb.create_sheet("Recommendations")

    ws_rec.append([
        "Recommendation ID",
        "User ID",
        "Job ID",
        "Match Score",
        "Reason",
        "Created At"
    ])

    recommendations = connection.execute("""
        SELECT
            id,
            user_id,
            job_id,
            match_score,
            reason,
            created_at
        FROM recommendations
        ORDER BY id
    """).fetchall()

    for recommendation in recommendations:
        ws_rec.append(list(recommendation))

    connection.close()

    # ==========================
    # FORMAT EXCEL
    # ==========================
    for worksheet in wb.worksheets:

        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        worksheet.freeze_panes = "A2"

        # Tự chỉnh độ rộng cột
        for column in worksheet.columns:

            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:

                if cell.value is not None:
                    length = len(str(cell.value))

                    if length > max_length:
                        max_length = length

            worksheet.column_dimensions[
                column_letter
            ].width = min(max_length + 3, 45)

    # ==========================
    # SAVE TO MEMORY
    # ==========================
    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="IT_Career_Match_Admin_Data.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

# =========================================================
# ADMIN - JOB MANAGEMENT
# =========================================================

@app.route("/admin/jobs")
def admin_jobs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip().lower()

    if status not in ("", "active", "inactive"):
        status = ""

    connection = get_connection()

    where = ["1=1"]
    params = []

    if q:
        where.append(
            "(title LIKE ? OR company LIKE ? OR category LIKE ?)"
        )
        keyword = f"%{q}%"
        params.extend([keyword, keyword, keyword])

    if status:
        where.append("COALESCE(status, 'active') = ?")
        params.append(status)

    sql = """
        SELECT *
        FROM jobs
        WHERE """ + " AND ".join(where) + """
        ORDER BY created_at DESC, job_id DESC
    """

    jobs_data = connection.execute(sql, params).fetchall()

    stats = connection.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN COALESCE(status, 'active') = 'active'
                THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN status = 'inactive'
                THEN 1 ELSE 0 END) AS inactive
        FROM jobs
    """).fetchone()

    connection.close()

    return render_template(
        "admin/jobs.html",
        jobs=jobs_data,
        stats=stats,
        q=q,
        selected_status=status
    )


@app.route("/admin/jobs/<int:job_id>/status", methods=["POST"])
def admin_job_status(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Bạn không có quyền truy cập.", 403

    new_status = request.form.get("status", "")

    if new_status not in ("active", "inactive"):
        return "Trạng thái không hợp lệ.", 400

    connection = get_connection()

    cursor = connection.execute("""
        UPDATE jobs
        SET status = ?
        WHERE job_id = ?
    """, (new_status, job_id))

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return "Không tìm thấy công việc.", 404

    return redirect(url_for("admin_jobs"))
def chatbot_normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )
    text = text.replace("đ", "d")
    text = re.sub(r"[^a-z0-9+#/.\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


CHATBOT_KNOWLEDGE = [
    {
        "keywords": [
            "viet cv", "lam cv", "cv it",
            "ho so xin viec", "resume"
        ],
        "reply": (
            "📄 CÁCH VIẾT CV IT\n\n"
            "1. Giới thiệu ngắn gọn bản thân và mục tiêu nghề nghiệp.\n"
            "2. Liệt kê kỹ năng lập trình và công nghệ đã học.\n"
            "3. Trình bày 2–3 dự án thực tế, nêu rõ vai trò của bạn.\n"
            "4. Thêm GitHub, portfolio và các chứng chỉ liên quan.\n"
            "5. Kiểm tra lỗi chính tả trước khi gửi.\n\n"
            "Bạn cũng có thể tải CV lên IT Career Match "
            "để hệ thống phân tích kỹ năng và gợi ý việc làm."
        )
    },
    {
        "keywords": [
            "backend", "back end",
            "flask", "django", "spring boot"
        ],
        "reply": (
            "💻 LỘ TRÌNH BACKEND DEVELOPER\n\n"
            "1. Học Python, Java, C# hoặc JavaScript.\n"
            "2. Nắm vững OOP và cấu trúc dữ liệu.\n"
            "3. Học SQL và thiết kế cơ sở dữ liệu.\n"
            "4. Xây dựng REST API với Flask, FastAPI hoặc Spring Boot.\n"
            "5. Học Authentication, Testing, Git và Docker.\n"
            "6. Triển khai một dự án thực tế lên server.\n\n"
            "Dự án gợi ý: Hệ thống quản lý tuyển dụng."
        )
    },
    {
        "keywords": [
            "frontend", "front end",
            "react", "vue", "html css"
        ],
        "reply": (
            "🎨 LỘ TRÌNH FRONTEND DEVELOPER\n\n"
            "1. HTML, CSS và JavaScript.\n"
            "2. Responsive Design và Flexbox/Grid.\n"
            "3. Git và GitHub.\n"
            "4. React hoặc Vue.\n"
            "5. REST API, xử lý form và quản lý state.\n"
            "6. Accessibility, Testing và tối ưu hiệu năng.\n\n"
            "Dự án gợi ý: Portfolio và website tìm việc IT."
        )
    },
    {
        "keywords": [
            "machine learning", "ai/ml",
            "tri tue nhan tao", "hoc may",
            "data science"
        ],
        "reply": (
            "🤖 LỘ TRÌNH AI / MACHINE LEARNING\n\n"
            "1. Học Python và NumPy, pandas.\n"
            "2. Ôn xác suất thống kê và đại số tuyến tính.\n"
            "3. Học Supervised và Unsupervised Learning.\n"
            "4. Thực hành scikit-learn.\n"
            "5. Tìm hiểu đánh giá mô hình: Accuracy, Precision, Recall, F1.\n"
            "6. Xây dựng dự án ML và triển khai lên web.\n\n"
            "Dự án gợi ý: Hệ thống gợi ý việc làm theo CV."
        )
    },
    {
        "keywords": [
            "cybersecurity", "an ninh mang",
            "bao mat", "security"
        ],
        "reply": (
            "🔐 LỘ TRÌNH CYBERSECURITY\n\n"
            "1. Nắm vững mạng máy tính và TCP/IP.\n"
            "2. Học Linux và quản trị hệ thống.\n"
            "3. Học Python hoặc Bash để tự động hóa.\n"
            "4. Tìm hiểu bảo mật web và OWASP Top 10.\n"
            "5. Thực hành trong môi trường lab được cho phép.\n"
            "6. Học phân tích log, giám sát và ứng phó sự cố."
        )
    },
    {
        "keywords": [
            "devops", "cloud", "docker",
            "kubernetes", "aws"
        ],
        "reply": (
            "☁️ LỘ TRÌNH DEVOPS / CLOUD\n\n"
            "1. Học Linux, mạng máy tính và Git.\n"
            "2. Làm quen Bash hoặc Python.\n"
            "3. Học Docker và container.\n"
            "4. Xây dựng CI/CD với GitHub Actions.\n"
            "5. Tìm hiểu AWS, Azure hoặc Google Cloud.\n"
            "6. Học Kubernetes, Monitoring và Logging."
        )
    },
    {
        "keywords": [
            "data analyst", "phan tich du lieu",
            "power bi", "sql"
        ],
        "reply": (
            "📊 LỘ TRÌNH DATA ANALYST\n\n"
            "1. Học Excel và SQL.\n"
            "2. Học Python với pandas, NumPy.\n"
            "3. Làm sạch và phân tích dữ liệu.\n"
            "4. Trực quan hóa bằng Matplotlib hoặc Power BI.\n"
            "5. Học thống kê cơ bản.\n"
            "6. Xây dựng dashboard và portfolio dữ liệu."
        )
    },
    {
        "keywords": [
            "phong van", "interview",
            "xin viec", "thuc tap"
        ],
        "reply": (
            "🎯 CHUẨN BỊ PHỎNG VẤN IT\n\n"
            "1. Ôn kiến thức nền tảng của vị trí ứng tuyển.\n"
            "2. Luyện giải thích các dự án trong CV.\n"
            "3. Ôn Git, SQL, OOP và DSA ở mức phù hợp.\n"
            "4. Chuẩn bị ví dụ về cách giải quyết vấn đề.\n"
            "5. Luyện giới thiệu bản thân bằng tiếng Anh.\n"
            "6. Tìm hiểu công ty và mô tả công việc."
        )
    },
    {
        "keywords": [
            "tai cv", "upload cv", "phan tich cv",
            "goi y viec lam", "su dung website",
            "it career match"
        ],
        "reply": (
            "🚀 SỬ DỤNG IT CAREER MATCH\n\n"
            "1. Đăng nhập tài khoản sinh viên.\n"
            "2. Cập nhật hồ sơ cá nhân và kỹ năng.\n"
            "3. Tải CV PDF hoặc DOCX lên hệ thống.\n"
            "4. Xem kết quả phân tích CV.\n"
            "5. Khám phá danh sách công việc được gợi ý.\n"
            "6. So sánh kỹ năng hiện có với yêu cầu tuyển dụng.\n\n"
            "Điểm phù hợp là kết quả ước tính của hệ thống, "
            "không đảm bảo bạn sẽ được tuyển dụng."
        )
    },
    {
        "keywords": [
            "xin chao", "hello", "hi",
            "chao ban"
        ],
        "reply": (
            "Xin chào! 👋\n\n"
            "Mình là IT Career Assistant.\n"
            "Bạn có thể hỏi mình về CV, Backend, Frontend, "
            "AI/ML, Data, Cybersecurity, DevOps hoặc "
            "cách sử dụng IT Career Match."
        )
    }
]


def chatbot_get_reply(message):
    normalized = chatbot_normalize(message)

    best_score = 0
    best_reply = None

    for item in CHATBOT_KNOWLEDGE:
        score = 0

        for keyword in item["keywords"]:
            normalized_keyword = chatbot_normalize(keyword)

            if normalized_keyword in normalized:
                score = max(score, len(normalized_keyword))

        if score > best_score:
            best_score = score
            best_reply = item["reply"]

    if best_reply:
        return best_reply

    return (
        "Mình chưa hiểu rõ câu hỏi của bạn. 🤔\n\n"
        "Bạn có thể hỏi về:\n"
        "• Cách viết CV IT\n"
        "• Lộ trình Backend / Frontend\n"
        "• AI và Machine Learning\n"
        "• Cybersecurity / DevOps\n"
        "• Chuẩn bị phỏng vấn\n"
        "• Cách sử dụng IT Career Match\n\n"
        "Bạn hãy thử diễn đạt câu hỏi cụ thể hơn nhé!"
    )


@app.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Dữ liệu không hợp lệ."
        }), 400

    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({
            "error": "Tin nhắn phải là chuỗi văn bản."
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "error": "Vui lòng nhập câu hỏi."
        }), 400

    if len(message) > 500:
        return jsonify({
            "error": "Câu hỏi không được vượt quá 500 ký tự."
        }), 400

    reply = chatbot_get_reply(message)

    return jsonify({
        "reply": reply
    })
# =========================================================
# RUN LOCAL
# =========================================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )