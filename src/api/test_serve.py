import requests

API_URL = "https://equinelead-api-516367992092.us-east1.run.app/horse/predict"
#API_URL = "http://localhost:8080/horse/predict"

sample_input = {
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
    "extra_features": 0
  }

sample_input = {"features": sample_input}

response = requests.post(API_URL, json=sample_input)

print(f"Status code: {response.status_code}")
print("Prediction:", response.json())
