import os
import sys
from typing import Any
import logging
import uvicorn
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="[%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

model_registry = {
    "iris-model": {
        "service_name": "iris-model-service",
        "endpoint": "/predict",
        "port": 8001,
        "local_url": "http://localhost:8001/predict",
    },
}


def get_model_url(model_name):
    # check if model exists in registry
    if model_name not in model_registry:
        raise HTTPException(status_code=404, detail="Model not found")
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        # running on kubernetes
        service_name = model_registry[model_name]["service_name"]
        endpoint = model_registry[model_name]["endpoint"]
        port = model_registry[model_name]["port"]
        return f"http://{service_name}:{port}{endpoint}"
    else:
        # running locally
        return model_registry[model_name]["local_url"]


class PredictionRequest(BaseModel):
    model_name: str
    input_data: Any


@app.post("/predict")
async def predict(request: PredictionRequest):
    logger.info(
        f"Incoming request: [model_name: {request.model_name}] [data: {request.input_data}]"
    )

    model_url = get_model_url(request.model_name)
    logger.info(f"Model url: {model_url}")

    response = requests.post(model_url, json={"input_data": request.input_data})

    if response.status_code != 200:
        return {"error": "Failed to get prediction from model"}

    res = response.json()
    res["model_name"] = request.model_name

    logger.info(f"Prediction response: {res}")
    return res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
