import pytest
from fastapi.testclient import TestClient

from src.api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_predict(client):
    payload = {
        "input_data": [
            [5.1, 3.5, 1.4, 0.2],
            [6.2, 3.4, 5.4, 2.3],
            [4.3, 3.0, 1.1, 0.1]
        ]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["prediction"] == [0, 2, 0]

