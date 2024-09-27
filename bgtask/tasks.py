import random
import smtplib
from email.message import EmailMessage

from celery import Celery
from redis import Redis

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, REDIS_HOST, REDIS_PORT

celery = Celery('tasks', broker='redis://localhost:6379')

def get_email_message(email: str, user_id: int):
    email_message = EmailMessage()
    email_message['Subject'] = 'Танки'
    email_message['From'] = SMTP_USER
    email_message['To'] = email

    code_value = random.randint(1000,9999)

    with Redis(host=REDIS_HOST, port=REDIS_PORT) as redis_client:
        redis_client.set(user_id,value=code_value,ex=300)

    email_message.set_content(
        '<div>'
            f'<h1>Код для подтверждения email: {code_value}</h1>'
        '</div>',
        subtype='html'
    )
    return email_message

@celery.task
def send_email_hello_world(email: str, user_id: int):
    email_message = get_email_message(email, user_id)
    with smtplib.SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email_message)