import requests
from celery import shared_task
import os
from requests.exceptions import RequestException

api_host = os.getenv('API_HOST')
api_port = os.getenv('API_PORT')

@shared_task(autoretry_for=(RequestException,), retry_backoff=True)
def send_mail_once(*args):
    message = args[0]

    response = requests.post(f'http://gate_api:8082/post_notifications', json=[message])
    print(response.status_code, response.text)
    if response.status_code == 200:
        print("Emails sent successfully.")
    else:
        print("Failed to send emails.")
