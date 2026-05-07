import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587

SMTP_LOGIN = "aa95f5001@smtp-brevo.com"
SMTP_PASSWORD = "03GW46rpAIjahZsw"

SENDER_EMAIL = "trade.vkquick@gmail.com"


def send_otp_email(receiver_email, otp, referral_code=None):

    subject = "ForexPro Login Verification Code"

    body = f"""
Dear User,

Your OTP is: {otp}

Referral Code: {referral_code}

This OTP is valid for 10 minutes.

Regards,
ForexPro Team
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

        server.starttls()

        server.login(SMTP_LOGIN, SMTP_PASSWORD)

        server.sendmail(
            SENDER_EMAIL,
            receiver_email,
            msg.as_string()
        )

        server.quit()

        print("EMAIL SENT SUCCESSFULLY")

    except Exception as e:
        print("EMAIL ERROR:", e)