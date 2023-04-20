import pytest

from src.model import IrisModel

@pytest.mark.parametrize(
    "input_data, output", [
        ([[0, 0, 0, 0]], 0),
        ([[10, 10, 10, 10]], 2),
    ]
)
def test_iris_model(input_data, output):
    model = IrisModel("../assets/iris_knn.joblib")
    res = model.predict(input_data)

    assert isinstance(res, list)
    assert res[0] == output