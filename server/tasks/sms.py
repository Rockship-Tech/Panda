import os
from twilio.rest import Client

from main_celery import celery


@celery.task(name='tasks.mail.send_sms')
def send_sms(to_phone_number, message):
    client = Client(
        os.getenv('TWILIO_ACCOUNT_ID'),
        os.getenv('TWILIO_AUTH_TOKEN'),

    )
    message = client.messages.create(
        body=message,
        from_='ROCKSHIP',
        to=to_phone_number
    )
