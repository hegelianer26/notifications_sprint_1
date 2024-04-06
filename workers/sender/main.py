import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
from aio_pika import connect_robust
from db import get_session
import json
from sqlalchemy import text
from config import mail_server_config, rabbitmq_config
import logging

logging.basicConfig(filename='sender.log', level=logging.INFO)


async def set_status(notification_uuid: str, status: str):

    async for session in get_session():
        try:
            async with session.begin():
                await session.execute(
                    text(f'update notify_history set status = \'{status}\' where notification_uuid = \'{notification_uuid}\''))
        finally:
            await session.close()


async def send_email(smtp_client, subject, message, recipient, notification_uuid, sender):

    try:
        email_message = MIMEMultipart()
        email_message['Subject'] = subject
        email_message['From'] = sender
        email_message['To'] = recipient

        email_message.attach(MIMEText(message, 'html'))
        smtp_client.sendmail(sender, recipient, email_message.as_string())
        await set_status(notification_uuid, 'delivered')
        logging.info("Email has been delivered")
    except Exception as e:
        await set_status(notification_uuid, 'failed')
        logging.error(f"Error sending email: {e}")


async def main():
    smtp_client = smtplib.SMTP(mail_server_config.host, mail_server_config.port)

    connection = await connect_robust(
        f"amqp://{rabbitmq_config.user}:{rabbitmq_config.password}@{rabbitmq_config.host}/")
    channel = await connection.channel()
    queue = await channel.declare_queue(rabbitmq_config.queue, durable=True)
    async for message in queue_iter:
        async with message.process():
            msg_body = message.body.decode()
            msg_dict = json.loads(msg_body)
            subject = msg_dict.get('subject')
            message = msg_dict.get('content')
            notification_uuid = msg_dict.get('notification_uuid')
            recipient = msg_dict.get('recipient')
            sender = msg_dict.get('sender')
            try:
                await send_email(smtp_client, subject, message, recipient, notification_uuid, sender)
            except Exception as e:
                logging.error(f"Error processing message: {e}")

    smtp_client.quit()


if __name__ == '__main__':
    asyncio.run(main())
