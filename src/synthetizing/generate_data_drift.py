from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N = 5_000
OUT = Path("data/production/data_drift.parquet")


def generate(n: int = N, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # ── Targets (distribución desviada → más Lead Oro en producción) ──────────
    horse_target = rng.choice(
        ["Lead Bronce", "Lead Plata", "Lead Oro"],
        size=n,
        p=[0.45, 0.35, 0.20],  # entrenamiento era ~[0.60, 0.30, 0.10]
    )
    prods_target = rng.choice(
        ["Lead Bronce", "Lead Plata", "Lead Oro"],
        size=n,
        p=[0.48, 0.33, 0.19],
    )

    # ── Numéricas — drift en comportamiento de navegación ─────────────────────
    # horses_viewed: usuarios ven más caballos en producción
    horses_viewed = rng.poisson(lam=9, size=n)  # ref: ~5

    # horses_added_to_cart: más agresivos
    horses_added_to_cart = rng.poisson(lam=3, size=n)  # ref: ~1

    # precios: distribución más alta y con mayor cola
    max_horse_price_viewed = rng.lognormal(mean=11.0, sigma=1.2, size=n).clip(
        0, 800_000
    )
    avg_horse_price_viewed = max_horse_price_viewed * rng.uniform(0.4, 0.9, size=n)
    min_horse_price_viewed = avg_horse_price_viewed * rng.uniform(0.1, 0.6, size=n)

    # engagement con segmentos premium — drift pronunciado
    viewed_premium_horses = rng.poisson(lam=3, size=n)  # ref: ~1
    viewed_sport_elite = rng.poisson(lam=2, size=n)  # ref: ~0.5
    viewed_family_safe = rng.poisson(lam=1, size=n)
    viewed_working_elite = rng.poisson(lam=1, size=n)
    viewed_pro_sellers = rng.poisson(lam=4, size=n)  # ref: ~2

    # características de los caballos vistos
    avg_horse_age = rng.normal(loc=9, scale=4, size=n).clip(0, 30)
    avg_prestige_score_horses = rng.normal(loc=65, scale=20, size=n).clip(0, 100)
    unique_regions_horses = rng.integers(1, 6, size=n)
    avg_height = rng.normal(loc=158, scale=10, size=n).clip(130, 185)
    avg_weight = rng.normal(loc=490, scale=60, size=n).clip(300, 700)
    has_registry_viewed = rng.integers(0, 2, size=n)
    has_shipping_viewed = rng.integers(0, 2, size=n)
    avg_tech_score = rng.normal(loc=55, scale=18, size=n).clip(0, 100)
    avg_temperament = pd.array(
        rng.normal(loc=3.2, scale=1.0, size=n).clip(1, 5), dtype="Float64"
    )
    avg_comment_length = rng.normal(loc=120, scale=50, size=n).clip(0, 500)
    caballos_unicos_vistos = rng.poisson(lam=6, size=n)  # ref: ~3

    # ratios — drift en recurrencia
    ratio_recurrencia_horse = rng.beta(a=3, b=4, size=n)  # ref: uniform(0,1)
    max_visitas_mismo_caballo = rng.normal(loc=4, scale=2, size=n).clip(0, 20)
    ratio_cart_horse = rng.beta(a=2, b=5, size=n)
    rango_precio_horse = rng.normal(loc=3, scale=1.5, size=n).clip(0, 10)

    # ── Numéricas — productos (sin drift fuerte) ──────────────────────────────
    products_viewed = rng.poisson(lam=6, size=n)
    products_added_to_cart = rng.poisson(lam=2, size=n)
    avg_product_price_viewed = rng.lognormal(mean=5, sigma=0.8, size=n).clip(0, 5000)
    max_product_price_viewed = avg_product_price_viewed * rng.uniform(1, 3, size=n)
    unique_categories = rng.integers(1, 8, size=n)
    viewed_waterproof = rng.poisson(lam=1, size=n)
    viewed_leather = rng.poisson(lam=1, size=n)
    viewed_breathable = rng.poisson(lam=1, size=n)
    viewed_uv_protection = rng.poisson(lam=0.5, size=n)
    viewed_machine_washable = rng.poisson(lam=0.5, size=n)
    avg_prestige_score_products = rng.normal(loc=55, scale=15, size=n).clip(0, 100)
    productos_unicos_vistos = rng.poisson(lam=4, size=n)
    ratio_recurrencia_prods = rng.uniform(0, 1, size=n)
    max_visitas_mismo_producto = rng.normal(loc=3, scale=1.5, size=n).clip(0, 15)
    ratio_cart_prods = rng.beta(a=2, b=6, size=n)

    # ── Globales ──────────────────────────────────────────────────────────────
    total_views = horses_viewed + products_viewed
    total_cart_adds = horses_added_to_cart + products_added_to_cart
    ratio_cart_global = np.where(total_views > 0, total_cart_adds / total_views, 0.0)
    ratio_horse_views = np.where(total_views > 0, horses_viewed / total_views, 0.0)
    prestige_gap = avg_prestige_score_horses - avg_prestige_score_products
    has_both_interests = ((horses_viewed > 0) & (products_viewed > 0)).astype(int)

    # ── Usuario — drift en región (más usuarios de nuevas zonas) ─────────────
    user_prestige_score = rng.integers(0, 100, size=n)
    user_antiguedad_dias = rng.integers(0, 1500, size=n)  # ref: hasta ~1000
    user_region = rng.choice(
        ["norte", "sur", "centro", "este", "oeste"],
        size=n,
        p=[0.15, 0.15, 0.20, 0.25, 0.25],  # ref: distribución más uniforme
    )
    user_card_issuer = rng.choice(
        ["visa", "mastercard", "amex", "naranja"],
        size=n,
        p=[0.35, 0.30, 0.15, 0.20],  # naranja: nueva tarjeta en producción
    )
    user_domain = rng.choice(
        ["gmail", "hotmail", "yahoo", "outlook", "empresa"],
        size=n,
        p=[0.40, 0.20, 0.10, 0.20, 0.10],
    )

    # ── Categóricas de caballos ───────────────────────────────────────────────
    gender_with_most_appearances = rng.choice(
        ["Macho", "Hembra", "Castrado"],
        size=n,
        p=[0.55, 0.35, 0.10],
    )
    breedFamily_with_most_appearances = rng.choice(
        ["Warmblood", "Thoroughbred", "Quarter", "Pony", "Draught"],
        size=n,
        p=[0.35, 0.30, 0.20, 0.10, 0.05],
    )
    color_grouped_with_most_appearances = rng.choice(
        ["bay", "black", "chestnut", "grey", "palomino", "roan"],
        size=n,
        p=[0.30, 0.20, 0.20, 0.15, 0.10, 0.05],
    )

    # ── Categóricas de productos ──────────────────────────────────────────────
    most_viewed_category = rng.choice(
        ["silla", "rienda", "manta", "protector", "herramienta"],
        size=n,
        p=[0.30, 0.25, 0.20, 0.15, 0.10],
    )
    most_viewed_brand = rng.choice(
        ["HorsePro", "EquiMax", "RiderElite", "StableMate", "WildRide"],
        size=n,
    )
    most_viewed_target_user = rng.choice(
        ["amateur", "profesional", "competidor", "recreativo"],
        size=n,
        p=[0.30, 0.25, 0.25, 0.20],
    )

    # ── Armar DataFrame con el mismo orden de columnas que df_final ───────────
    df = pd.DataFrame(
        {
            "horse_target": horse_target,
            "prods_target": prods_target,
            "horses_viewed": horses_viewed,
            "horses_added_to_cart": horses_added_to_cart,
            "avg_horse_price_viewed": avg_horse_price_viewed,
            "max_horse_price_viewed": max_horse_price_viewed,
            "min_horse_price_viewed": min_horse_price_viewed,
            "viewed_premium_horses": viewed_premium_horses,
            "viewed_sport_elite": viewed_sport_elite,
            "viewed_family_safe": viewed_family_safe,
            "avg_horse_age": avg_horse_age,
            "viewed_pro_sellers": viewed_pro_sellers,
            "avg_prestige_score_horses": avg_prestige_score_horses,
            "unique_regions_horses": unique_regions_horses,
            "avg_height": avg_height,
            "avg_weight": avg_weight,
            "gender_with_most_appearances": gender_with_most_appearances,
            "breedFamily_with_most_appearances": breedFamily_with_most_appearances,
            "has_registry_viewed": has_registry_viewed,
            "has_shipping_viewed": has_shipping_viewed,
            "color_grouped_with_most_appearances": color_grouped_with_most_appearances,
            "viewed_working_elite": viewed_working_elite,
            "avg_tech_score": avg_tech_score,
            "avg_temperament": avg_temperament,
            "avg_comment_length": avg_comment_length,
            "caballos_unicos_vistos": caballos_unicos_vistos,
            "user_prestige_score": user_prestige_score,
            "user_region": user_region,
            "user_card_issuer": user_card_issuer,
            "user_domain": user_domain,
            "user_antiguedad_dias": user_antiguedad_dias,
            "ratio_recurrencia_horse": ratio_recurrencia_horse,
            "max_visitas_mismo_caballo": max_visitas_mismo_caballo,
            "products_viewed": products_viewed,
            "products_added_to_cart": products_added_to_cart,
            "avg_product_price_viewed": avg_product_price_viewed,
            "max_product_price_viewed": max_product_price_viewed,
            "unique_categories": unique_categories,
            "most_viewed_category": most_viewed_category,
            "viewed_waterproof": viewed_waterproof,
            "viewed_leather": viewed_leather,
            "viewed_breathable": viewed_breathable,
            "viewed_uv_protection": viewed_uv_protection,
            "viewed_machine_washable": viewed_machine_washable,
            "most_viewed_brand": most_viewed_brand,
            "most_viewed_target_user": most_viewed_target_user,
            "avg_prestige_score_products": avg_prestige_score_products,
            "productos_unicos_vistos": productos_unicos_vistos,
            "ratio_recurrencia_prods": ratio_recurrencia_prods,
            "max_visitas_mismo_producto": max_visitas_mismo_producto,
            "total_views": total_views,
            "total_cart_adds": total_cart_adds,
            "ratio_cart_horse": ratio_cart_horse,
            "ratio_cart_prods": ratio_cart_prods,
            "ratio_cart_global": ratio_cart_global,
            "rango_precio_horse": rango_precio_horse,
            "prestige_gap": prestige_gap,
            "ratio_horse_views": ratio_horse_views,
            "has_both_interests": has_both_interests,
        }
    )

    return df


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_parquet(OUT, index=False)
    print(f"✅ Dataset con drift generado: {OUT}  ({len(df):,} filas)")
    print("\nDistribución horse_target:")
    print(df["horse_target"].value_counts(normalize=True).round(3).to_string())
    print("\nDrift simulado en:")
    print("  horses_viewed        → lam=9   (ref ~5)")
    print("  horses_added_to_cart → lam=3   (ref ~1)")
    print("  viewed_premium_horses → lam=3  (ref ~1)")
    print("  viewed_sport_elite   → lam=2   (ref ~0.5)")
    print("  max_horse_price_viewed → lognormal(11, 1.2)  (ref lognormal(10, 1))")
    print("  user_card_issuer     → naranja 20%  (ref 0%)")
    print("  user_region          → este/oeste 50%  (ref uniforme)")
    print("  Lead Oro             → 20%  (ref ~10%)")
