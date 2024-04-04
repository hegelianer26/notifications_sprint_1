import asyncio
from aio_pika import connect_robust
from db import get_session, create_database
from models import NotificationDB
import json
from sqlalchemy import text
import aio_pika
import uuid
from config import rabbitmq_config


async def get_from_rabbit():
    connection = await connect_robust(
        f'amqp://{rabbitmq_config.user}:{rabbitmq_config.password}@{rabbitmq_config.host}/')
    channel = await connection.channel()

    queue = await channel.declare_queue(rabbitmq_config.queue_draft,
                                        durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                msg_body = message.body.decode()
                msg_dict = json.loads(msg_body)

                uuid = msg_dict.get('uuid')
                content = msg_dict.get('content')
                subject = msg_dict.get('subject')
                sender = msg_dict.get('sender')
                user_groups = msg_dict.get('user_groups')

                message = {
                    'uuid': uuid,
                    'content': content,
                    'subject': subject,
                    'sender': sender,
                    'user_groups': user_groups
                }
                yield message


async def get_message_for_user(user_groups):
    async for session in get_session():
        try:
            async with session.begin():
                users = await session.execute(
                    text(f"select first_name, last_name, email from users_for_mails where group_name = '{user_groups}'"),)
        finally:
            await session.close()
        return users


async def send_to_queue(mail):
    # exchange_name = 'notifications_exchange'
    # queue_name = 'notifications_queue_ready'

    connection = await aio_pika.connect_robust(
        f"amqp://{rabbitmq_config.user}:{rabbitmq_config.password}@{rabbitmq_config.host}/")
    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            rabbitmq_config.exchange_name, aio_pika.ExchangeType.DIRECT)
        queue = await channel.declare_queue(
            rabbitmq_config.queue_ready,
            durable=True)

        await queue.bind(exchange, rabbitmq_config.routing_key)

        message = aio_pika.Message(
            body=mail.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        await exchange.publish(
            message, routing_key=rabbitmq_config.routing_key)


async def form_user_message(user, message):
    user_message = {
        'campaign_uuid': message.get('uuid'),
        'notification_uuid': str(uuid.uuid4()),
        'content': message.get('content'),
        'subject': message.get('subject'),
        'sender': message.get('sender'),
        'user_groups': message.get('user_groups'),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'recipient': user.email
    }
    return user_message


async def send_to_db(notification):
    async for session in get_session():

        try:
            async with session.begin():
                await session.execute(
                    NotificationDB.__table__.insert().values(
                        notification_uuid=notification.get(
                            'notification_uuid'),
                        campaign_uuid=notification.get('campaign_uuid'),
                        status='pending',
                        user_groups=notification.get('user_groups'),
                        sender=notification.get('sender'),
                        subject=notification.get('subject'),
                        content=notification.get('content'),
                        first_name=notification.get('first_name'),
                        last_name=notification.get('last_name'),
                        recipient=notification.get('recipient'),
                    ))

                await session.commit()

        finally:
            await session.close()


async def main():
    await create_database()

    async for msg in get_from_rabbit():
        if msg:
            print('взяли', msg)
            users = await get_message_for_user(msg.get('user_groups'))
            user_records = users.fetchall()
            for user in user_records:
                notification = await form_user_message(user, msg)
                await send_to_db(notification)
                await send_to_queue(json.dumps(notification))


if __name__ == "__main__":
    asyncio.run(main())
