class EmailTemplate:

    @staticmethod
    def create_password_email(username: str, password: str) -> str:
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 30px;
                    color: #333333;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background-color: #ffffff;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                }}
                .highlight {{
                    color: #b30059;
                    font-weight: bold;
                    font-size: 18px;
                }}
                p {{
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Dobrý deň <strong>{username}</strong>,</p>
                <p>Vitajte v našom systéme. Tu je vaše dočasné heslo:</p>
                <p class="highlight">{password}</p>
                <p>Prosím, prihláste sa do 48 hodín a zmeňte si heslo.</p>
                <p>Ďakujeme,<br>Váš tím</p>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def verification_email(username: str, link: str) -> str:
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 30px;
                    color: #333333;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background-color: #ffffff;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                }}
                a {{
                    color: #0066cc;
                    text-decoration: none;
                    font-weight: bold;
                }}
                p {{
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Dobrý deň <strong>{username}</strong>,</p>
                <p>Prosím, overte svoj účet pomocou nasledujúceho odkazu:</p>
                <p><a href="{link}">{link}</a></p>
                <p>Ďakujeme,<br>Váš tím</p>
            </div>
        </body>
        </html>
        """
