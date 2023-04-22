from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.src.config import logger
from app.src.exceptions import MLModelRequestNotFoundException
from app.src.ml_model_request import RMQModelRequest

app = FastAPI()


class PredictionRequest(BaseModel):
    model_name: str
    input_data: Any


@app.post("/predict")
async def predict(request: PredictionRequest):
    logger.info(
        f"Incoming request: [model_name: {request.model_name}] [data: {request.input_data}]"
    )
    try:
        model_request = RMQModelRequest()
        response = model_request.request(request.model_name, request.input_data)
    except MLModelRequestNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.args)

    response["model_name"] = request.model_name

    logger.info(f"Request response: [response: {response}]")
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
