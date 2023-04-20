FROM python:3.10-slim

ARG MODEL_NAME

WORKDIR /model_app

# Install dependencies
COPY ${MODEL_NAME}/requirements.txt .
RUN pip install -r requirements.txt

# Copy the model files
COPY ${MODEL_NAME}  ./${MODEL_NAME}
ENV PYTHONPATH="./${MODEL_NAME}"


# Start the app
EXPOSE 80
CMD uvicorn api:app --app-dir ${PYTHONPATH}/src --host 0.0.0.0 --port 80