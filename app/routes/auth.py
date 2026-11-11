"""
Auth routes - Registration, Login, OTP Verification, Logout
"""
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
import bcrypt
from werkzeug.security import check_password_hash
import secrets
from datetime import datetime, timedelta
from itsdangerous import BadSignature, URLSafeTimedSerializer

from database.database import (
    get_user_by_email,
    create_user,
    verify_otp as db_verify_otp,
    update_user_verified,
    get_user_by_id
)
from utils.email_utils import send_otp_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration with email verification."""
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    # Validation
    if not email or not password:
        flash("Email và mật khẩu là bắt buộc", "error")
        return render_template("register.html"), 400

    if password != confirm_password:
        flash("Mật khẩu xác nhận không khớp", "error")
        return render_template("register.html"), 400

    if len(password) < 8:
        flash("Mật khẩu phải có ít nhất 8 ký tự", "error")
        return render_template("register.html"), 400

    # Check existing user
    existing = get_user_by_email(email)
    if existing:
        if existing["is_verified"]:
            flash("Email đã được đăng ký", "error")
            return render_template("register.html"), 400
        else:
            # Email exists but not verified - resend OTP
            otp = str(secrets.randbelow(900000) + 100000)  # 6-digit
            otp_expires = datetime.utcnow() + timedelta(minutes=10)

            from database.database import update_user_otp
            update_user_otp(email, otp, otp_expires)

            try:
                sent, message = send_otp_email(email, otp)
                if not sent:
                    current_app.logger.error("Could not send OTP email: %s", message)
                    flash("Không gửi được email OTP. Vui lòng kiểm tra cấu hình email hoặc thử gửi lại.", "warning")
                else:
                    flash("Mã OTP mới đã được gửi đến email của bạn.", "success")
            except Exception as e:
                current_app.logger.exception("Could not send OTP email")
                flash(f"Không gửi được email: {str(e)}", "warning")

            session["pending_verification_email"] = email
            return redirect(url_for("auth.verify_otp"))

    # Hash password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Generate OTP
    otp = str(secrets.randbelow(900000) + 100000)  # 6-digit
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    # Create user
    create_user(email, hashed, "student", otp, otp_expires)

    # Send OTP email
    try:
        sent, message = send_otp_email(email, otp)
        if sent:
            flash("Đăng ký thành công! Mã OTP đã được gửi đến email của bạn.", "success")
        else:
            current_app.logger.error("Could not send OTP email: %s", message)
            flash("Đăng ký thành công nhưng không gửi được email OTP. Vui lòng thử gửi lại.", "warning")
    except Exception as e:
        current_app.logger.exception("Could not send OTP email")
        flash(f"Đăng ký thành công nhưng không gửi được email: {str(e)}", "warning")

    session["pending_verification_email"] = email
    return redirect(url_for("auth.verify_otp"))


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    """Verify OTP and activate account."""
    email = session.get("pending_verification_email")

    if not email:
        flash("Phiên hết hạn. Vui lòng đăng ký lại.", "error")
        return redirect(url_for("auth.register"))

    if request.method == "GET":
        return render_template("verify_otp.html", email=email)

    otp_input = request.form.get("otp", "").strip()

    if not otp_input:
        flash("Vui lòng nhập mã OTP", "error")
        return render_template("verify_otp.html", email=email), 400

    success, message = db_verify_otp(email, otp_input)

    if success:
        update_user_verified(email)
        session.pop("pending_verification_email", None)
        flash("Xác thực thành công! Bạn có thể đăng nhập ngay.", "success")
        return redirect(url_for("auth.login"))
    else:
        flash(message, "error")
        return render_template("verify_otp.html", email=email), 400


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    """Resend OTP to pending verification email."""
    email = session.get("pending_verification_email")

    if not email:
        return {"success": False, "message": "Không có email chờ xác thực"}, 400

    from database.database import update_user_otp
    import secrets
    from datetime import datetime, timedelta

    otp = str(secrets.randbelow(900000) + 100000)
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    update_user_otp(email, otp, otp_expires)

    try:
        sent, message = send_otp_email(email, otp)
        if not sent:
            current_app.logger.error("Could not resend OTP email: %s", message)
            return {"success": False, "message": "Không gửi được email OTP. Vui lòng thử lại sau."}, 500
        return {"success": True, "message": "Đã gửi lại mã OTP"}
    except Exception as e:
        current_app.logger.exception("Could not resend OTP email")
        return {"success": False, "message": f"Lỗi gửi email: {str(e)}"}, 500


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    remember = request.form.get("remember") == "on"

    if not email or not password:
        flash("Email và mật khẩu là bắt buộc", "error")
        return render_template("login.html"), 400

    user = get_user_by_email(email)

    if not user:
        flash("Email hoặc mật khẩu không đúng", "error")
        return render_template("login.html"), 401

    # Older accounts used Werkzeug's scrypt hashes; migrate valid logins to bcrypt.
    stored_hash = user.get("password_hash") or user.get("password")
    if not isinstance(stored_hash, str):
        current_app.logger.warning("User account has no usable password hash")
        flash("Email hoặc mật khẩu không đúng", "error")
        return render_template("login.html"), 401

    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            password_matches = bcrypt.checkpw(
                password.encode("utf-8"), stored_hash.encode("utf-8")
            )
        except ValueError:
            current_app.logger.warning("User account has a malformed bcrypt password hash")
            password_matches = False
    elif stored_hash.startswith(("scrypt:", "pbkdf2:")):
        try:
            password_matches = check_password_hash(stored_hash, password)
        except (ValueError, TypeError):
            current_app.logger.warning("User account has a malformed legacy password hash")
            password_matches = False
    else:
        current_app.logger.warning("User account has an unsupported password hash format")
        password_matches = False

    if not password_matches:
        flash("Email hoặc mật khẩu không đúng", "error")
        return render_template("login.html"), 401

    if not stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        upgraded_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        from database.database import update_user_password
        update_user_password(email, upgraded_hash)

    if not user["is_verified"]:
        from database.database import update_user_otp

        otp = str(secrets.randbelow(900000) + 100000)
        otp_expires = datetime.utcnow() + timedelta(minutes=10)
        update_user_otp(email, otp, otp_expires)

        try:
            sent, message = send_otp_email(email, otp)
            if sent:
                flash("Tài khoản chưa xác thực. Mã OTP mới đã được gửi đến email của bạn.", "warning")
            else:
                current_app.logger.error("Could not send login verification OTP: %s", message)
                flash("Tài khoản chưa xác thực và hệ thống không gửi được OTP. Vui lòng bấm gửi lại mã.", "warning")
        except Exception:
            current_app.logger.exception("Could not send login verification OTP")
            flash("Tài khoản chưa xác thực và hệ thống không gửi được OTP. Vui lòng bấm gửi lại mã.", "warning")

        session["pending_verification_email"] = email
        return redirect(url_for("auth.verify_otp"))

    # Create session
    session.clear()
    session["user_id"] = user["user_id"]
    session["user_email"] = user["email"]
    session["user_role"] = user["role"]
    session.permanent = remember

    flash("Đăng nhập thành công!", "success")

    # Redirect based on role
    if user["role"] == "admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("profile.dashboard"))


@auth_bp.route("/logout")
def logout():
    """User logout."""
    session.clear()
    flash("Đã đăng xuất", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password - send reset link or OTP for unverified accounts."""
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form.get("email", "").strip().lower()

    if not email:
        flash("Vui lòng nhập email", "error")
        return render_template("forgot_password.html"), 400

    user = get_user_by_email(email)
    if not user:
        # Keep user enumeration safe, but do not disclose whether the email exists.
        flash("Nếu email tồn tại, hướng dẫn đặt lại mật khẩu đã được gửi.", "info")
        return render_template("forgot_password.html")

    if not user["is_verified"]:
        from database.database import update_user_otp

        otp = str(secrets.randbelow(900000) + 100000)
        otp_expires = datetime.utcnow() + timedelta(minutes=10)
        update_user_otp(email, otp, otp_expires)

        try:
            sent, message = send_otp_email(email, otp)
            if sent:
                session["pending_verification_email"] = email
                flash("Tài khoản chưa xác thực email. Mã OTP đã được gửi để bạn xác thực trước khi đặt lại mật khẩu.", "warning")
                return redirect(url_for("auth.verify_otp"))

            current_app.logger.error("Could not send reset OTP email for unverified user: %s", message)
            flash("Tài khoản chưa xác thực email và hệ thống không gửi được mã OTP. Vui lòng thử lại sau.", "error")
            return render_template("forgot_password.html"), 500
        except Exception as exc:
            current_app.logger.exception("Could not send reset OTP email for unverified user")
            flash(f"Không thể gửi mã OTP: {exc}", "error")
            return render_template("forgot_password.html"), 500

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps(
        {"email": email, "password_hash": user["password_hash"]},
        salt="password-reset",
    )
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    from utils.email_utils import send_email
    sent, message = send_email(
        email,
        "Đặt lại mật khẩu - IT Career Match",
        f'<p>Để đặt lại mật khẩu, <a href="{reset_url}">nhấn vào đây</a>. '
        "Liên kết có hiệu lực trong 1 giờ.</p>",
    )
    if not sent:
        current_app.logger.error("Could not send password reset email: %s", message)
        flash("Không thể gửi email đặt lại mật khẩu. Vui lòng thử lại sau.", "error")
        return render_template("forgot_password.html"), 500

    flash("Nếu email tồn tại, hướng dẫn đặt lại mật khẩu đã được gửi.", "info")
    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password with token."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        token_data = serializer.loads(
            token,
            salt="password-reset",
            max_age=current_app.config.get("PASSWORD_RESET_TOKEN_MAX_AGE", 3600),
        )
    except BadSignature:
        flash("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "GET":
        return render_template("reset_password.html", token=token)

    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    if len(password) < 8:
        flash("Mật khẩu phải có ít nhất 8 ký tự.", "error")
        return render_template("reset_password.html", token=token), 400
    if password != confirm_password:
        flash("Mật khẩu xác nhận không khớp.", "error")
        return render_template("reset_password.html", token=token), 400

    user = get_user_by_email(token_data["email"])
    if not user or not user["is_verified"]:
        flash("Tài khoản không tồn tại hoặc chưa xác thực.", "error")
        return redirect(url_for("auth.login"))
    if user["password_hash"] != token_data["password_hash"]:
        flash("Liên kết đặt lại mật khẩu đã được sử dụng.", "error")
        return redirect(url_for("auth.forgot_password"))

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    from database.database import update_user_password
    update_user_password(token_data["email"], hashed)

    flash("Đặt lại mật khẩu thành công. Vui lòng đăng nhập.", "success")
    return redirect(url_for("auth.login"))