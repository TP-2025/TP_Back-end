import os

class Settings:
    #Potrebné pridať legit smtp server s vlastnou doménou. Toto je len free služba, ktorá hádže všetky emaily do spamu!
    #Tiež je vhodné zrejme prerobiť subject, premiestniť ho z nastavení...

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "ocunetai@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "ptyc vlav ieex jizj")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "ocunetai@gmail.com")

    PASSWORD_SUBJECT: str = "Nové heslo"
    VERIFY_SUBJECT: str = "Verifikácia"

    ADMIN_EMAIL: str = "admin@admin.com"
    ADMIN_PASSWORD: str = "yJ02+J1_?a<V<y!bWeWL"




settings = Settings()