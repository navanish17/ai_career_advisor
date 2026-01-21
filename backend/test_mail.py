import asyncio
from ai_career_advisor.services.email_service import EmailService


def test_email():
    result = EmailService.send_alert_email(
        to_email="navnishpande17@gmail.com",  # Replace with your email
        exam_name="JEE Advanced 2026",
        alert_type="registration_start",
        target_date="2026-05-01",
        exam_website="https://jeeadv.ac.in",
        college_name="IIT Bombay",
        degree="BTech"
    )
    
    if result:
        print("✅ Email sent successfully! Check your inbox.")
    else:
        print("❌ Email failed. Check logs.")


if __name__ == "__main__":
    test_email()
