import xgboost as xgb
import os

ARTIFACTS_PATH = "./models/production"

def load_model(name: str):
    path = os.path.join(ARTIFACTS_PATH, name, "model.ubj")
    model = xgb.XGBClassifier()
    model.load_model(path)
    return model