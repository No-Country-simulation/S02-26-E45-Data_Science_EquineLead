import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from fastapi import APIRouter, HTTPException
from schemas import ProdsPredictRequest
from utils import load_model

router = APIRouter(prefix="/prods", tags=["Products"])

model_p1 = load_model("PRODS_P1")
model_p2 = load_model("PRODS_P2")


def validate_features(features: dict, expected_features):
    expected = set(expected_features)
    received = set(features.keys())

    extra = received - expected
    missing = expected - received

    if extra:
        raise HTTPException(
            status_code=422, detail=f"Features no soportadas: {sorted(extra)}"
        )
    if missing:
        raise HTTPException(
            status_code=422, detail=f"Features faltantes: {sorted(missing)}"
        )

    nulls = [k for k, v in features.items() if v is None]
    if nulls:
        raise HTTPException(
            status_code=422, detail=f"Features con valor nulo: {sorted(nulls)}"
        )

    string_errors = [k for k, v in features.items() if isinstance(v, str)]
    if string_errors:
        raise HTTPException(
            status_code=422,
            detail=f"Features con tipo string no permitido: {sorted(string_errors)}",
        )


def run_prediction(features: dict):
    df = pd.DataFrame([features])
    df = df[model_p1.feature_names_in_]
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


@router.post("/predict")
def predict_prods(data: ProdsPredictRequest):
    try:
        validate_features(data.features, model_p1.feature_names_in_)
        return run_prediction(data.features)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
