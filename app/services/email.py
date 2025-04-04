import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    """Function to send an email."""
    # Email server configuration (use a real SMTP server in production)
    smtp_server = "smtp.example.com"  # Replace with actual SMTP server
    smtp_port = 587  # Standard port for TLS
    sender_email = "your_email@example.com"  # Replace with your email
    sender_password = "your_password"  # Replace with your email password

    # Set up the MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the message
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a connection to the mail server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection using TLS
            server.login(sender_email, sender_password)  # Login to the email account
            text = msg.as_string()  # Convert the message to string format
            server.sendmail(sender_email, to_email, text)  # Send the email
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def send_report(user_email, report_content, portfolio_holdings=None, analysis=None):
    """Function to send a report to the user, including recommendations and portfolio details."""
    # If portfolio_holdings and analysis are provided, add them to the report
    subject = "Your Apex Trades Report"

    # Build the body of the email with a personalized report content
    body = f"Dear user,\n\nHere is your requested report:\n\n{report_content}"

    # Add portfolio holdings if available
    if portfolio_holdings:
        body += "\n\nYour Portfolio Holdings:\n"
        for asset, details in portfolio_holdings.items():
            body += f"{asset}: {details}\n"

    # Add analysis if available
    if analysis:
        body += "\n\nYour Portfolio Analysis:\n"
        for key, value in analysis.items():
            body += f"{key}: {value}\n"

    body += "\n\nBest regards,\nApex Trades Team"

    # Send the email
    send_email(subject, body, user_email)

def send_password_reset(user_email, reset_token):
    """Function to send a password reset email to the user."""
    subject = "Password Reset Request"
    body = f"Dear user,\n\nTo reset your password, please use the following token:\n\n{reset_token}\n\nBest regards,\nApex Trades Team"
    send_email(subject, body, user_email)