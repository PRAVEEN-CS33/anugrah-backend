import random
import secrets
import string
from twilio.rest import Client
import os


def generate_secure_otp(number):
    characters = string.digits 
    otp = ''.join(secrets.choice(characters) for _ in range(6))

    str="Your OTP for Verification is "+otp

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+14405652156',
        body=str,
        to='+91'+number
    )
    print(message.sid)
    return otp
