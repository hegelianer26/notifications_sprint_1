import json

from core.config import rabbitmq_config
from fastapi import Depends, APIRouter
from models.entity import EmailCampaign
from db.postgres.crud import get_crud_service, PostgresCRUD
import aio_pika


router = APIRouter()


@router.post("/post_notifications/")
async def post_notification(
    message_body: list[EmailCampaign],
    db_service: PostgresCRUD = Depends(get_crud_service)
):
    await db_service.post_notifications_db(message_body)

    json_data = [notification.model_dump() for notification in message_body]

    connection = await aio_pika.connect_robust(
        f"amqp://{rabbitmq_config.user}:{rabbitmq_config.password}@{rabbitmq_config.host}/")
    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            rabbitmq_config.exchange_name,
            aio_pika.ExchangeType.DIRECT)
        queue = await channel.declare_queue(rabbitmq_config.queue_draft,
                                            durable=True)

        await queue.bind(exchange, rabbitmq_config.routing_key)
        for notification in json_data:
            notification = json.dumps(notification)
            message = aio_pika.Message(
                body=notification.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await exchange.publish(message,
                                   routing_key=rabbitmq_config.routing_key)
    return message_body
