"""
Email Utilities - Send OTP and notification emails via Brevo (Sendinblue)
"""
import os
import logging
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import Brevo SDK
try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    BREVO_AVAILABLE = True
except ImportError:
    BREVO_AVAILABLE = False
    sib_api_v3_sdk = None
    ApiException = Exception


def get_brevo_config():
    """Get Brevo API configuration from environment."""
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("BREVO_SENDER_EMAIL", "noreply@example.com")
    sender_name = os.getenv("BREVO_SENDER_NAME", "IT Career Match")

    return api_key, sender_email, sender_name


def send_email(to_email: str, subject: str, html_content: str,
               text_content: str = None) -> tuple[bool, str]:
    """
    Send email via Brevo API.
    Returns (success, message).
    """
    if not BREVO_AVAILABLE:
        return False, "Brevo SDK not installed. Run: pip install sib-api-v3-sdk"

    api_key, sender_email, sender_name = get_brevo_config()

    if not api_key:
        return False, "BREVO_API_KEY not configured"

    sender_domain = sender_email.rpartition("@")[2].lower()
    if not sender_domain or sender_domain in {"example.com", "yourdomain.com"}:
        return False, "BREVO_SENDER_EMAIL must use a real sender verified in Brevo"

    # Configure API
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # Prepare email
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": sender_email, "name": sender_name},
        subject=subject,
        html_content=html_content,
        text_content=text_content or _html_to_text(html_content)
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email sent to {to_email}: {api_response.message_id}")
        return True, "Email sent successfully"
    except ApiException as e:
        error_msg = f"Brevo API error: {e.body if hasattr(e, 'body') else str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Email sending failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def send_otp_email(to_email: str, otp: str) -> tuple[bool, str]:
    """Send OTP verification email."""
    subject = "Mã xác thực tài khoản - IT Career Match"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                     line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .container {{ background: #fff; border-radius: 12px; padding: 40px;
                          box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .logo {{ text-align: center; margin-bottom: 30px; }}
            .logo h1 {{ color: #2563eb; margin: 0; font-size: 28px; }}
            .otp-box {{ background: #f0f4ff; border: 2px solid #2563eb; border-radius: 8px;
                        padding: 20px; text-align: center; margin: 20px 0; }}
            .otp-code {{ font-size: 36px; font-weight: bold; color: #2563eb;
                         letter-spacing: 8px; font-family: monospace; }}
            .otp-label {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
            .info {{ background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px;
                     padding: 15px; margin: 20px 0; font-size: 14px; color: #92400e; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>IT Career Match</h1>
            </div>
            <h2>Xác thực tài khoản</h2>
            <p>Cảm ơn bạn đã đăng ký tài khoản tại IT Career Match. Vui lòng sử dụng mã OTP bên dưới để xác thực email:</p>

            <div class="otp-box">
                <div class="otp-label">Mã OTP của bạn</div>
                <div class="otp-code">{otp}</div>
            </div>

            <div class="info">
                <strong>Lưu ý:</strong> Mã OTP có hiệu lực trong <strong>10 phút</strong>.
                Không chia sẻ mã này với bất kỳ ai.
            </div>

            <p>Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email này.</p>

            <div class="footer">
                <p>© 2024 IT Career Match. All rights reserved.</p>
                <p>Email này được gửi tự động, vui lòng không trả lời.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
IT Career Match - Xác thực tài khoản

Mã OTP của bạn: {otp}

Mã OTP có hiệu lực trong 10 phút. Không chia sẻ mã này với bất kỳ ai.

Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email này.

---
IT Career Match
    """

    return send_email(to_email, subject, html_content, text_content)


def send_welcome_email(to_email: str, username: str) -> tuple[bool, str]:
    """Send welcome email after successful verification."""
    subject = "Chào mừng bạn đến với IT Career Match!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                     line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .container {{ background: #fff; border-radius: 12px; padding: 40px;
                          box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .logo {{ text-align: center; margin-bottom: 30px; }}
            .logo h1 {{ color: #2563eb; margin: 0; font-size: 28px; }}
            .btn {{ display: inline-block; background: #2563eb; color: #fff;
                     padding: 14px 28px; border-radius: 8px; text-decoration: none;
                     font-weight: 600; margin: 20px 0; }}
            .features {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 30px 0; }}
            .feature {{ text-align: center; padding: 20px; background: #f8fafc; border-radius: 8px; }}
            .feature-icon {{ font-size: 24px; margin-bottom: 10px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>IT Career Match</h1>
            </div>
            <h2>Chào mừng {username}! 🎉</h2>
            <p>Tài khoản của bạn đã được xác thực thành công. Bây giờ bạn có thể khám phá tất cả tính năng:</p>

            <div class="features">
                <div class="feature">
                    <div class="feature-icon">📄</div>
                    <strong>Tải lên CV</strong><br>
                    <small>Phân tích kỹ năng tự động</small>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <strong>Gợi ý việc làm</strong><br>
                    <small>AI matching độ chính xác cao</small>
                </div>
                <div class="feature">
                    <div class="feature-icon">💬</div>
                    <strong>Chatbot hướng nghiệp</strong><br>
                    <small>Tư vấn CV, phỏng vấn, roadmap</small>
                </div>
            </div>

            <a href="https://itcareermatch.com/dashboard" class="btn">Bắt đầu ngay</a>

            <p>Cần hỗ trợ? Chatbot của chúng tôi sẵn sàng trả lời mọi thắc mắc về CV, phỏng vấn, lộ trình học tập.</p>

            <div class="footer">
                <p>© 2024 IT Career Match. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Chào mừng {username} đến với IT Career Match!

Tài khoản của bạn đã được xác thực. Bạn có thể:
- Tải lên CV để phân tích kỹ năng
- Nhận gợi ý việc làm phù hợp
- Sử dụng chatbot tư vấn nghề nghiệp

Truy cập dashboard để bắt đầu: https://itcareermatch.com/dashboard

---
IT Career Match
    """

    return send_email(to_email, subject, html_content, text_content)


def send_application_confirmation(to_email: str, job_title: str, company: str) -> tuple[bool, str]:
    """Send application confirmation email."""
    subject = f"Xác nhận ứng tuyển: {job_title} tại {company}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                     line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .container {{ background: #fff; border-radius: 12px; padding: 40px;
                          box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .logo {{ text-align: center; margin-bottom: 30px; }}
            .logo h1 {{ color: #2563eb; margin: 0; font-size: 28px; }}
            .job-info {{ background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px;
                         padding: 20px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>IT Career Match</h1>
            </div>
            <h2>Ứng tuyển thành công! ✅</h2>
            <p>Bạn đã nộp đơn ứng tuyển vị trí:</p>

            <div class="job-info">
                <strong>{job_title}</strong><br>
                Tại: {company}<br>
                Trạng thái: <span style="color: #2563eb;">Đang chờ xét duyệt</span>
            </div>

            <p>Nhà tuyển dụng sẽ xem xét hồ sơ và liên hệ với bạn trong vòng 3-5 ngày làm việc.</p>
            <p>Bạn có thể theo dõi trạng thái đơn ứng tuyển tại mục <strong>Đơn ứng tuyển của tôi</strong>.</p>

            <div class="footer">
                <p>© 2024 IT Career Match. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Ứng tuyển thành công!

Vị trí: {job_title}
Công ty: {company}
Trạng thái: Đang chờ xét duyệt

Nhà tuyển dụng sẽ liên hệ trong 3-5 ngày làm việc.
Theo dõi tại: Đơn ứng tuyển của tôi

---
IT Career Match
    """

    return send_email(to_email, subject, html_content, text_content)


def _html_to_text(html: str) -> str:
    """Simple HTML to text conversion."""
    import re
    # Remove scripts and styles
    html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
    # Replace block elements with newlines
    html = re.sub(r'</(div|p|h[1-6]|li|tr)>', '\n', html)
    html = re.sub(r'<br\s*/?>', '\n', html)
    # Remove remaining tags
    html = re.sub(r'<[^>]+>', '', html)
    # Decode entities
    html = html.replace('&nbsp;', ' ').replace('&', '&').replace('<', '<').replace('>', '>')
    # Clean whitespace
    html = re.sub(r'\n\s*\n', '\n\n', html)
    return html.strip()


if __name__ == "__main__":
    # Test
    print("Email utilities loaded")
    print(f"Brevo SDK available: {BREVO_AVAILABLE}")

    # Test HTML to text
    test_html = "<p>Hello <strong>World</strong></p><div>Test</div>"
    print(f"HTML to text: {_html_to_text(test_html)}")