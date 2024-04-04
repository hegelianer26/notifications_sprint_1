from contextlib import asynccontextmanager
import json

import uvicorn
from core.config import fastapi_config, rabbitmq_config
from db.postgres.database import create_database
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from models.entity import EmailCampaign
from db.postgres.crud import get_crud_service, PostgresCRUD
import aio_pika


@asynccontextmanager
async def lifespan(app: FastAPI):
    if fastapi_config.is_debug:
        await create_database()
    yield


app = FastAPI(
    title=fastapi_config.fastapi_project_name,
    docs_url="/notify/api/openapi",
    openapi_url="/notify/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.post("/post_notifications/")
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

# @app.middleware('http')
# async def before_request(request: Request, call_next):
#     response = await call_next(request)
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         return ORJSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={'detail': 'X-Request-Id is required'})
#     return response



# app.include_router(roles.router, prefix="/auth/api/v1/roles")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,
        reload=True
    )
