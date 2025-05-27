from fastapi import HTTPException
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.frontend_oriented.utils.email_templates import EmailTemplate
from app.settings import settings


class EmailService:
    def __init__(self):
        self.smptServer = settings.SMTP_SERVER
        self.smptPort = settings.SMTP_PORT
        self.smptUser = settings.SMTP_USER
        self.smptPassword = settings.SMTP_PASSWORD
        self.senderEmail = settings.SENDER_EMAIL
        self.passwordSubject = "Nové heslo"
        self.verifySubject = "dcba"

    def send_email(self, to: str, subject: str, body: str):
        try:
            with SMTP(self.smptServer, self.smptPort) as smpt:
                smpt.starttls()
                smpt.login(self.smptUser, self.smptPassword)
                message = MIMEMultipart()
                message["From"] = self.senderEmail
                message["To"] = to
                message["Subject"] = subject
                message.attach(MIMEText(body, "html"))

                smpt.sendmail(self.senderEmail, to, message.as_string())
        except SMTPException as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email.")

    def send_password_email(self, to: str, username: str, password: str):

        body = EmailTemplate.create_password_email(username, password)
        self.send_email(to, self.passwordSubject, body)

    def send_verification_email(self, to: str, link: str):

        body = EmailTemplate.verification_email(to, link)
        self.send_email(to, self.verifySubject, body)
