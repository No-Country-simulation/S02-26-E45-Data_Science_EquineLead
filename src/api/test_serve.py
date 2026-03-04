import requests

API_URL = "https://equinelead-api-516367992092.us-east1.run.app/horse/predict"
#API_URL = "http://localhost:8080/horse/predict"

sample_input = {
    "horses_viewed": 9.0,
    "horses_added_to_cart": 1.0,
    "avg_horse_price_viewed": 23272.727272727272,
    "max_horse_price_viewed": 30000.0,
    "min_horse_price_viewed": 20000.0,
    "viewed_premium_horses": 0.0,
    "viewed_sport_elite": 8.0,
    "viewed_family_safe": 0.0,
    "avg_horse_age": 6.6,
    "viewed_pro_sellers": 9.0,
    "avg_prestige_score_horses": 3.0,
    "unique_regions_horses": 1.0,
    "avg_height": 16.0,
    "avg_weight": 1053.8181818181818,
    "has_registry_viewed": 1.0,
    "has_shipping_viewed": 1.0,
    "viewed_working_elite": 0.0,
    "avg_tech_score": 3.6363636363636362,
    "avg_temperament": 3.909090909090909,
    "avg_comment_length": 121.45454545454545,
    "caballos_unicos_vistos": 10.0,
    "user_prestige_score": 3.0,
    "user_region": 0.06499441120389243,
    "user_card_issuer": 0.06678014927327484,
    "user_domain": 0.06456237604836204,
    "user_antiguedad_dias": 183.0,
    "ratio_recurrencia_horse": 0.8181818181818182,
    "max_visitas_mismo_caballo": 1.0,
    "products_viewed": 11.0,
    "products_added_to_cart": 1.0,
    "avg_product_price_viewed": 705.7038461538461,
    "max_product_price_viewed": 1619.1,
    "unique_categories": 5.0,
    "viewed_waterproof": 2.0,
    "viewed_leather": 7.0,
    "viewed_breathable": 4.0,
    "viewed_uv_protection": 0.0,
    "viewed_machine_washable": 1.0,
    "avg_prestige_score_products": 3.0,
    "productos_unicos_vistos": 10.0,
    "ratio_recurrencia_prods": 1.0,
    "max_visitas_mismo_producto": 2.0,
    "total_views": 20.0,
    "total_cart_adds": 2.0,
    "ratio_cart_horse": 0.1,
    "ratio_cart_prods": 0.08333333333333333,
    "ratio_cart_global": 0.09523809523809523,
    "rango_precio_horse": 10000.0,
    "prestige_gap": 0.0,
    "ratio_horse_views": 0.42857142857142855,
    "has_both_interests": 1.0
}

sample_input = {"features": sample_input}

response = requests.post(API_URL, json=sample_input)

print(f"Status code: {response.status_code}")
print("Prediction:", response.json())
