from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class PredictionRequest(BaseModel):
    input_data: str


@app.post("/predict")
async def predict(request: PredictionRequest):
    # model_output = model.predict(request.input_data)
    model_output = ""
    return {"prediction": model_output}
