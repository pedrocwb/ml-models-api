# ml-models-api
The `ml-models-api` repository contains the implementation of a FastAPI application designed to serve multiple machine 
learning models through a unified API. It provides a scalable and flexible architecture that allows for seamless integration 
and deployment of new models as separate pods in a Kubernetes environment. 

The repository includes code for handling requests, routing them to the appropriate models using a message broker (RabbitMQ), 
and caching predictions with Redis. Additionally, it incorporates monitoring, logging, and alerting capabilities using 
Prometheus, Grafana, and Alertmanager, as well as support for autoscaling and dynamic discovery of newly deployed models.