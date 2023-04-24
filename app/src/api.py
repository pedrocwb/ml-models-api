import json
from typing import Any
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import logger
from exceptions import MLModelRequestNotFoundException
from ml_model_request import RMQModelRequest
import redis

app = FastAPI()


redis_client = redis.Redis(host="redis.default.svc.cluster.local", port=6379, db=0)


class PredictionRequest(BaseModel):
    model_name: str
    input_data: Any


@app.post("/predict")
async def predict(request: PredictionRequest):
    logger.info(
        f"Incoming request: [model_name: {request.model_name}] [data: {request.input_data}]"
    )
    try:
        cache_key = "predict:" + str(hash(request.json()))
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for {cache_key}")
            return json.loads(cached_result)

        logger.info(f"Cache miss for {cache_key}")

        model_request = RMQModelRequest()
        response = model_request.request(request.model_name, request.input_data)
    except MLModelRequestNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.args)

    response["model_name"] = request.model_name
    redis_client.set(cache_key, json.dumps(response), ex=3600)

    logger.info(f"Request response: [response: {response}]")

    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
