class EmailTemplate:

    @staticmethod
    def create_password_email(username: str, password: str) -> str:
        return f"""
        <html>
        <body>
            <p>Hi {username},</p>
            <p>Welcome to our system. Here is your temporary password: <strong>{password}</strong></p>
            <p>Please log in within 48 hours to change your password.</p>
        </body>
        </html>
        """

    @staticmethod
    def verification_email(username: str, link: str) -> str:
        return f"""
        <html>
        <body>
            <p>Hi {username},</p>
            <p>Please verify your account using this link: <strong>{link}</strong></p>
        </body>
        </html>
        """