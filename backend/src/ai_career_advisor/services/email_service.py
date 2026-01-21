import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger


class EmailService:
    
    @staticmethod
    def send_alert_email(
        *,
        to_email: str,
        exam_name: str,
        alert_type: str,
        target_date: str,
        exam_website: str,
        college_name: str = None,
        degree: str = None
    ):
        
        alert_messages = {
            "registration_start": {
                "subject": f"🎯 {exam_name} Registration Now Open!",
                "title": "Registration Has Started",
                "message": f"The registration for {exam_name} is now open. Don't miss out!"
            },
            "registration_3days": {
                "subject": f"⚠️ Only 3 Days Left - {exam_name} Registration",
                "title": "Registration Closing Soon",
                "message": f"Only 3 days remaining to register for {exam_name}. Complete your registration now!"
            },
            "registration_last": {
                "subject": f"🚨 Last Day - {exam_name} Registration Closes Tomorrow!",
                "title": "Final Day to Register",
                "message": f"This is your last chance! Registration for {exam_name} closes tomorrow."
            },
            "exam_1day": {
                "subject": f"📝 {exam_name} Exam Tomorrow - Good Luck!",
                "title": "Exam Day Reminder",
                "message": f"Your {exam_name} exam is scheduled for tomorrow. All the best!"
            }
        }
        
        alert_info = alert_messages.get(alert_type, alert_messages["registration_start"])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                .info-box {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{alert_info['title']}</h1>
                </div>
                <div class="content">
                    <p>Hi there,</p>
                    <p>{alert_info['message']}</p>
                    
                    <div class="info-box">
                        <strong>📅 Important Date:</strong> {target_date}<br>
                        <strong>📝 Exam:</strong> {exam_name}<br>
                        {f"<strong>🎓 College:</strong> {college_name}<br>" if college_name else ""}
                        {f"<strong>📚 Degree:</strong> {degree}<br>" if degree else ""}
                    </div>
                    
                    <p><strong>What to do next:</strong></p>
                    <ul>
                        <li>Visit the official website</li>
                        <li>Complete all required steps</li>
                        <li>Keep your documents ready</li>
                    </ul>
                    
                    <a href="{exam_website}" class="button">Visit Official Website</a>
                    
                    <p>Good luck with your preparations! 🚀</p>
                </div>
                <div class="footer">
                    <p>AI Career Advisor - Helping students achieve their dreams</p>
                    <p>You're receiving this because you set up an alert for {exam_name}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = alert_info['subject']
            
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.success(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email failed: {str(e)}")
            return False
