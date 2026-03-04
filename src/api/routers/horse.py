import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi import APIRouter, HTTPException
from schemas import InputData
import pandas as pd
from utils import load_model

router = APIRouter(prefix="/horse", tags=["Horse"])

model_p1 = load_model("HORSE_P1")
model_p2 = load_model("HORSE_P2")

@router.post("/predict")
def predict_horse(data: InputData):
    try:
        df = pd.DataFrame([data.features])
        probs_p1 = model_p1.predict_proba(df)[0]
        probs_p2 = model_p2.predict_proba(df)[0]
        return {
            "paso1": {
                "prob_bronce": round(float(probs_p1[0]), 4),
                "prob_plata_oro": round(float(probs_p1[1]), 4),
            },
            "paso2": {
                "prob_plata": round(float(probs_p2[0]), 4),
                "prob_oro": round(float(probs_p2[1]), 4),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))