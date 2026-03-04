from pydantic import BaseModel

class InputData(BaseModel):
    features: dict