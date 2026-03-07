import pytest
import requests

API_URL = "https://equinelead-api-516367992092.us-east1.run.app"
# API_URL = "http://localhost:8080/prods/predict"


@pytest.fixture
def sample_horse():
    return {
        "features": {
            "avg_comment_length": 0,
            "avg_height": 0,
            "avg_horse_age": 0,
            "avg_prestige_score_horses": 0,
            "avg_tech_score": 0,
            "avg_temperament": 0,
            "avg_weight": 0,
            "caballos_unicos_vistos": 0,
            "has_registry_viewed": 0,
            "has_shipping_viewed": 0,
            "horses_added_to_cart": 0,
            "horses_viewed": 0,
            "max_horse_price_viewed": 0,
            "max_visitas_mismo_caballo": 0,
            "rango_precio_horse": 0,
            "ratio_cart_horse": 0,
            "ratio_recurrencia_horse": 0,
            "user_antiguedad_dias": 0,
            "user_card_issuer": 0,
            "user_domain": 0,
            "user_prestige_score": 0,
            "user_region": 0,
            "viewed_family_safe": 0,
            "viewed_premium_horses": 0,
            "viewed_pro_sellers": 0,
            "viewed_sport_elite": 0,
            "viewed_working_elite": 0,
        }
    }


@pytest.fixture
def sample_prods():
    return {
        "features": {
            "avg_prestige_score_products": 0,
            "avg_product_price_viewed": 0,
            "max_product_price_viewed": 0,
            "most_viewed_brand": 0,
            "most_viewed_category": 0,
            "most_viewed_target_user": 0,
            "productos_unicos_vistos": 0,
            "products_added_to_cart": 0,
            "products_viewed": 0,
            "ratio_cart_prods": 0,
            "ratio_recurrencia_prods": 0,
            "unique_categories": 0,
            "user_antiguedad_dias": 0,
            "user_card_issuer": 0,
            "user_domain": 0,
            "user_prestige_score": 0,
            "user_region": 0,
            "viewed_breathable": 0,
            "viewed_leather": 0,
            "viewed_machine_washable": 0,
            "viewed_uv_protection": 0,
            "viewed_waterproof": 0,
        }
    }


@pytest.fixture
def sample_recommender():
    return {
        "breed": "andalusian",
        "color": "bay",
        "price": 22000.0,
    }


def test_horse_predict_status(sample_horse):
    response = requests.post(f"{API_URL}/horse/predict", json=sample_horse)
    assert response.status_code == 200


def test_horse_predict_schema(sample_horse):
    response = requests.post(f"{API_URL}/horse/predict", json=sample_horse)
    data = response.json()
    assert "paso1" in data
    assert "paso2" in data
    assert "prob_bronce" in data["paso1"]
    assert "prob_plata_oro" in data["paso1"]
    assert "prob_plata" in data["paso2"]
    assert "prob_oro" in data["paso2"]


def test_prods_predict_status(sample_prods):
    response = requests.post(f"{API_URL}/prods/predict", json=sample_prods)
    assert response.status_code == 200


def test_prods_predict_schema(sample_prods):
    response = requests.post(f"{API_URL}/prods/predict", json=sample_prods)
    data = response.json()
    assert "paso1" in data
    assert "paso2" in data
    assert "prob_bronce" in data["paso1"]
    assert "prob_plata_oro" in data["paso1"]
    assert "prob_plata" in data["paso2"]
    assert "prob_oro" in data["paso2"]


def test_recommender_status(sample_recommender):
    response = requests.post(
        f"{API_URL}/recommender/recommend", json=sample_recommender
    )
    assert response.status_code == 200


def test_recommender_schema(sample_recommender):
    response = requests.post(
        f"{API_URL}/recommender/recommend", json=sample_recommender
    )
    data = response.json()
    assert "neighbors" in data
    assert len(data["neighbors"]) > 0
    assert "index" in data["neighbors"][0]
    assert "distance" in data["neighbors"][0]
