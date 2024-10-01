# email_sender.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(receiver_email, user_name):
    smtp_server = 'smtp.gmail.com'
    port = 587  # For starttls
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = "TechChat Team"
    password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not password:
        print("Error: Environment variables for email are not set properly.")
        return

    # Render the feedback HTML template for the email
    email_html = render_template('email_templates/feedback_email.html', user_name=user_name)

    # Create email message
    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "Thank you for your feedback"

    # Attach the HTML content
    message.attach(MIMEText(email_html, "html"))

    try:
        # Set up the SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as smtp:
            smtp.ehlo()  # Can be omitted as starttls includes it
            smtp.starttls(context=context)
            smtp.ehlo()  # Re-identify after starting TLS
            smtp.login(sender_email, password)
            smtp.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")