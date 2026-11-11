"""
Jobs routes - Job listing, search, detail, admin management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from functools import wraps

from database.database import (
    get_jobs_paginated,
    get_job_by_id,
    create_job,
    update_job,
    delete_job,
    get_job_skills,
    add_job_skill,
    remove_job_skill,
    get_all_skills,
    get_categories,
    get_locations,
    search_jobs,
    get_user_cvs,
    get_cv_by_id,
)
from ai.recommender import recommend_jobs_for_user

jobs_bp = Blueprint("jobs", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để truy cập", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("user_role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@jobs_bp.route("/")
def list_jobs():
    """Public job listing with search and filters."""
    page = request.args.get("page", 1, type=int)
    per_page = 9

    # Filters
    filters = {
        "keyword": request.args.get("keyword", "").strip(),
        "category": request.args.get("category", "").strip(),
        "location": request.args.get("location", "").strip(),
        "job_type": request.args.get("job_type", "").strip(),
        "level": request.args.get("level", "").strip(),
        "salary_min": request.args.get("salary_min", type=int),
        "salary_max": request.args.get("salary_max", type=int),
    }

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}

    # Only show active jobs for public
    filters["status"] = "active"

    result = get_jobs_paginated(page=page, per_page=per_page, filters=filters)

    categories = get_categories()
    locations = get_locations()
    job_types = ["Full-time", "Part-time", "Internship", "Contract", "Remote"]
    levels = ["Intern", "Fresher", "Junior", "Mid", "Senior", "Lead", "Manager"]

    return render_template("jobs.html",
        jobs=result["items"],
        pagination=result,
        filters=filters,
        categories=categories,
        locations=locations,
        job_types=job_types,
        levels=levels
    )


@jobs_bp.route("/<int:job_id>")
def job_detail(job_id):
    """Job detail page."""
    job = get_job_by_id(job_id)

    if not job:
        abort(404)

    skills = get_job_skills(job_id)

    # Check if user has favorited/applied
    is_favourite = False
    has_applied = False
    user_recommendation = None
    cvs = []

    if "user_id" in session:
        user_id = session["user_id"]
        from database.database import (
            check_favourite,
            check_application,
            get_recommendation_for_job
        )
        is_favourite = check_favourite(user_id, job_id)
        has_applied = check_application(user_id, job_id)
        user_recommendation = get_recommendation_for_job(user_id, job_id)
        cvs = get_user_cvs(user_id)

    return render_template("job_detail.html",
        job=job,
        skills=skills,
        is_favourite=is_favourite,
        has_applied=has_applied,
        recommendation=user_recommendation,
        cvs=cvs,
    )


@jobs_bp.route("/recommendations")
@login_required
def recommendations():
    """Personalized job recommendations for logged-in user."""
    user_id = session["user_id"]

    # Get recommendations from ML
    recommended = recommend_jobs_for_user(user_id, top_k=10)

    return render_template("recommendations.html",
        recommendations=recommended
    )


@jobs_bp.route("/api/search")
def api_search():
    """AJAX endpoint for job search autocomplete/suggestions."""
    keyword = request.args.get("q", "").strip()

    if len(keyword) < 2:
        return jsonify({"jobs": []})

    jobs = search_jobs(keyword, limit=10)
    return jsonify({"jobs": jobs})


# =========================================================
# Admin Job Management
# =========================================================

@jobs_bp.route("/admin")
@admin_required
def admin_jobs():
    """Admin job management list."""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    status_filter = request.args.get("status", "all")
    filters = {}
    if status_filter != "all":
        filters["status"] = status_filter

    result = get_jobs_paginated(page=page, per_page=per_page, filters=filters)

    return render_template("admin/jobs.html",
        jobs=result["items"],
        pagination=result,
        status_filter=status_filter
    )


@jobs_bp.route("/admin/create", methods=["GET", "POST"])
@admin_required
def admin_create_job():
    """Create new job (admin)."""
    if request.method == "GET":
        skills = get_all_skills()
        return render_template("admin/job_form.html",
            job=None,
            skills=skills,
            job_types=["Full-time", "Part-time", "Internship", "Contract", "Remote"],
            levels=["Intern", "Fresher", "Junior", "Mid", "Senior", "Lead", "Manager"],
            categories=get_categories()
        )

    # POST - Create job
    data = {
        "title": request.form.get("title", "").strip(),
        "company": request.form.get("company", "").strip(),
        "location": request.form.get("location", "").strip(),
        "category": request.form.get("category", "").strip(),
        "job_type": request.form.get("job_type", "").strip(),
        "level": request.form.get("level", "").strip(),
        "salary_min": request.form.get("salary_min", type=int),
        "salary_max": request.form.get("salary_max", type=int),
        "description": request.form.get("description", "").strip(),
        "requirements": request.form.get("requirements", "").strip(),
        "benefits": request.form.get("benefits", "").strip(),
        "status": request.form.get("status", "active"),
    }

    # Validate
    required = ["title", "company", "location", "category", "job_type", "level"]
    for field in required:
        if not data[field]:
            flash(f"{field} là bắt buộc", "error")
            return redirect(url_for("jobs.admin_create_job"))

    if data["salary_min"] is not None and data["salary_max"] is not None:
        if data["salary_min"] > data["salary_max"]:
            flash("Mức lương tối thiểu không được lớn hơn tối đa", "error")
            return redirect(url_for("jobs.admin_create_job"))

    job_id = create_job(data)

    # Handle skills
    skill_ids = request.form.getlist("skills")
    for skill_id in skill_ids:
        add_job_skill(job_id, int(skill_id))

    flash("Tạo tin tuyển dụng thành công!", "success")
    return redirect(url_for("jobs.admin_jobs"))


@jobs_bp.route("/admin/<int:job_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_job(job_id):
    """Edit job (admin)."""
    job = get_job_by_id(job_id)
    if not job:
        abort(404)

    if request.method == "GET":
        skills = get_all_skills()
        job_skills = get_job_skills(job_id)
        job_skill_ids = {s["skill_id"] for s in job_skills}

        return render_template("admin/job_form.html",
            job=job,
            skills=skills,
            job_skill_ids=job_skill_ids,
            job_types=["Full-time", "Part-time", "Internship", "Contract", "Remote"],
            levels=["Intern", "Fresher", "Junior", "Mid", "Senior", "Lead", "Manager"],
            categories=get_categories()
        )

    # POST - Update job
    data = {
        "title": request.form.get("title", "").strip(),
        "company": request.form.get("company", "").strip(),
        "location": request.form.get("location", "").strip(),
        "category": request.form.get("category", "").strip(),
        "job_type": request.form.get("job_type", "").strip(),
        "level": request.form.get("level", "").strip(),
        "salary_min": request.form.get("salary_min", type=int),
        "salary_max": request.form.get("salary_max", type=int),
        "description": request.form.get("description", "").strip(),
        "requirements": request.form.get("requirements", "").strip(),
        "benefits": request.form.get("benefits", "").strip(),
        "status": request.form.get("status", "active"),
    }

    # Validate
    required = ["title", "company", "location", "category", "job_type", "level"]
    for field in required:
        if not data[field]:
            flash(f"{field} là bắt buộc", "error")
            return redirect(url_for("jobs.admin_edit_job", job_id=job_id))

    update_job(job_id, data)

    # Update skills
    from database.database import clear_job_skills
    clear_job_skills(job_id)
    skill_ids = request.form.getlist("skills")
    for skill_id in skill_ids:
        add_job_skill(job_id, int(skill_id))

    flash("Cập nhật tin tuyển dụng thành công!", "success")
    return redirect(url_for("jobs.admin_jobs"))


@jobs_bp.route("/admin/<int:job_id>/delete", methods=["POST"])
@admin_required
def admin_delete_job(job_id):
    """Delete job (admin)."""
    job = get_job_by_id(job_id)
    if not job:
        abort(404)

    delete_job(job_id)
    flash("Đã xoá tin tuyển dụng", "success")
    return redirect(url_for("jobs.admin_jobs"))


@jobs_bp.route("/admin/<int:job_id>/toggle-status", methods=["POST"])
@admin_required
def admin_toggle_job_status(job_id):
    """Toggle job active/inactive status (AJAX)."""
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found"}), 404

    new_status = "inactive" if job["status"] == "active" else "active"
    from database.database import update_job_status
    update_job_status(job_id, new_status)

    return jsonify({"success": True, "status": new_status})


# =========================================================
# User Actions (Favourite, Apply)
# =========================================================

@jobs_bp.route("/<int:job_id>/favourite", methods=["POST"])
@login_required
def toggle_favourite(job_id):
    """Add/remove job from favourites."""
    user_id = session["user_id"]

    from database.database import check_favourite, add_favourite, remove_favourite

    if check_favourite(user_id, job_id):
        remove_favourite(user_id, job_id)
        return jsonify({"success": True, "favourited": False})
    else:
        add_favourite(user_id, job_id)
        return jsonify({"success": True, "favourited": True})


@jobs_bp.route("/<int:job_id>/apply", methods=["POST"])
@login_required
def apply_job(job_id):
    """Apply to a job."""
    user_id = session["user_id"]

    from database.database import check_application, create_application, get_job_by_id

    job = get_job_by_id(job_id)
    if not job or job.get("status") != "active":
        return jsonify({"success": False, "message": "Tin tuyển dụng không tồn tại hoặc đã đóng"}), 404

    cv_id = request.form.get("cv_id", type=int)
    if not cv_id:
        return jsonify({"success": False, "message": "Vui lòng chọn CV để ứng tuyển"}), 400

    cv = get_cv_by_id(cv_id)
    if not cv or cv["user_id"] != user_id:
        return jsonify({"success": False, "message": "CV đã chọn không hợp lệ"}), 400

    if check_application(user_id, job_id):
        return jsonify({"success": False, "message": "Bạn đã ứng tuyển vào vị trí này"}), 400

    cover_letter = request.form.get("cover_letter", "").strip()

    create_application(user_id, job_id, cv_id, cover_letter)

    return jsonify({"success": True, "message": "Ứng tuyển thành công!"})


@jobs_bp.route("/my-applications")
@login_required
def my_applications():
    """User's job applications."""
    user_id = session["user_id"]

    from database.database import get_user_applications
    applications = get_user_applications(user_id)

    return render_template("my_applications.html", applications=applications)


@jobs_bp.route("/my-favourites")
@login_required
def my_favourites():
    """User's favourite jobs."""
    user_id = session["user_id"]

    from database.database import get_user_favourites
    favourites = get_user_favourites(user_id)

    return render_template("my_favourites.html", favourites=favourites)