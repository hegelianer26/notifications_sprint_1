import aio_pika
from core.config import rabbitmq_config


async def get_rabbitmq_connection():
    connection = await aio_pika.connect_robust(
        f"amqp://{rabbitmq_config.user}:{rabbitmq_config.password}@{rabbitmq_config.host}/")
    return connection
