from locust import HttpUser, task, between
import json
import random


class PredictionUser(HttpUser):
    abstract = True
    host = "http://localhost:8080"
    wait_time = between(1, 2)

    def input_data(self):
        input_data = [
            [
                random.uniform(0, 10),  # Replace with appropriate input range
                random.uniform(0, 10),
                random.uniform(0, 10),
                random.uniform(0, 10),
            ]
            for _ in range(10)  # Generate 10 input samples
        ]
        return input_data

    def make_request(self, model_name: str):
        input_data = self.input_data()
        headers = {"Content-Type": "application/json"}
        data = json.dumps({"model_name": model_name, "input_data": input_data})
        self.client.post("/predict", data=data, headers=headers)


class FastModelUser(PredictionUser):
    weight = 3

    @task
    def model_predict(self):
        self.make_request("fast-iris-model")


class IntermediateUser(PredictionUser):
    weight = 2

    @task
    def model_predict(self):
        self.make_request("intermediate-iris-model")


class SlowUser(PredictionUser):
    weight = 1

    @task
    def model_predict(self):
        self.make_request("slow-iris-model")
