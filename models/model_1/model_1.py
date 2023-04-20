from models.base_model import BaseModel


class Model1(BaseModel):
    def predict(self, input_data: str):
        preprocessed_data = self.preprocess(input_data)
        prediction = self.model.predict(preprocessed_data)

        return prediction

    def preprocess(self, input_data: str):
        return input_data
