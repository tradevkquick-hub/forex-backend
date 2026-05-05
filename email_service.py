import smtplib
from email.mime.text import MIMEText
EMAIL = "nk20forex@gmail.com"
APP_PASSWORD = "fjvgqumfyhshidjk"
def send_otp_email(receiver_email,otp,referral_code=None):
    subject = "ForexPro Login Verification Code"
    body = f"""DEAR SIR/MAM,
    
               Your One-Time Password (OTP) for logging into ForexPro Trading is:OTP: {otp}
               Your Referral Code: {referral_code}
               Share this code with friends and earn rewards
               This OTP is valid for 10 minutes.
               If you did not request this login, please ignore this email or contact our support team.

               For security reasons, do not share this OTP with anyone.
               

               Regards,
               ForexPro Security Team
               """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = receiver_email

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(EMAIL,APP_PASSWORD)
    server.sendmail(EMAIL,receiver_email,msg.as_string())
    server.quit()