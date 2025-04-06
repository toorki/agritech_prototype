from celery import shared_task

@shared_task
def send_sms(phone_number, message):
    print(f"Sending SMS to {phone_number}: {message}")
    return True