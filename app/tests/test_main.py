import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app, get_model_url
import requests_mock


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_predict(client):
    payload = {
        "model_name": "iris-model",
        "input_data": [
            [5.1, 3.5, 1.4, 0.2],
            [6.2, 3.4, 5.4, 2.3],
            [4.3, 3.0, 1.1, 0.1],
        ],
    }

    with requests_mock.Mocker() as m:
        # mock the call of the model
        m.post("http://localhost:8001/predict", json={"prediction": [0, 2, 0]})

        # call the API endpoint
        response = client.post("http://0.0.0.0:8000/predict", json=payload)

        assert response.status_code == 200
        assert response.json()["prediction"] == [0, 2, 0]
        assert response.json()["model_name"] == "iris-model"


def test_model_url(monkeypatch):
    monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "true")
    model_url = get_model_url("iris-model")
    assert model_url == "http://iris-model-service:80/predict"

    monkeypatch.delenv("KUBERNETES_SERVICE_HOST")
    model_url = get_model_url("iris-model")
    assert model_url == "http://localhost:8001/predict"

    with pytest.raises(HTTPException) as exc_info:
        model_url = get_model_url("blah-model")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Model not found"
