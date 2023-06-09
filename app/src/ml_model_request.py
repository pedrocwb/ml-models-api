import abc
import asyncio
import os
from typing import Any, Dict

import requests

from config import logger
from exceptions import ModelNotFoundException, QueueNotFoundException
from rmq_client import RabbitMQRPCClient, AsyncRabbitMQRPCClient


class MLModelRequest(abc.ABC):
    @abc.abstractmethod
    def request(self, model_name: str, input_data: Any):
        raise NotImplementedError


class RabbitMQConnectionPool:
    def __init__(self):
        self.connections = {}

    async def get_connection(self, model_name: str) -> AsyncRabbitMQRPCClient:
        if (
            model_name not in self.connections
            or self.connections[model_name].is_closed
            or self.connections[model_name].channel.is_closed
        ):
            queue = RMQModelRequest.get_queue(model_name)
            self.connections[model_name] = await AsyncRabbitMQRPCClient.create(queue=queue)
        return self.connections[model_name]

    async def close_all(self):
        logger.info("Closing all connections")
        for connection in self.connections:
            await connection.close()
        self.connections.clear()


class RMQModelRequest(MLModelRequest):

    """
    The RMQModelRequest class uses RabbitMQ to connect to a remote machine learning model service.
    It connects to a specific queue that is associated with a particular model and sends the input
    data to that queue. It then waits for a response from the model service, which is sent back to
    the application via the same queue.
    """

    MODEL_QUEUES = {
        "fast-iris-model": "fast_iris_model_queue",
        "intermediate-iris-model": "intermediate_iris_model_queue",
        "slow-iris-model": "slow_iris_model_queue",
    }
    connection_pool = RabbitMQConnectionPool()

    async def request(self, model_name: str, input_data: Any) -> Dict:
        client = await self.connection_pool.get_connection(model_name)

        logger.info(f" [x] Requesting predictions for {input_data}")
        response = await client.call(input_data)
        logger.info(f" [x] Got response {response}")

        return response

    @classmethod
    def get_queue(self, model_name: str) -> str:
        if model_name not in self.MODEL_QUEUES:
            raise QueueNotFoundException("Model queue not found")
        return self.MODEL_QUEUES.get(model_name)


class HTTPModelRequest(MLModelRequest):
    """
    The HTTPModelRequest class uses a REST API to connect to a remote machine learning model service.
    It connects to a specific URL that is associated with a particular model and sends the input data
    via a POST request to that URL. It then waits for a response from the model service,
    which is sent back to the application as a JSON object.
    """

    MODEL_REGISTRY = {
        "iris-model": {
            "service_name": "iris-model-service",
            "endpoint": "/predict",
            "port": 8001,
            "local_url": "http://localhost:8001/predict",
        },
    }

    def request(self, model_name: str, input_data: Any):
        model_url = self.get_model_url(model_name)
        logger.info(f"Model url: {model_url}")

        response = requests.post(model_url, json={"input_data": input_data})

        if response.status_code != 200:
            return {"error": "Failed to get prediction from model"}

        return response

    def get_model_url(self, model_name):
        # check if model exists in registry
        if model_name not in self.MODEL_REGISTRY:
            raise ModelNotFoundException("Model not found in model registry")

        if os.getenv("KUBERNETES_SERVICE_HOST"):
            # running on kubernetes
            service_name = self.MODEL_REGISTRY[model_name]["service_name"]
            endpoint = self.MODEL_REGISTRY[model_name]["endpoint"]
            port = self.MODEL_REGISTRY[model_name]["port"]
            return f"http://{service_name}:{port}{endpoint}"
        else:
            # running locally
            return self.MODEL_REGISTRY[model_name]["local_url"]
