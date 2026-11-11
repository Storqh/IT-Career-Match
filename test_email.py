from utils.email_utils import send_email, send_otp_email, BREVO_AVAILABLE
import os

print('Brevo SDK available:', BREVO_AVAILABLE)
print('BREVO_API_KEY:', os.getenv('BREVO_API_KEY')[:20] + '...' if os.getenv('BREVO_API_KEY') else 'NOT SET')
print('BREVO_SENDER_EMAIL:', os.getenv('BREVO_SENDER_EMAIL'))
print('BREVO_SENDER_NAME:', os.getenv('BREVO_SENDER_NAME'))

# Test send
print('\n--- Testing OTP email ---')
result = send_otp_email('tranquochuy8645@gmail.com', '123456')
print('Result:', result)

print('\n--- Testing reset password email ---')
html_content = '<p>Test <a href="http://localhost:5000/reset">link</a></p>'
result2 = send_email(
    'tranquochuy8645@gmail.com',
    'Test Reset Password',
    html_content
)
print('Result:', result2)