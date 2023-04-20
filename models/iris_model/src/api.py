import os
from typing import Any, List
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.model import IrisModel

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent


app = FastAPI()


class PredictionRequest(BaseModel):
    input_data: Any


class PredictionResponse(BaseModel):
    prediction: List[int]


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    model = IrisModel(f"{ROOT_DIR}/assets/iris_knn.joblib")
    prediction = model.predict(request.input_data)
    return {"prediction": prediction}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)



