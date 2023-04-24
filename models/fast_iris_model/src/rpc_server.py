import abc
import json
import logging

import pika

from config import RMQ_HOST, RMQ_PASSWORD, RMQ_USER


class RabbitMQRPCServer:
    def __init__(self, queue: str):
        """
        Parameters:
        -----------
        queue : str
            The name of the RabbitMQ queue.

        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RMQ_HOST,
                credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD),
            ),
        )
        self.channel = self.connection.channel()
        self.queue = queue

    def on_request(self, ch, method, props, body):
        """
        Callback function for RabbitMQ consumer to process requests.

        Parameters:
        -----------
        ch : pika.channel.Channel
            The channel object.
        method : pika.spec.Basic.Deliver
            Method object.
        props : pika.spec.BasicProperties
            Properties object.
        body : bytes
            The body of the message.
        """
        input_data = json.loads(body)
        response = self.run_process(input_data)

        logging.info(f"[x] Prediction response {response}")

        ch.basic_publish(
            exchange="",
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """
        Start the RPC server by declaring the queue and setting up the consumer.

        """
        self.channel.queue_declare(queue=self.queue)
        self.channel.basic_qos(prefetch_count=5)
        self.channel.basic_consume(
            queue=self.queue, on_message_callback=self.on_request
        )

        logging.info(f" [x] Awaiting RPC requests on queue {self.queue}")
        self.channel.start_consuming()

    def stop(self):
        """
        Close the RabbitMQ connection.

        """
        self.connection.close()

    @abc.abstractmethod
    def run_process(self, *args):
        """
        Abstract method for running the model and returning predictions.

        Parameters:
        -----------
        *args
            Arguments required to run the model.

        Returns:
        --------
        dict
            A dictionary containing the prediction.

        """
        raise NotImplementedError
