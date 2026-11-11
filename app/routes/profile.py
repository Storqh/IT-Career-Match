"""
Profile routes - Student dashboard, profile CRUD, skills management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path

from database.database import (
    get_user_by_id,
    get_student_profile,
    upsert_student_profile,
    get_student_skills,
    add_student_skill,
    remove_student_skill,
    get_all_skills,
    get_user_cvs,
    delete_cv,
    get_cv_by_id
)
from ai.skill_extractor import extract_skills
from utils.file_utils import allowed_file, extract_text_from_file, validate_file

profile_bp = Blueprint("profile", __name__)


def login_required(f):
    """Decorator to require login."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để truy cập", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@profile_bp.route("/dashboard")
@login_required
def dashboard():
    """Student dashboard with profile summary and recommendations."""
    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    profile = get_student_profile(user_id)
    skills = get_student_skills(user_id)
    cvs = get_user_cvs(user_id)

    # Get latest recommendations
    from database.database import get_user_recommendations
    recommendations = get_user_recommendations(user_id, limit=5)

    return render_template("dashboard.html",
        user=user,
        profile=profile,
        skills=skills,
        cvs=cvs,
        recommendations=recommendations
    )


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit student profile."""
    user_id = session["user_id"]

    if request.method == "GET":
        profile = get_student_profile(user_id)
        all_skills = get_all_skills()
        student_skills = get_student_skills(user_id)
        student_skill_ids = {s["skill_id"] for s in student_skills}

        return render_template("edit_profile.html",
            profile=profile,
            all_skills=all_skills,
            student_skill_ids=student_skill_ids
        )

    # POST - Update profile
    data = {
        "full_name": request.form.get("full_name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "address": request.form.get("address", "").strip(),
        "university": request.form.get("university", "").strip(),
        "major": request.form.get("major", "").strip(),
        "graduation_year": request.form.get("graduation_year", type=int),
        "gpa": request.form.get("gpa", type=float),
        "linkedin": request.form.get("linkedin", "").strip(),
        "github": request.form.get("github", "").strip(),
        "portfolio": request.form.get("portfolio", "").strip(),
        "bio": request.form.get("bio", "").strip(),
    }

    # Validate
    if not data["full_name"]:
        flash("Họ tên là bắt buộc", "error")
        return redirect(url_for("profile.edit_profile"))

    if data["gpa"] is not None and (data["gpa"] < 0 or data["gpa"] > 4):
        flash("GPA phải từ 0 đến 4.0", "error")
        return redirect(url_for("profile.edit_profile"))

    upsert_student_profile(user_id, data)

    # Handle skills
    skill_ids = request.form.getlist("skills")
    from database.database import clear_student_skills
    clear_student_skills(user_id)
    for skill_id in skill_ids:
        add_student_skill(user_id, int(skill_id))

    flash("Cập nhật hồ sơ thành công!", "success")
    return redirect(url_for("profile.dashboard"))


@profile_bp.route("/skills/add", methods=["POST"])
@login_required
def add_skill():
    """Add a skill to student profile (AJAX)."""
    user_id = session["user_id"]
    skill_id = request.form.get("skill_id", type=int)

    if not skill_id:
        return {"success": False, "message": "Skill ID required"}, 400

    try:
        add_student_skill(user_id, skill_id)
        return {"success": True, "message": "Đã thêm kỹ năng"}
    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@profile_bp.route("/skills/remove", methods=["POST"])
@login_required
def remove_skill():
    """Remove a skill from student profile (AJAX)."""
    user_id = session["user_id"]
    skill_id = request.form.get("skill_id", type=int)

    if not skill_id:
        return {"success": False, "message": "Skill ID required"}, 400

    try:
        remove_student_skill(user_id, skill_id)
        return {"success": True, "message": "Đã xoá kỹ năng"}
    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@profile_bp.route("/cv/upload", methods=["GET", "POST"])
@login_required
def upload_cv():
    """Upload and parse CV."""
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("upload_cv.html")

    if "cv_file" not in request.files:
        flash("Không có file được tải lên", "error")
        return redirect(url_for("profile.upload_cv"))

    file = request.files["cv_file"]

    # Validate file
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        flash(error_msg, "error")
        return redirect(url_for("profile.upload_cv"))

    # Save file with unique name to avoid overwriting
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
        return redirect(url_for("profile.upload_cv"))

    # Check for empty content
    if not text or not text.strip():
        try:
            os.remove(filepath)
        except OSError:
            pass
        flash("Không thể trích xuất nội dung từ file. File có thể bị rỗng hoặc hỏng.", "error")
        return redirect(url_for("profile.upload_cv"))

    # Extract skills
    skills = extract_skills(text)

    # Save CV record
    from database.database import create_cv
    cv_id = create_cv(user_id, original_filename, str(filepath), text, skills)

    # Add extracted skills to profile
    from database.database import get_skill_id_by_name
    for skill_name in skills:
        skill_id = get_skill_id_by_name(skill_name)
        if skill_id:
            add_student_skill(user_id, skill_id)

    flash(f"Tải lên CV thành công! Đã trích xuất {len(skills)} kỹ năng.", "success")
    return redirect(url_for("profile.dashboard"))


@profile_bp.route("/cv/<int:cv_id>/delete", methods=["POST"])
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
    return redirect(url_for("profile.dashboard"))


@profile_bp.route("/cv/<int:cv_id>/view")
@login_required
def view_cv(cv_id):
    """View CV details."""
    user_id = session["user_id"]
    cv = get_cv_by_id(cv_id)

    if not cv or cv["user_id"] != user_id:
        abort(404)

    return render_template("view_cv.html", cv=cv)