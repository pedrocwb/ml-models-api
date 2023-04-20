from typing import Any, Dict, List, Union

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.model import IrisModel

app = FastAPI()


class PredictionRequest(BaseModel):
    input_data: Any


class PredictionResponse(BaseModel):
    prediction: List[int]


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    model = IrisModel("../assets/iris_knn.joblib")
    prediction = model.predict(request.input_data)
    return {"prediction": prediction}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



