from celery import Celery
import psycopg2
import pika
import json
from config import rabbitmq_config, postgres_config
import logging

logging.basicConfig(filename='checker.log', level=logging.INFO) 

# checker_app = Celery('tasks', broker=f'pyamqp://{rabbitmq_config.user}:{rabbitmq_config.password}@{rabbitmq_config.host}//',)
checker_app = Celery('tasks', broker=f'redis://movie_redis_1')

checker_app.autodiscover_tasks()

@checker_app.task
def check_and_send_messages():

    conn = psycopg2.connect(
        dbname=postgres_config.db_name,
        user=postgres_config.db_user,
        password=postgres_config.db_password,
        host=postgres_config.db_host,
        port=postgres_config.db_port)

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM notify_history WHERE status = 'failed'")
        columns = [desc[0] for desc in cur.description]
        failed_messages = [dict(zip(columns, row)) for row in cur.fetchall()]
    conn.close()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM notify_history WHERE status = 'failed'")
            columns = [desc[0] for desc in cur.description]
            failed_messages = [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        conn.close()

    if failed_messages:

        credentials = pika.PlainCredentials(rabbitmq_config.user,
                                            rabbitmq_config.password)
        parameters = pika.ConnectionParameters('localhost',
                                               credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        exchange = channel.exchange_declare(rabbitmq_config.exchange_name)
        queue = channel.queue_declare(rabbitmq_config.queue, durable=True)

        for message in failed_messages:
            message_body = json.dumps(message)
            message_body_bytes = message_body.encode()
            channel.basic_publish(
                exchange=rabbitmq_config.queue,
                routing_key='notifications_ready',
                body=message_body_bytes,
                properties=pika.BasicProperties(delivery_mode=2))

        logging.info('Message published to RabbitMQ')


checker_app.conf.CELERYBEAT_SCHEDULE = {
    'check-and-send-messages': {
        'task': 'tasks.check_and_send_messages',
        'schedule': 100,
    },
}
