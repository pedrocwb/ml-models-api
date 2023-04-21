FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the model files
COPY main.py .

ENV KUBERNETES_SERVICE_HOST=true

# Start the app
EXPOSE 80
CMD uvicorn main:app  --host 0.0.0.0 --port 80