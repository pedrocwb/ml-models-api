import json
from typing import List
import asyncio
import aio_pika
import pika
import uuid

from config import RMQ_HOST, RMQ_PASSWORD, RMQ_USER


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RabbitMQRPCClient:
    def __init__(self, queue: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RMQ_HOST,
                credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD),
            ),
        )

        self.channel = self.connection.channel()
        self.queue = queue
        self.callback_queue = self.channel.queue_declare(
            queue="", exclusive=True
        ).method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, input_data: List[List[int]]):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue, correlation_id=self.corr_id
            ),
            body=json.dumps(input_data),
        )

        while self.response is None:
            self.connection.process_data_events()
        return self.response

    @property
    def is_closed(self):
        return self.connection.is_closed

    def close(self):
        self.connection.close()


class AsyncRabbitMQRPCClient:
    def __init__(self, queue: str):
        self.queue = queue
        self.response = None
        self.corr_id = None

        self.response_received = asyncio.Event()

    @classmethod
    async def create(cls, queue: str):
        client = cls(queue)
        await client.connect()
        return client

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}"
        )

        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)

        await self.callback_queue.consume(self.on_response)

    async def on_response(self, message: aio_pika.IncomingMessage):
        async with message.process():
            if self.corr_id == message.correlation_id:
                self.response = json.loads(message.body)
                self.response_received.set()

    async def call(self, input_data: List[List[int]]):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(input_data).encode(),
                correlation_id=self.corr_id,
                reply_to=self.callback_queue.name
            ),
            routing_key=self.queue
        )

        await self.response_received.wait()
        self.response_received.clear()
        return self.response

    @property
    def is_closed(self):
        return self.connection.is_closed

    async def close(self):
        await self.connection.close()