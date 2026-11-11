"""
Admin routes - Dashboard, user management, job management, analytics, export
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, send_file, jsonify
from functools import wraps
from datetime import datetime, timedelta
import io
import csv

from database.database import (
    get_users_paginated,
    get_user_by_id,
    update_user_role,
    delete_user,
    get_jobs_paginated,
    get_job_by_id,
    get_applications_paginated,
    get_application_stats,
    get_user_stats,
    get_job_stats,
    export_users_csv,
    export_jobs_csv,
    export_applications_csv,
    get_recent_users,
    get_recent_jobs,
    get_recent_applications,
    get_application_by_id
)

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("user_role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/")
@admin_required
def dashboard():
    """Admin dashboard with overview statistics."""
    # Get stats
    user_stats = get_user_stats()
    job_stats = get_job_stats()
    app_stats = get_application_stats()

    # Recent activity
    from database.database import get_recent_users, get_recent_jobs, get_recent_applications
    recent_users = get_recent_users(5)
    recent_jobs = get_recent_jobs(5)
    recent_applications = get_recent_applications(5)

    return render_template("admin/dashboard.html",
        user_stats=user_stats,
        job_stats=job_stats,
        app_stats=app_stats,
        recent_users=recent_users,
        recent_jobs=recent_jobs,
        recent_applications=recent_applications
    )


# =========================================================
# User Management
# =========================================================

@admin_bp.route("/users")
@admin_required
def users():
    """User management list."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    role_filter = request.args.get("role", "all")
    status_filter = request.args.get("status", "all")
    search = request.args.get("search", "").strip()

    from database.database import get_users_paginated
    result = get_users_paginated(
        page=page,
        per_page=per_page,
        role=role_filter if role_filter != "all" else None,
        verified=(status_filter == "verified") if status_filter != "all" else None,
        search=search if search else None
    )

    return render_template("admin/users.html",
        users=result["items"],
        pagination=result,
        role_filter=role_filter,
        status_filter=status_filter,
        search=search
    )


@admin_bp.route("/users/<int:user_id>")
@admin_required
def user_detail(user_id):
    """View user detail."""
    user = get_user_by_id(user_id)
    if not user:
        abort(404)

    from database.database import get_student_profile, get_user_cvs, get_user_applications, get_user_favourites
    profile = get_student_profile(user_id)
    cvs = get_user_cvs(user_id)
    applications = get_user_applications(user_id)
    favourites = get_user_favourites(user_id)

    return render_template("admin/user_detail.html",
        user=user,
        profile=profile,
        cvs=cvs,
        applications=applications,
        favourites=favourites
    )


@admin_bp.route("/users/<int:user_id>/toggle-role", methods=["POST"])
@admin_required
def toggle_user_role(user_id):
    """Toggle user role between student/admin."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Prevent self-demotion
    if user_id == session["user_id"]:
        return jsonify({"success": False, "message": "Không thể thay đổi vai trò của chính mình"}), 400

    new_role = "admin" if user["role"] == "student" else "student"
    update_user_role(user_id, new_role)

    return jsonify({"success": True, "role": new_role})


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user_route(user_id):
    """Delete user (cascades to profiles, CVs, applications, etc.)."""
    user = get_user_by_id(user_id)
    if not user:
        abort(404)

    # Prevent self-deletion
    if user_id == session["user_id"]:
        flash("Không thể xoá chính mình", "error")
        return redirect(url_for("admin.users"))

    delete_user(user_id)
    flash("Đã xoá người dùng và tất cả dữ liệu liên quan", "success")
    return redirect(url_for("admin.users"))


# =========================================================
# Job Management (delegates to jobs blueprint for CRUD)
# =========================================================

@admin_bp.route("/jobs")
@admin_required
def admin_jobs_list():
    """Redirect to jobs blueprint admin view."""
    return redirect(url_for("jobs.admin_jobs"))


# =========================================================
# Applications Management
# =========================================================

@admin_bp.route("/applications")
@admin_required
def applications():
    """All applications management."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    status_filter = request.args.get("status", "all")

    from database.database import get_applications_paginated
    result = get_applications_paginated(
        page=page,
        per_page=per_page,
        status=status_filter if status_filter != "all" else None
    )

    return render_template("admin/applications.html",
        applications=result["items"],
        pagination=result,
        status_filter=status_filter
    )


@admin_bp.route("/applications/<int:app_id>/update-status", methods=["POST"])
@admin_required
def update_application_status(app_id):
    """Update application status."""
    from database.database import get_application_by_id, update_application_status

    app = get_application_by_id(app_id)
    if not app:
        return jsonify({"success": False, "message": "Application not found"}), 404

    new_status = request.form.get("status")
    valid_statuses = ["pending", "accepted", "rejected", "withdrawn"]

    if new_status not in valid_statuses:
        return jsonify({"success": False, "message": "Invalid status"}), 400

    update_application_status(app_id, new_status)

    return jsonify({"success": True, "status": new_status})


# =========================================================
# Analytics
# =========================================================

@admin_bp.route("/analytics")
@admin_required
def analytics():
    """Analytics dashboard."""
    from database.database import (
        get_jobs_by_category,
        get_jobs_by_location,
        get_jobs_by_type,
        get_applications_by_month,
        get_top_skills_demand,
        get_top_skills_supply
    )

    # Job distribution
    by_category = get_jobs_by_category()
    by_location = get_jobs_by_location()
    by_type = get_jobs_by_type()

    # Application trends
    apps_by_month = get_applications_by_month(12)

    # Skills demand vs supply
    demand_skills = get_top_skills_demand(15)
    supply_skills = get_top_skills_supply(15)

    return render_template("admin/analytics.html",
        by_category=by_category,
        by_location=by_location,
        by_type=by_type,
        apps_by_month=apps_by_month,
        demand_skills=demand_skills,
        supply_skills=supply_skills
    )


# =========================================================
# Export Data
# =========================================================

@admin_bp.route("/export/users")
@admin_required
def export_users():
    """Export users to CSV."""
    csv_data = export_users_csv()
    return send_file(
        io.BytesIO(csv_data.encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"users_export_{datetime.now().strftime('%Y%m%d')}.csv"
    )


@admin_bp.route("/export/jobs")
@admin_required
def export_jobs():
    """Export jobs to CSV."""
    csv_data = export_jobs_csv()
    return send_file(
        io.BytesIO(csv_data.encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"jobs_export_{datetime.now().strftime('%Y%m%d')}.csv"
    )


@admin_bp.route("/export/applications")
@admin_required
def export_applications():
    """Export applications to CSV."""
    csv_data = export_applications_csv()
    return send_file(
        io.BytesIO(csv_data.encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"applications_export_{datetime.now().strftime('%Y%m%d')}.csv"
    )


# =========================================================
# System Settings
# =========================================================

@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    """System settings."""
    if request.method == "GET":
        from database.database import get_settings
        settings = get_settings()
        return render_template("admin/settings.html", settings=settings)

    # POST - Update settings
    from database.database import update_setting
    for key, value in request.form.items():
        update_setting(key, value)

    flash("Cài đặt đã được cập nhật", "success")
    return redirect(url_for("admin.settings"))