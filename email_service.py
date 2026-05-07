import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)

SENDER_EMAIL = "trade.vkquick@gmail.com"


def send_otp_email(receiver_email, otp, referral_code=None):

    subject = "ForexPro Login Verification Code"

    html_content = f"""
    <html>
    <body>
        <h2>Your OTP is: {otp}</h2>
        <p>Referral Code: {referral_code}</p>
        <p>This OTP is valid for 10 minutes.</p>

        <br>
        <p>Regards,</p>
        <p>ForexPro Team</p>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": receiver_email}],
        sender={
            "email": SENDER_EMAIL,
            "name": "ForexPro"
        },
        subject=subject,
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("EMAIL SENT SUCCESS")
        print(api_response)

    except ApiException as e:
        print("EMAIL ERROR:", e)