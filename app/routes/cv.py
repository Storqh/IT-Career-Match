"""
CV routes - Upload, parse, recommendations, gap analysis
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from functools import wraps
from pathlib import Path
import os
import uuid

from database.database import (
    get_user_cvs,
    get_cv_by_id,
    create_cv,
    delete_cv,
    get_user_by_id,
    get_student_profile,
    get_student_skills,
    get_cv_by_id as get_cv_record
)
from ai.skill_extractor import extract_skills
from ai.recommender import recommend_jobs_for_user
from ai.skill_gap import analyze_skill_gap
from utils.file_utils import allowed_file, extract_text_from_file, validate_file

cv_bp = Blueprint("cv", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để truy cập", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@cv_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_cv():
    """Upload and parse CV."""
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("upload_cv.html")

    if "cv_file" not in request.files:
        flash("Không có file được tải lên", "error")
        return redirect(url_for("cv.upload_cv"))

    file = request.files["cv_file"]

    # Validate file
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        flash(error_msg, "error")
        return redirect(url_for("cv.upload_cv"))

    # Save file with unique name to avoid overwriting
    from werkzeug.utils import secure_filename
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

    upload_folder = Path(__file__).parent.parent.parent / "uploads" / str(user_id)
    upload_folder.mkdir(parents=True, exist_ok=True)

    filepath = upload_folder / unique_filename
    file.save(filepath)

    # Extract text
    try:
        text = extract_text_from_file(filepath)
    except Exception as e:
        # Clean up file on parse error
        try:
            os.remove(filepath)
        except OSError:
            pass
        flash(f"Lỗi đọc file: {str(e)}", "error")
        return redirect(url_for("cv.upload_cv"))

    # Check for empty content
    if not text or not text.strip():
        try:
            os.remove(filepath)
        except OSError:
            pass
        flash("Không thể trích xuất nội dung từ file. File có thể bị rỗng hoặc hỏng.", "error")
        return redirect(url_for("cv.upload_cv"))

    # Extract skills
    skills = extract_skills(text)

    # Save CV record
    cv_id = create_cv(user_id, original_filename, str(filepath), text, skills)

    # Add extracted skills to profile
    from database.database import get_skill_id_by_name, add_student_skill
    for skill_name in skills:
        skill_id = get_skill_id_by_name(skill_name)
        if skill_id:
            add_student_skill(user_id, skill_id)

    flash(f"Tải lên CV thành công! Đã trích xuất {len(skills)} kỹ năng.", "success")
    return redirect(url_for("cv.my_cvs"))


@cv_bp.route("/my-cvs")
@login_required
def my_cvs():
    """List user's CVs."""
    user_id = session["user_id"]
    cvs = get_user_cvs(user_id)
    return render_template("my_cvs.html", cvs=cvs)


@cv_bp.route("/<int:cv_id>")
@login_required
def view_cv(cv_id):
    """View CV details with extracted skills."""
    user_id = session["user_id"]
    cv = get_cv_by_id(cv_id)

    if not cv or cv["user_id"] != user_id:
        abort(404)

    return render_template("view_cv.html", cv=cv)


@cv_bp.route("/<int:cv_id>/delete", methods=["POST"])
@login_required
def delete_cv_route(cv_id):
    """Delete a CV."""
    user_id = session["user_id"]
    cv = get_cv_by_id(cv_id)

    if not cv or cv["user_id"] != user_id:
        abort(404)

    # Delete file
    try:
        os.remove(cv["file_path"])
    except OSError:
        pass

    delete_cv(cv_id)
    flash("Đã xoá CV", "success")
    return redirect(url_for("cv.my_cvs"))


@cv_bp.route("/recommendations")
@login_required
def recommendations():
    """Get job recommendations based on latest CV or profile."""
    user_id = session["user_id"]

    # Get recommendations from ML
    recommended = recommend_jobs_for_user(user_id, top_k=10)

    return render_template("recommendations.html",
        recommendations=recommended
    )


@cv_bp.route("/gap-analysis/<int:job_id>")
@login_required
def gap_analysis(job_id):
    """Analyze skill gap between user profile and job requirements."""
    user_id = session["user_id"]

    from database.database import get_job_by_id, get_job_skills, get_cv_by_id

    job = get_job_by_id(job_id)
    if not job:
        abort(404)

    # Get user's latest CV for raw text (for evidence extraction)
    cvs = get_user_cvs(user_id)
    cv_raw_text = None
    if cvs:
        latest_cv = get_cv_by_id(cvs[0]["cv_id"])
        if latest_cv:
            cv_raw_text = latest_cv.get("raw_text", "")

    # Analyze gap using enhanced function
    gap_result = analyze_skill_gap(
        cv_text=None,  # Will be fetched via user_id
        job_text=None,  # Will be fetched via job_id
        job_category=job.get("category", ""),
        job_id=job_id,
        user_id=user_id,
        cv_raw_text=cv_raw_text,
        include_resources=True,
        include_learning_path=True
    )

    return render_template("gap_analysis.html",
        job=job,
        gap=gap_result,
        user_skills=gap_result.get("cv_skills", []),
        job_skills=gap_result.get("job_skills", [])
    )


@cv_bp.route("/api/parse-text", methods=["POST"])
@login_required
def parse_text():
    """Parse skills from raw text (AJAX)."""
    text = request.json.get("text", "") if request.is_json else request.form.get("text", "")

    if not text:
        return jsonify({"success": False, "message": "No text provided"}), 400

    skills = extract_skills(text)

    return jsonify({"success": True, "skills": skills})