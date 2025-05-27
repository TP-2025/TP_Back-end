from app.frontend_oriented.services.email import EmailService

EmailService = EmailService()

#Only for testing purposes

EmailService.send_password_email("matejjhorsky@gmail.com","matejjhorsky@gmail.com", "abrakadabra")
#EmailService.send_email("igorgrozny125@gmail.com","feri", "feri123456789")
#EmailService.send_verification_email("igorgrozny125@gmail.com", "youtube.com")
