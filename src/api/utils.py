import pickle
import os
import json

ARTIFACTS_PATH = "./models/production"

def load_model(name: str):
    path = os.path.join(ARTIFACTS_PATH, name, "model.pkl")
    with open(path, "rb") as f:
        return pickle.load(f)
    
def load_input_example(name: str):
    path = os.path.join(ARTIFACTS_PATH, name, "input_example.json")
    with open(path) as f:
        return json.load(f)