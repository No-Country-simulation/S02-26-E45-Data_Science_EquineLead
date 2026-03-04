from pydantic import BaseModel

class InputData(BaseModel):
    features: dict

class HorsePredictRequest(InputData):
    model_config = {
        "json_schema_extra": {
            "example": {
                "features": {
                    "avg_comment_length": 0.0,
                    "avg_height": 0.0,
                    "avg_horse_age": 0.0,
                    "avg_prestige_score_horses": 0.0,
                    "avg_tech_score": 0.0,
                    "avg_temperament": 0.0,
                    "avg_weight": 0.0,
                    "caballos_unicos_vistos": 0,
                    "has_registry_viewed": 0,
                    "has_shipping_viewed": 0,
                    "horses_added_to_cart": 0,
                    "horses_viewed": 0,
                    "max_horse_price_viewed": 0.0,
                    "max_visitas_mismo_caballo": 0,
                    "rango_precio_horse": 0,
                    "ratio_cart_horse": 0.0,
                    "ratio_recurrencia_horse": 0.0,
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
        }
    }

class ProdsPredictRequest(InputData):
    model_config = {
        "json_schema_extra": {
            "example": {
                "features": {
                    "avg_prestige_score_products": 0.0,
                    "avg_product_price_viewed": 0.0,
                    "max_product_price_viewed": 0.0,
                    "most_viewed_brand": 0,
                    "most_viewed_category": 0,
                    "most_viewed_target_user": 0,
                    "productos_unicos_vistos": 0,
                    "products_added_to_cart": 0,
                    "products_viewed": 0,
                    "ratio_cart_prods": 0.0,
                    "ratio_recurrencia_prods": 0.0,
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
        }
    }