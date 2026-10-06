import os
from ai.recommender import recommend_jobs, predict_career
from ai.text_preprocessing import preprocess_text
from ai.skill_extractor import extract_skills
from ai.cv_parser import read_pdf, read_docx
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import get_connection

app = Flask(__name__)
app.secret_key = "it-career-match-secret-key"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
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

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Mật khẩu xác nhận không khớp."

        connection = get_connection()

        existing_user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()
            return "Email đã được sử dụng."

        password_hash = generate_password_hash(password)

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (email, password, role)
            VALUES (?, ?, ?)
            """,
            (email, password_hash, "student")
        )

        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO student_profiles (user_id, full_name)
            VALUES (?, ?)
            """,
            (user_id, full_name)
        )

        connection.commit()
        connection.close()

        return "Đăng ký thành công!"


    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if user is None:
            return "Email không tồn tại."

        if not check_password_hash(user["password"], password):
            return "Mật khẩu không chính xác."

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