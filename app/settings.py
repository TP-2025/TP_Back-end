import os

class Settings:
    #Potrebné pridať legit smtp server s vlastnou doménou. Toto je len free služba, ktorá hádže všetky emaily do spamu!
    #Tiež je vhodné zrejme prerobiť subject, premiestniť ho z nastavení...

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.mailersend.net")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 2525))
    SMTP_USER: str = os.getenv("SMTP_USER", "MS_nnb1Gj@test-86org8e2j11gew13.mlsender.net")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "mssp.KoJ6prv.x2p0347oqekgzdrn.BgJK9xb")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "MS_nnb1Gj@test-86org8e2j11gew13.mlsender.net")

    PASSWORD_SUBJECT: str = "Nové heslo"
    VERIFY_SUBJECT: str = "Verifikácia"

    ADMIN_EMAIL: str = "admin@admin.com"
    ADMIN_PASSWORD: str = "yJ02+J1_?a<V<y!bWeWL"


settings = Settings()
