# ML Models API

This project aims to create a system that runs on Kubernetes and serves multiple machine learning models through a single API. The system is designed to handle multiple requests and forward them to the appropriate models. The models can scale horizontally to respond in a timely manner.

## Technical Details

### App
- The `app/` directory contains the FastAPI endpoint `/predict`, which is responsible for handling incoming requests.
- MLModelRequest is a wrapper that connects to the running RabbitMQ server and maintains a pool of connections to different RabbitMQ queues based on the available models to be requested.
- The request input should contain the `model_name` which will be mapped to the appropriate queue.
- MLModelRequest receives the response from the model in another queue.
- The FastAPI endpoint checks if the incoming request is cached using Redis and returns cached results instead.
- The API is configured to scale when it reaches 80% of CPU usage to ensure that the requests are being processed efficiently.

The `app/src/ml_model_request.py` file contains the RabbitMQConnectionPool class, which is responsible for managing connections to the RabbitMQ server. 
Additionally, the RMQModelRequest class is an implementation of the MLModelRequest abstract base class, which uses RabbitMQ to connect to a remote machine learning model service.
It connects to a specific queue associated with a particular model and sends the input data to that queue. 
It then waits for a response from the model service, which is sent back to the application via the RabbitMQ queue.

In the `app/src/rmq_client.py` file, the RabbitMQRPCClient class is responsible for creating connections to the RabbitMQ server, sending messages, and receiving responses.
It uses the pika library to create a blocking connection to the server, create a channel, and declare a callback queue for receiving responses. 
The call method is used to send input data to the model service and wait for a response, which is then returned to the caller.


### Models
### Models
- The `models/` directory can contain multiple models.
- Each model is implemented in a separate folder (e.g., `fast_iris_model`, `intermediate_iris_model`, `slow_iris_model`) with its own `src` directory.
- Inside the `src` directory, the `model.py` file contains the `Model` class, which loads a the model and uses it to predict. The `Model` class utilizes the Singleton design pattern to ensure that only one instance of the class is created.
- The `RPCServer` class is also defined in the `model.py` file. This class inherits from the `RabbitMQRPCServer` class, which is defined in the `rpc_server.py` file. The `RPCServer` class sets up an RPC server for serving the model object predictions.
- The `RabbitMQRPCServer` class is an abstract class that sets up a RabbitMQ connection and defines methods for starting and stopping the RPC server. It also contains an abstract method, `run_process`, that should be implemented by the model-specific RPC server class (e.g., `IrisRPCServer`).
- The main method in the `model.py` file is responsible for parsing command-line arguments to specify the name of the queue for the model server, creating an instance of the IrisRPCServer class using the specified queue name and the path to the model file, and starting the server.
- Each model's Kubernetes deployment configuration is located in its respective `k8s` directory.
- The models are configured to scale when they reach 80% of CPU usage to ensure that the requests are being processed efficiently.

### Kubernetes Configuration
- The `k8s-config/` directory contains Kubernetes configuration files for different resources used in the project.
- Locust load testing script.
- Configuration for the Kubernetes Metrics Server.
- Configuration for the RabbitMQ Cluster Operator.
- Configuration for the RabbitMQ cluster.
- Configuration for the Redis server deployment.

## Features
- Horizontal scaling
- Load balancing
- Caching
- Message queue

## Future Improvements
- Monitoring and Alerting: Integration of Prometheus and Grafana for monitoring the system's performance and setting up alerts for potential issues.
- Model Registry: Incorporation of a model registry to manage and track different versions of machine learning models.
- CI/CD Pipeline: Implementation of a Continuous Integration and Continuous Deployment (CI/CD) pipeline for smooth development and deployment of updates.
- Code Sharing: Enhance code sharing between models, making it easier to develop and maintain multiple models in the system.

## Instructions

**Prerequisites:** You have already installed and configured a local or remote Kubernetes cluster.

### Install Kubernetes Resources
Install metrics server, RabbitMQ, and Redis servers:
```
kubectl apply -f ml-models-api/k8s-config/
```

### Deploy the API
Build and push the API images and deploy to Kubernetes:
```
sh ml-models-api/build_app_images.sh
kubectl apply -f ml-models-api/app/k8s/deployment.yaml
```

### Deploy the Models
Build and push the model images and deploy:
```
sh ml-models-api/models/build_model_images.sh

kubectl apply -f ml-models-api/model/fast_iris_model/k8s/deployment.yaml
kubectl apply -f ml-models-api/model/intermediate_iris_model/k8s/deployment.yaml
kubectl apply -f ml-models-api/model/slow_iris_model/k8s/deployment.yaml
```

### Load Test the System
Install Locust on your machine and run:
```
locust -f ml-models-api/k8s-config/locust/locustfile.py
```

Access `http://0.0.0.0:8089/` and configure the Number of users (peak concurrency) and Spawn rate (users started/second). Monitor the models scaling in Kubernetes.