FROM python:3.10-slim

ARG MODEL_NAME

WORKDIR /model_app

# Install dependencies
COPY ${MODEL_NAME}/requirements.txt .
RUN pip install -r requirements.txt

# Copy the model files
COPY ${MODEL_NAME}  .
ENV QUEUE_NAME=${MODEL_NAME}_queue



# Start the app
EXPOSE 80
CMD python src/model.py --queue ${QUEUE_NAME}