

docker build . --build-arg MODEL_NAME=fast_iris_model \
  --tag pedrocwb/fast-iris-model-rmq \
  && docker push pedrocwb/fast-iris-model-rmq

docker build . --build-arg MODEL_NAME=intermediate_iris_model \
  --tag pedrocwb/intermediate-iris-model-rmq \
  && docker push pedrocwb/intermediate-iris-model-rmq


docker build . --build-arg MODEL_NAME=slow_iris_model \
  --tag pedrocwb/slow-iris-model-rmq \
  && docker push pedrocwb/slow-iris-model-rmq

