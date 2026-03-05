from fastapi import APIRouter, HTTPException
from schemas import HorseRecommendRequest
from utils import load_bundle

router = APIRouter(prefix="/recommender", tags=["Recommender"])

bundle = load_bundle("model_engine")
model = bundle["model"]
vectorizer = bundle["vectorizer"]
scaler = bundle["scaler"]
transform_input = bundle["transform_fn"]  # cloudpickle serializa el bytecode completo


@router.post("/recommend")
def recommend(data: HorseRecommendRequest):
    """
    Recibe breed, color y price y devuelve los caballos más similares.

    Request body:
        {
            "breed": "Thoroughbred",
            "color": "bay",
            "price": 5000.0
        }
    """
    try:
        X = transform_input(
            {"breed": data.breed, "color": data.color, "price": data.price},
            vectorizer,
            scaler,
        )

        distances, indices = model.kneighbors(X)

        return {
            "neighbors": [
                {"index": int(idx), "distance": round(float(dist), 4)}
                for idx, dist in zip(indices[0], distances[0])
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
