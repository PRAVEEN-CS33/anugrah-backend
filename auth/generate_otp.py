import random
import secrets
import string
from twilio.rest import Client

def generate_secure_otp(number):
    characters = string.digits 
    otp = ''.join(secrets.choice(characters) for _ in range(6))

    str="Your OTP for Verification is "+otp

    account_sid = 'AC138692c8f4c7ae6c08a9a86e934c3734'
    auth_token = '764c09c702781897d67811048075df9c'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+14405652156',
        body=str,
        to='+91'+number
    )
    print(message.sid)
    return otp
