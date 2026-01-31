"""
Brevo Email Service for sending admission alerts
"""
import os
import httpx
from datetime import datetime
from typing import Optional
from ai_career_advisor.core.logger import logger


class BrevoService:
    """Service for sending emails via Brevo API"""
    
    API_KEY = os.getenv("BREVO_API_KEY", "")
    API_URL = "https://api.brevo.com/v3/smtp/email"
    SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "noreply@aicareerpilot.com")
    SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "AI Career Pilot")
    
    @classmethod
    async def send_admission_alert(
        cls,
        to_email: str,
        exam_name: str,
        college_name: str,
        degree: str,
        branch: str,
        alert_type: str,
        target_date: datetime,
        exam_details: Optional[dict] = None
    ) -> bool:
        """
        Send an admission alert email via Brevo
        
        Args:
            to_email: Recipient email address
            exam_name: Name of the entrance exam
            college_name: Name of the college
            degree: Degree program
            branch: Branch/specialization
            alert_type: Type of alert (registration_start, exam_1day, etc.)
            target_date: The target date for the alert
            exam_details: Optional dict with exam details
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        
        if not cls.API_KEY:
            logger.error("❌ BREVO_API_KEY not configured")
            return False
        
        try:
            subject, html_content = cls._get_email_content(
                alert_type=alert_type,
                exam_name=exam_name,
                college_name=college_name,
                degree=degree,
                branch=branch,
                target_date=target_date,
                exam_details=exam_details
            )
            
            headers = {
                "api-key": cls.API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "sender": {
                    "email": cls.SENDER_EMAIL,
                    "name": cls.SENDER_NAME
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_content
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    cls.API_URL,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 201:
                    logger.success(f"✅ Email sent to {to_email} for {alert_type}")
                    return True
                else:
                    logger.error(f"❌ Failed to send email: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error sending email via Brevo: {str(e)}")
            return False
    
    @classmethod
    def _get_email_content(
        cls,
        alert_type: str,
        exam_name: str,
        college_name: str,
        degree: str,
        branch: str,
        target_date: datetime,
        exam_details: Optional[dict] = None
    ) -> tuple[str, str]:
        """Generate email subject and HTML content based on alert type"""
        
        date_str = target_date.strftime("%B %d, %Y")
        
        # Email templates for different alert types
        templates = {
            "registration_start": {
                "subject": f"🎓 {exam_name} Registration Opens Today!",
                "body": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Registration Opens Today! 🎓</h2>
                        <p>Hi there,</p>
                        <p>Great news! The registration for <strong>{exam_name}</strong> opens today!</p>
                        
                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #1f2937;">Admission Details</h3>
                            <p><strong>College:</strong> {college_name}</p>
                            <p><strong>Degree:</strong> {degree}</p>
                            <p><strong>Branch:</strong> {branch}</p>
                            <p><strong>Exam:</strong> {exam_name}</p>
                            <p><strong>Registration Opens:</strong> {date_str}</p>
                        </div>
                        
                        <p><strong>⚡ Action Required:</strong> Don't miss out! Register as soon as possible.</p>
                        
                        {cls._get_exam_details_html(exam_details)}
                        
                        <p style="margin-top: 30px;">Best of luck with your application!</p>
                        <p style="color: #6b7280;">- AI Career Pilot Team</p>
                    </div>
                </body>
                </html>
                """
            },
            "registration_3days": {
                "subject": f"⏰ Only 3 Days Left - {exam_name} Registration Deadline",
                "body": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #dc2626;">⏰ Only 3 Days Left!</h2>
                        <p>Hi there,</p>
                        <p>This is a reminder that the registration for <strong>{exam_name}</strong> closes in just <strong>3 days</strong>!</p>
                        
                        <div style="background-color: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                            <h3 style="margin-top: 0; color: #991b1b;">Urgent Reminder</h3>
                            <p><strong>College:</strong> {college_name}</p>
                            <p><strong>Degree:</strong> {degree}</p>
                            <p><strong>Branch:</strong> {branch}</p>
                            <p><strong>Registration Deadline:</strong> {date_str}</p>
                        </div>
                        
                        <p><strong>🚨 Don't Wait!</strong> Complete your registration before it's too late.</p>
                        
                        {cls._get_exam_details_html(exam_details)}
                        
                        <p style="margin-top: 30px;">Good luck!</p>
                        <p style="color: #6b7280;">- AI Career Pilot Team</p>
                    </div>
                </body>
                </html>
                """
            },
            "registration_last": {
                "subject": f"🚨 LAST DAY - {exam_name} Registration Closes Today!",
                "body": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #dc2626;">🚨 LAST DAY TO REGISTER!</h2>
                        <p>Hi there,</p>
                        <p><strong>This is your final reminder!</strong> The registration for <strong>{exam_name}</strong> closes <strong>TODAY</strong>!</p>
                        
                        <div style="background-color: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                            <h3 style="margin-top: 0; color: #991b1b;">⚠️ Final Call</h3>
                            <p><strong>College:</strong> {college_name}</p>
                            <p><strong>Degree:</strong> {degree}</p>
                            <p><strong>Branch:</strong> {branch}</p>
                            <p><strong>Last Day:</strong> {date_str}</p>
                        </div>
                        
                        <p><strong>⏰ ACT NOW!</strong> This is your last chance to register. Don't miss this opportunity!</p>
                        
                        {cls._get_exam_details_html(exam_details)}
                        
                        <p style="margin-top: 30px;">All the best!</p>
                        <p style="color: #6b7280;">- AI Career Pilot Team</p>
                    </div>
                </body>
                </html>
                """
            },
            "exam_1day": {
                "subject": f"📝 Tomorrow is Your {exam_name} Exam!",
                "body": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">📝 Exam Tomorrow!</h2>
                        <p>Hi there,</p>
                        <p>Your <strong>{exam_name}</strong> exam is scheduled for <strong>tomorrow</strong>!</p>
                        
                        <div style="background-color: #eff6ff; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb;">
                            <h3 style="margin-top: 0; color: #1e40af;">Exam Details</h3>
                            <p><strong>College:</strong> {college_name}</p>
                            <p><strong>Degree:</strong> {degree}</p>
                            <p><strong>Branch:</strong> {branch}</p>
                            <p><strong>Exam Date:</strong> {date_str}</p>
                        </div>
                        
                        <h3 style="color: #1f2937;">📋 Final Checklist:</h3>
                        <ul>
                            <li>✅ Admit card downloaded and printed</li>
                            <li>✅ Valid ID proof ready</li>
                            <li>✅ Required stationery packed</li>
                            <li>✅ Exam center location confirmed</li>
                            <li>✅ Good night's sleep planned</li>
                        </ul>
                        
                        {cls._get_exam_details_html(exam_details)}
                        
                        <p style="margin-top: 30px;"><strong>You've got this! 💪</strong></p>
                        <p style="color: #6b7280;">- AI Career Pilot Team</p>
                    </div>
                </body>
                </html>
                """
            }
        }
        
        template = templates.get(alert_type, templates["registration_start"])
        return template["subject"], template["body"]
    
    @classmethod
    def _get_exam_details_html(cls, exam_details: Optional[dict]) -> str:
        """Generate HTML for exam details section"""
        if not exam_details:
            return ""
        
        html = '<div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">'
        html += '<h3 style="margin-top: 0; color: #1f2937;">📚 Exam Information</h3>'
        
        if exam_details.get("official_website"):
            html += f'<p><strong>Official Website:</strong> <a href="{exam_details["official_website"]}" style="color: #2563eb;">{exam_details["official_website"]}</a></p>'
        
        if exam_details.get("conducting_body"):
            html += f'<p><strong>Conducting Body:</strong> {exam_details["conducting_body"]}</p>'
        
        if exam_details.get("exam_pattern"):
            html += f'<p><strong>Exam Pattern:</strong> {exam_details["exam_pattern"]}</p>'
        
        if exam_details.get("syllabus_link"):
            html += f'<p><strong>Syllabus:</strong> <a href="{exam_details["syllabus_link"]}" style="color: #2563eb;">View Syllabus</a></p>'
        
        html += '</div>'
        return html
