from twilio.rest import Client
from django.conf import settings

def send_sms(to_number, message):
    """
    Send an SMS using Twilio.
    :param to_number: Recipient phone number (e.g., +21612345678)
    :param message: Message content
    :return: None
    """
    account_sid = settings.SMS_TWILIO_ACCOUNT_SID
    auth_token = settings.SMS_TWILIO_AUTH_TOKEN
    twilio_number = settings.SMS_TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        print(f"SMS sent successfully to {to_number}")
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        raise