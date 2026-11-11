"""
Database Operations - Core CRUD functions for IT Career Match
Uses connection pool for production-ready connection management.
"""
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

import psycopg.sql as sql

from database.connection_pool import get_cursor, get_connection, check_db_connection


# =========================================================
# Helper Functions
# =========================================================

def _dict_row(cursor) -> List[Dict]:
    """Convert cursor results to list of dicts."""
    return [dict(row) for row in cursor.fetchall()]


def _one_row(cursor) -> Optional[Dict]:
    """Get single row as dict or None."""
    row = cursor.fetchone()
    return dict(row) if row else None


# =========================================================
# User Operations
# =========================================================

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
        return _one_row(cur)


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return _one_row(cur)


def create_user(email: str, password_hash: str, role: str, otp: str, otp_expires: datetime) -> int:
    """Create new user, return user_id."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO users (email, password, password_hash, role, otp_code, otp_expires, is_verified, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """, (email.lower(), password_hash, password_hash, role, otp, otp_expires, False, datetime.utcnow()))
        return cur.fetchone()["user_id"]


def verify_otp(email: str, otp_input: str) -> tuple[bool, str]:
    """Verify OTP code. Returns (success, message)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT user_id, otp_code, otp_expires, is_verified
            FROM users WHERE email = %s
        """, (email.lower(),))
        user = _one_row(cur)

    if not user:
        return False, "Email không tồn tại"

    if user["is_verified"]:
        return False, "Tài khoản đã được xác thực"

    if not user["otp_code"] or not user["otp_expires"]:
        return False, "Mã OTP đã hết hạn hoặc không tồn tại. Yêu cầu gửi lại."

    if datetime.utcnow() > user["otp_expires"]:
        return False, "Mã OTP đã hết hạn. Yêu cầu gửi lại."

    if user["otp_code"] != otp_input:
        return False, "Mã OTP không đúng"

    return True, "Xác thực thành công"


def update_user_verified(email: str):
    """Mark user as verified."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE users SET is_verified = TRUE, otp_code = NULL, otp_expires = NULL
            WHERE email = %s
        """, (email.lower(),))


def update_user_otp(email: str, otp: str, otp_expires: datetime):
    """Update user's OTP."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE users SET otp_code = %s, otp_expires = %s
            WHERE email = %s
        """, (otp, otp_expires, email.lower()))


def update_user_role(user_id: int, role: str):
    """Update user role."""
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE users SET role = %s WHERE user_id = %s", (role, user_id))


def update_user_password(email: str, password_hash: str):
    """Update a user's password hash."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET password = %s, password_hash = %s WHERE email = %s",
            (password_hash, password_hash, email.lower()),
        )


def delete_user(user_id: int):
    """Delete user (cascades to related tables via FK)."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))


def get_users_paginated(page: int = 1, per_page: int = 20, role: str = None,
                        verified: bool = None, search: str = None) -> Dict:
    """Get paginated users with filters."""
    offset = (page - 1) * per_page

    where_clauses = []
    params = []

    if role:
        where_clauses.append("role = %s")
        params.append(role)

    if verified is not None:
        where_clauses.append("is_verified = %s")
        params.append(verified)

    if search:
        where_clauses.append("(email ILIKE %s)")
        params.append(f"%{search}%")

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    with get_cursor() as cur:
        # Count total
        cur.execute(f"SELECT COUNT(*) as total FROM users {where_sql}", params)
        total = cur.fetchone()["total"]

        # Get items
        params_extended = params + [per_page, offset]
        cur.execute(f"""
            SELECT user_id, email, role, is_verified, created_at, last_login
            FROM users {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params_extended)
        items = _dict_row(cur)

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }


def get_recent_users(limit: int = 5) -> List[Dict]:
    """Get recently registered users."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT user_id, email, role, is_verified, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        return _dict_row(cur)


def get_user_stats() -> Dict:
    """Get user statistics for admin dashboard."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) as total_users,
                COUNT(*) FILTER (WHERE role = 'student') as students,
                COUNT(*) FILTER (WHERE role = 'admin') as admins,
                COUNT(*) FILTER (WHERE is_verified = TRUE) as verified,
                COUNT(*) FILTER (WHERE is_verified = FALSE) as unverified,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as new_this_week,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as new_this_month
            FROM users
        """)
        return _one_row(cur) or {}


# =========================================================
# Student Profile Operations
# =========================================================

def get_student_profile(user_id: int) -> Optional[Dict]:
    """Get student profile by user_id."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM student_profiles WHERE user_id = %s", (user_id,))
        return _one_row(cur)


def upsert_student_profile(user_id: int, data: Dict):
    """Insert or update student profile."""
    with get_cursor(commit=True) as cur:
        # Check if exists
        cur.execute("SELECT user_id FROM student_profiles WHERE user_id = %s", (user_id,))
        exists = cur.fetchone()

        if exists:
            # Update
            fields = []
            values = []
            for key, value in data.items():
                if value is not None:
                    fields.append(f"{key} = %s")
                    values.append(value)

            if fields:
                values.append(user_id)
                cur.execute(f"""
                    UPDATE student_profiles SET {', '.join(fields)}, updated_at = NOW()
                    WHERE user_id = %s
                """, values)
        else:
            # Insert
            data["user_id"] = user_id
            columns = list(data.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            values = list(data.values())

            cur.execute(f"""
                INSERT INTO student_profiles ({', '.join(columns)}, created_at, updated_at)
                VALUES ({placeholders}, NOW(), NOW())
            """, values)


# =========================================================
# Skills Operations
# =========================================================

def get_all_skills() -> List[Dict]:
    """Get all skills ordered by name."""
    with get_cursor() as cur:
        cur.execute("SELECT skill_id, skill_name FROM skills ORDER BY skill_name")
        return _dict_row(cur)


def get_skill_id_by_name(skill_name: str) -> Optional[int]:
    """Get skill_id by skill_name."""
    with get_cursor() as cur:
        cur.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,))
        row = _one_row(cur)
        return row["skill_id"] if row else None


def get_skill_by_id(skill_id: int) -> Optional[Dict]:
    """Get skill by ID."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM skills WHERE skill_id = %s", (skill_id,))
        return _one_row(cur)


def create_skill(skill_name: str) -> int:
    """Create new skill, return skill_id."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO skills (skill_name) VALUES (%s)
            ON CONFLICT (skill_name) DO UPDATE SET skill_name = EXCLUDED.skill_name
            RETURNING skill_id
        """, (skill_name,))
        return cur.fetchone()["skill_id"]


# =========================================================
# Student Skills Operations
# =========================================================

def get_user_skills(user_id: int) -> List[str]:
    """Get user's skill names (for chatbot/skill gap analysis)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.skill_name
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.skill_id
            WHERE ss.user_id = %s
            ORDER BY s.skill_name
        """, (user_id,))
        return [row["skill_name"] for row in _dict_row(cur)]


def get_student_skills(user_id: int) -> List[Dict]:
    """Get student's skills with skill names (full objects)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT ss.skill_id, s.skill_name
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.skill_id
            WHERE ss.user_id = %s
            ORDER BY s.skill_name
        """, (user_id,))
        return _dict_row(cur)


def add_student_skill(user_id: int, skill_id: int):
    """Add skill to student profile."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO student_skills (user_id, skill_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, skill_id) DO NOTHING
        """, (user_id, skill_id))


def remove_student_skill(user_id: int, skill_id: int):
    """Remove skill from student profile."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM student_skills WHERE user_id = %s AND skill_id = %s",
                    (user_id, skill_id))


def clear_student_skills(user_id: int):
    """Remove all skills from student profile."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM student_skills WHERE user_id = %s", (user_id,))


# =========================================================
# Job Operations
# =========================================================

def get_jobs_paginated(page: int = 1, per_page: int = 9, filters: Dict = None) -> Dict:
    """Get paginated jobs with filters. Uses psycopg.sql for safe query composition."""
    offset = (page - 1) * per_page
    filters = filters or {}

    where_conditions = []
    params = []

    # Status filter (default active for public)
    status = filters.get("status", "active")
    where_conditions.append(sql.SQL("status = %s"))
    params.append(status)

    # Keyword search
    if filters.get("keyword"):
        kw = f"%{filters['keyword']}%"
        where_conditions.append(sql.SQL(
            "(title ILIKE %s OR company ILIKE %s OR description ILIKE %s)"
        ))
        params.extend([kw, kw, kw])

    # Category
    if filters.get("category"):
        where_conditions.append(sql.SQL("category = %s"))
        params.append(filters["category"])

    # Location
    if filters.get("location"):
        where_conditions.append(sql.SQL("location ILIKE %s"))
        params.append(f"%{filters['location']}%")

    # Job type
    if filters.get("job_type"):
        where_conditions.append(sql.SQL("job_type = %s"))
        params.append(filters["job_type"])

    # Level
    if filters.get("level"):
        where_conditions.append(sql.SQL("level = %s"))
        params.append(filters["level"])

    # Salary range
    if filters.get("salary_min") is not None:
        where_conditions.append(sql.SQL("salary_max >= %s"))
        params.append(filters["salary_min"])

    if filters.get("salary_max") is not None:
        where_conditions.append(sql.SQL("salary_min <= %s"))
        params.append(filters["salary_max"])

    # Build WHERE clause safely
    if where_conditions:
        where_clause = sql.SQL("WHERE ") + sql.SQL(" AND ").join(where_conditions)
    else:
        where_clause = sql.SQL("")

    # Count query
    count_query = sql.SQL("SELECT COUNT(*) as total FROM jobs {}").format(where_clause)

    # Select query
    select_query = sql.SQL("""
        SELECT * FROM jobs {}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """).format(where_clause)

    with get_cursor() as cur:
        # Count total
        cur.execute(count_query, params)
        total = cur.fetchone()["total"]

        # Get items
        params_extended = params + [per_page, offset]
        cur.execute(select_query, params_extended)
        items = _dict_row(cur)

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }


def get_job_by_id(job_id: int) -> Optional[Dict]:
    """Get job by ID."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        return _one_row(cur)


def create_job(data: Dict) -> int:
    """Create new job, return job_id."""
    with get_cursor(commit=True) as cur:
        columns = list(data.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        values = list(data.values())

        cur.execute(f"""
            INSERT INTO jobs ({', '.join(columns)}, created_at, updated_at)
            VALUES ({placeholders}, NOW(), NOW())
            RETURNING job_id
        """, values)
        return cur.fetchone()["job_id"]


def update_job(job_id: int, data: Dict):
    """Update job."""
    with get_cursor(commit=True) as cur:
        fields = []
        values = []
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)

        if fields:
            fields.append("updated_at = NOW()")
            values.append(job_id)
            cur.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE job_id = %s", values)


def update_job_status(job_id: int, status: str):
    """Update job status."""
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE jobs SET status = %s, updated_at = NOW() WHERE job_id = %s",
                    (status, job_id))


def delete_job(job_id: int):
    """Delete job (cascades to job_skills, recommendations, favourites, applications)."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))


def get_categories() -> List[str]:
    """Get distinct job categories."""
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT category FROM jobs WHERE category IS NOT NULL ORDER BY category")
        return [row["category"] for row in _dict_row(cur)]


def get_locations() -> List[str]:
    """Get distinct job locations."""
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT location FROM jobs WHERE location IS NOT NULL ORDER BY location")
        return [row["location"] for row in _dict_row(cur)]


def search_jobs(keyword: str, limit: int = 10) -> List[Dict]:
    """Search jobs by keyword (for autocomplete)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT job_id, title, company, location
            FROM jobs
            WHERE status = 'active'
            AND (title ILIKE %s OR company ILIKE %s)
            ORDER BY created_at DESC
            LIMIT %s
        """, (f"%{keyword}%", f"%{keyword}%", limit))
        return _dict_row(cur)


# =========================================================
# Job Skills Operations
# =========================================================

def get_job_skills(job_id: int) -> List[Dict]:
    """Get skills required for a job."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT js.skill_id, s.skill_name
            FROM job_skills js
            JOIN skills s ON js.skill_id = s.skill_id
            WHERE js.job_id = %s
            ORDER BY s.skill_name
        """, (job_id,))
        return _dict_row(cur)


def add_job_skill(job_id: int, skill_id: int, importance_level: str = "required"):
    """Add skill requirement to job."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO job_skills (job_id, skill_id, importance_level)
            VALUES (%s, %s, %s)
            ON CONFLICT (job_id, skill_id) DO UPDATE SET
                importance_level = EXCLUDED.importance_level
        """, (job_id, skill_id, importance_level))


def remove_job_skill(job_id: int, skill_id: int):
    """Remove skill requirement from job."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM job_skills WHERE job_id = %s AND skill_id = %s",
                    (job_id, skill_id))


def clear_job_skills(job_id: int):
    """Remove all skill requirements from job."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM job_skills WHERE job_id = %s", (job_id,))


# =========================================================
# CV Operations
# =========================================================

def create_cv(user_id: int, filename: str, file_path: str, raw_text: str,
              extracted_skills: List[str]) -> int:
    """Create CV record."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO cvs (user_id, filename, file_path, raw_text, extracted_skills, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING cv_id
        """, (user_id, filename, file_path, raw_text, extracted_skills, datetime.utcnow()))
        return cur.fetchone()["cv_id"]


def get_user_cvs(user_id: int) -> List[Dict]:
    """Get all CVs for a user."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT cv_id, filename, file_path, extracted_skills, created_at
            FROM cvs
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        return _dict_row(cur)


def get_cv_by_id(cv_id: int) -> Optional[Dict]:
    """Get CV by ID."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM cvs WHERE cv_id = %s", (cv_id,))
        return _one_row(cur)


def delete_cv(cv_id: int):
    """Delete CV."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM cvs WHERE cv_id = %s", (cv_id,))


# =========================================================
# Recommendations Operations
# =========================================================

def create_recommendation(user_id: int, job_id: int, match_score: float,
                          skill_match: float, career_match: bool,
                          reason: str = None) -> int:
    """Create or update recommendation."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO recommendations
                (user_id, job_id, match_score, skill_match, career_match, reason, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, job_id)
            DO UPDATE SET
                match_score = EXCLUDED.match_score,
                skill_match = EXCLUDED.skill_match,
                career_match = EXCLUDED.career_match,
                reason = EXCLUDED.reason,
                created_at = EXCLUDED.created_at
            RETURNING id
        """, (
            user_id, job_id, match_score, skill_match, career_match,
            reason, datetime.utcnow(),
        ))
        return cur.fetchone()["id"]


def get_user_recommendations(user_id: int, limit: int = 10) -> List[Dict]:
    """Get user's recommendations with job details."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT r.*, j.title, j.company, j.location, j.category, j.job_type, j.level,
                   j.salary_min, j.salary_max, j.description
            FROM recommendations r
            JOIN jobs j ON r.job_id = j.job_id
            WHERE r.user_id = %s AND j.status = 'active'
            ORDER BY r.match_score DESC
            LIMIT %s
        """, (user_id, limit))
        return _dict_row(cur)


def get_recommendation_for_job(user_id: int, job_id: int) -> Optional[Dict]:
    """Get specific recommendation for user-job pair."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM recommendations WHERE user_id = %s AND job_id = %s
        """, (user_id, job_id))
        return _one_row(cur)


# =========================================================
# Favourites Operations
# =========================================================

def check_favourite(user_id: int, job_id: int) -> bool:
    """Check if job is favourited by user."""
    with get_cursor() as cur:
        cur.execute("SELECT 1 FROM favourites WHERE user_id = %s AND job_id = %s",
                    (user_id, job_id))
        return cur.fetchone() is not None


def add_favourite(user_id: int, job_id: int):
    """Add job to favourites."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO favourites (user_id, job_id, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, job_id) DO NOTHING
        """, (user_id, job_id, datetime.utcnow()))


def remove_favourite(user_id: int, job_id: int):
    """Remove job from favourites."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM favourites WHERE user_id = %s AND job_id = %s",
                    (user_id, job_id))


def get_user_favourites(user_id: int) -> List[Dict]:
    """Get user's favourite jobs with details."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT f.*, j.title, j.company, j.location, j.category, j.job_type, j.level,
                   j.salary_min, j.salary_max
            FROM favourites f
            JOIN jobs j ON f.job_id = j.job_id
            WHERE f.user_id = %s AND j.status = 'active'
            ORDER BY f.created_at DESC
        """, (user_id,))
        return _dict_row(cur)


# =========================================================
# Applications Operations
# =========================================================

def check_application(user_id: int, job_id: int) -> bool:
    """Check if user has applied to job."""
    with get_cursor() as cur:
        cur.execute("SELECT 1 FROM applications WHERE user_id = %s AND job_id = %s",
                    (user_id, job_id))
        return cur.fetchone() is not None


def create_application(user_id: int, job_id: int, cv_id: int = None,
                       cover_letter: str = "") -> int:
    """Create job application."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO applications (user_id, job_id, cv_id, cover_letter, status, applied_at)
            VALUES (%s, %s, %s, %s, 'pending', %s)
            RETURNING application_id
        """, (user_id, job_id, cv_id, cover_letter, datetime.utcnow()))
        return cur.fetchone()["application_id"]


def get_user_applications(user_id: int) -> List[Dict]:
    """Get user's applications with job details."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT a.*, j.title, j.company, j.location, j.category
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.user_id = %s
            ORDER BY a.applied_at DESC
        """, (user_id,))
        return _dict_row(cur)


def update_application_status(app_id: int, status: str):
    """Update application status."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE applications SET status = %s, updated_at = NOW()
            WHERE application_id = %s
        """, (status, app_id))


def get_applications_paginated(page: int = 1, per_page: int = 20, status: str = None) -> Dict:
    """Get paginated applications (admin view)."""
    offset = (page - 1) * per_page

    where_clauses = []
    params = []

    if status:
        where_clauses.append("a.status = %s")
        params.append(status)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    with get_cursor() as cur:
        cur.execute(f"""
            SELECT COUNT(*) as total
            FROM applications a {where_sql}
        """, params)
        total = cur.fetchone()["total"]

        params_extended = params + [per_page, offset]
        cur.execute(f"""
            SELECT a.*, u.email, j.title as job_title, j.company
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            JOIN jobs j ON a.job_id = j.job_id
            {where_sql}
            ORDER BY a.applied_at DESC
            LIMIT %s OFFSET %s
        """, params_extended)
        items = _dict_row(cur)

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page
    }


def get_recent_applications(limit: int = 5) -> List[Dict]:
    """Get recent applications."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT a.*, u.email, j.title as job_title
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            JOIN jobs j ON a.job_id = j.job_id
            ORDER BY a.applied_at DESC
            LIMIT %s
        """, (limit,))
        return _dict_row(cur)


def get_application_stats() -> Dict:
    """Get application statistics."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                COUNT(*) FILTER (WHERE status = 'accepted') as accepted,
                COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                COUNT(*) FILTER (WHERE status = 'withdrawn') as withdrawn,
                COUNT(*) FILTER (WHERE applied_at >= NOW() - INTERVAL '7 days') as this_week,
                COUNT(*) FILTER (WHERE applied_at >= NOW() - INTERVAL '30 days') as this_month
            FROM applications
        """)
        return _one_row(cur) or {}


# =========================================================
# Job Stats (Admin)
# =========================================================

def get_job_stats() -> Dict:
    """Get job statistics."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'active') as active,
                COUNT(*) FILTER (WHERE status = 'inactive') as inactive,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as this_week,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as this_month
            FROM jobs
        """)
        return _one_row(cur) or {}


def get_recent_jobs(limit: int = 5) -> List[Dict]:
    """Get recent jobs."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT job_id, title, company, location, category, status, created_at
            FROM jobs
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        return _dict_row(cur)


def get_all_applications() -> List[Dict]:
    """Get all applications (admin view)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT a.*, u.email, j.title as job_title, j.company
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            JOIN jobs j ON a.job_id = j.job_id
            ORDER BY a.applied_at DESC
        """)
        return _dict_row(cur)


def get_application_by_id(app_id: int) -> Optional[Dict]:
    """Get application by ID with full details."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT a.*, u.email, u.user_id as applicant_id,
                   j.title as job_title, j.company, j.location,
                   cv.filename as cv_filename
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            JOIN jobs j ON a.job_id = j.job_id
            LEFT JOIN cvs cv ON a.cv_id = cv.cv_id
            WHERE a.application_id = %s
        """, (app_id,))
        return _one_row(cur)


# =========================================================
# Analytics Queries
# =========================================================

def get_jobs_by_category() -> List[Dict]:
    """Get job count by category."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT category, COUNT(*) as count
            FROM jobs
            WHERE status = 'active' AND category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """)
        return _dict_row(cur)


def get_jobs_by_location() -> List[Dict]:
    """Get job count by location."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT location, COUNT(*) as count
            FROM jobs
            WHERE status = 'active' AND location IS NOT NULL
            GROUP BY location
            ORDER BY count DESC
            LIMIT 15
        """)
        return _dict_row(cur)


def get_jobs_by_type() -> List[Dict]:
    """Get job count by job_type."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT job_type, COUNT(*) as count
            FROM jobs
            WHERE status = 'active' AND job_type IS NOT NULL
            GROUP BY job_type
            ORDER BY count DESC
        """)
        return _dict_row(cur)


def get_applications_by_month(months: int = 12) -> List[Dict]:
    """Get application count by month."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                TO_CHAR(applied_at, 'YYYY-MM') as month,
                COUNT(*) as count
            FROM applications
            WHERE applied_at >= NOW() - INTERVAL '%s months'
            GROUP BY TO_CHAR(applied_at, 'YYYY-MM')
            ORDER BY month
        """, (months,))
        return _dict_row(cur)


def get_top_skills_demand(limit: int = 15) -> List[Dict]:
    """Get most demanded skills from job requirements."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.skill_name, COUNT(DISTINCT js.job_id) as job_count
            FROM job_skills js
            JOIN skills s ON js.skill_id = s.skill_id
            JOIN jobs j ON js.job_id = j.job_id
            WHERE j.status = 'active'
            GROUP BY s.skill_id, s.skill_name
            ORDER BY job_count DESC
            LIMIT %s
        """, (limit,))
        return _dict_row(cur)


def get_top_skills_supply(limit: int = 15) -> List[Dict]:
    """Get most common skills in student profiles."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.skill_name, COUNT(DISTINCT ss.user_id) as student_count
            FROM student_skills ss
            JOIN skills s ON ss.skill_id = s.skill_id
            GROUP BY s.skill_id, s.skill_name
            ORDER BY student_count DESC
            LIMIT %s
        """, (limit,))
        return _dict_row(cur)


# =========================================================
# Chat History
# =========================================================

def save_chat_message(user_id: int, message: str, is_bot: bool = False):
    """Save chat message to history."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO chat_history (user_id, message, is_bot, created_at)
            VALUES (%s, %s, %s, %s)
        """, (user_id, message, is_bot, datetime.utcnow()))


def get_chat_history(user_id: int, limit: int = 50) -> List[Dict]:
    """Get user's chat history."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT message, is_bot, created_at
            FROM chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        return list(reversed(_dict_row(cur)))  # Return chronological


# =========================================================
# Settings
# =========================================================

def get_settings() -> Dict:
    """Get all settings."""
    with get_cursor() as cur:
        cur.execute("SELECT setting_key, setting_value FROM settings")
        return {row["setting_key"]: row["setting_value"] for row in _dict_row(cur)}


def update_setting(key: str, value: str):
    """Update setting."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO settings (setting_key, setting_value, updated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (setting_key) DO UPDATE SET
                setting_value = EXCLUDED.setting_value,
                updated_at = EXCLUDED.updated_at
        """, (key, value, datetime.utcnow()))


# =========================================================
# Export Functions
# =========================================================

def export_users_csv() -> str:
    """Export users to CSV string."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT user_id, email, role, is_verified, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """)
        rows = _dict_row(cur)

    import csv
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["user_id", "email", "role", "is_verified", "created_at", "last_login"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def export_jobs_csv() -> str:
    """Export jobs to CSV string."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT job_id, title, company, location, category, job_type, level,
                   salary_min, salary_max, status, created_at
            FROM jobs
            ORDER BY created_at DESC
        """)
        rows = _dict_row(cur)

    import csv
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["job_id", "title", "company", "location", "category",
                                                 "job_type", "level", "salary_min", "salary_max",
                                                 "status", "created_at"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def export_applications_csv() -> str:
    """Export applications to CSV string."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT a.application_id, u.email, j.title as job_title, j.company,
                   a.status, a.applied_at, a.cv_id
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            JOIN jobs j ON a.job_id = j.job_id
            ORDER BY a.applied_at DESC
        """)
        rows = _dict_row(cur)

    import csv
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["application_id", "email", "job_title", "company",
                                                 "status", "applied_at", "cv_id"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


# =========================================================
# Initialize: Ensure skills table has data
# =========================================================

def ensure_default_skills():
    """Ensure skills table has default IT skills."""
    from ai.skill_extractor import SKILL_LIST

    with get_cursor(commit=True) as cur:
        for skill in SKILL_LIST:
            cur.execute("""
                INSERT INTO skills (skill_name) VALUES (%s)
                ON CONFLICT (skill_name) DO NOTHING
            """, (skill,))


if __name__ == "__main__":
    # Test connection
    print("Testing database connection...")
    if check_db_connection():
        print("✓ Database connected")

        # Test a query
        with get_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM users")
            print(f"Users: {cur.fetchone()['count']}")

            cur.execute("SELECT COUNT(*) as count FROM jobs")
            print(f"Jobs: {cur.fetchone()['count']}")

            cur.execute("SELECT COUNT(*) as count FROM skills")
            print(f"Skills: {cur.fetchone()['count']}")
    else:
        print("✗ Database connection failed")