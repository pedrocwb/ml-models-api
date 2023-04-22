import json
from typing import List

import pika
import uuid

from config import RMQ_HOST, RMQ_PASSWORD, RMQ_USER


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RabbitMQRPCClient(metaclass=Singleton):
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
