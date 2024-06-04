# email_sender.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template
import os

def send_email(receiver_email, user_name):
    smtp_server = 'smtp-mail.outlook.com'
    port = 587  # For starttls
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_name = "TechChat Team"
    password = os.environ.get("SENDER_PASSWORD")

    if not sender_email or not password:
        print("Error: Environment variables for email are not set properly.")
        return

    # Render the feedback HTML template for the email
    email_html = render_template('email_templates/feedback_email.html', user_name=user_name)

    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "Thank you for your feedback"

    message.attach(MIMEText(email_html, "html"))

    try:
        smtp = smtplib.SMTP(smtp_server, port)
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, receiver_email, message.as_string())
        smtp.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")
