import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_report_email(to_email, report_type, frequency, report_formats, additional_notes):
    """
    Composes and sends a report email.
    For demonstration, this function sends a basic text email.
    """
    # Create a subject and body. You can expand this to actually attach PDFs, etc.
    subject = f"Your {report_type} Report ({frequency})"
    body = (
        f"Hello,\n\n"
        f"Here is your requested {report_type} report delivered {frequency.lower()}.\n\n"
        f"Report Formats: {', '.join(report_formats)}\n"
        f"Additional Notes: {additional_notes}\n\n"
        f"Regards,\n"
        f"Portfolio Analyzer Team"
    )

    # Build the email message
    msg = MIMEMultipart()
    msg['From'] = os.environ.get('EMAIL_FROM', 'noreply@portfolioanalyzer.com')
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # SMTP server configuration from environment variables
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME', 'your_smtp_username')
    smtp_password = os.environ.get('SMTP_PASSWORD', 'your_smtp_password')

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

def schedule_report(email, report_type, frequency, report_formats, additional_notes):
    """
    For now we immediately send the report.
    In a real application, you might schedule this using Celery or APScheduler.
    """
    success = send_report_email(email, report_type, frequency, report_formats, additional_notes)
    return success
