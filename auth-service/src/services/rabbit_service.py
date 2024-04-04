import aio_pika
from core.config import rabbitmq_config
from db.rqbbitmq import get_rabbitmq_connection
import uuid
import json


class RabbitService:
    def __init__(self, connection):
        self.connection = connection

    async def send_to_queue(self, mail):

        mail['content'] = 'Welcome to our movie service!'
        mail['subject'] = 'Welcome!'
        mail['sender'] = 'movie@ya.com'
        mail['recipient'] = mail.get('email')
        mail['notification_uuid'] = str(uuid.uuid4())

        async with self.connection:
            channel = await self.connection.channel()

            exchange = await channel.declare_exchange(
                rabbitmq_config.exchange_name, aio_pika.ExchangeType.DIRECT)
            queue = await channel.declare_queue(
                rabbitmq_config.queue_ready,
                durable=True)

            await queue.bind(exchange, rabbitmq_config.routing_key)

            message = aio_pika.Message(
                body=json.dumps(mail).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await exchange.publish(
                message, routing_key=rabbitmq_config.routing_key)



async def get_rabbit_service():
    connection = await get_rabbitmq_connection()
    return RabbitService(connection=connection)


# get_rabbit_service = create_rabbit_service()