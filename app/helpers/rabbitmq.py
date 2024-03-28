import json
from contextlib import asynccontextmanager
from functools import partial

from aio_pika import DeliveryMode, ExchangeType, IncomingMessage, Message, connect

from app.helpers.db import DB_HELPER
from app.helpers.exceptions import RabbitMQError

from app.settings import APP_SETTINGS


class RabbitMQ:
    def __init__(
        self,
        host=APP_SETTINGS.RABBITMQ.RABBITMQ_HOST,
        port=APP_SETTINGS.RABBITMQ.RABBITMQ_PORT,
        username=APP_SETTINGS.RABBITMQ.RABBITMQ_USER,
        password=APP_SETTINGS.RABBITMQ.RABBITMQ_PASSWORD,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await connect(
            f"amqp://{self.username}:{self.password}@{self.host}:{self.port}",
            clientProperties={"connection_name": "Walle-service"},
        )
        self.channel = await self.connection.channel()

    async def declare_queue(self, queue_name):
        await self.channel.declare_queue(queue_name, durable=True)

    async def send_message(
        self,
        routing_key: str,
        message: dict,
    ):
        exchange = await self.channel.declare_exchange(
            APP_SETTINGS.RABBITMQ.EXCHANGE, ExchangeType.TOPIC, durable=True
        )
        message = Message(
            json.dumps(message.model_dump()).encode(),
            delivery_mode=DeliveryMode.NOT_PERSISTENT,
        )
        await exchange.publish(message, routing_key)

    async def consume_messages(self, queue_name, callback):
        queue = await self.channel.declare_queue(queue_name, durable=True)
        return await queue.consume(callback)

    async def close_connection(self):
        if self.connection and self.connection.is_open:
            await self.connection.close()


async def handle_payload(message: IncomingMessage, session_maker, queue_name: str):
    async with message.process():
        payload = message.body.decode()
        try:
            async with asynccontextmanager(session_maker)() as db:
                ...
        except Exception as e:
            print(e)
            raise RabbitMQError
        return {
            "subscribed": True,
            "consumption_started": True,
            "queue_name": queue_name,
        }


RMQ_Client = RabbitMQ()


async def consumer(queue_name: str = APP_SETTINGS.RABBITMQ.CONSUME_QUEUE):
    _handle = partial(
        handle_payload, session_maker=DB_HELPER.session_dependency, queue_name=queue_name
    )
    await RMQ_Client.consume_messages(queue_name, _handle)


async def producer(
    message: dict,
    queue_name: str = APP_SETTINGS.RABBITMQ.PUBLISH_QUEUE,
    routing_key: str = APP_SETTINGS.RABBITMQ.ROUTING_KEY,
):
    await RMQ_Client.declare_queue(queue_name)
    try:
        await RMQ_Client.send_message(routing_key=routing_key, message=message)
        print(f"Sent message: \n\n\t {message}")
    except Exception as e:
        print(e)
        raise RabbitMQError
