import sys
import os
from typing import Any, List
from pathlib import Path
import logging
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.model import IrisModel

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="[%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()


class PredictionRequest(BaseModel):
    input_data: Any


class PredictionResponse(BaseModel):
    prediction: List[int]


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    logger.info(f"Incoming request: {request.input_data}")

    model = IrisModel(f"{ROOT_DIR}/assets/iris_knn.joblib")
    prediction = model.predict(request.input_data)

    logger.info(f"Prediction response: {prediction}")
    return {"prediction": prediction}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
