import json
from utils import load_input_example

# Cargar input example
data = load_input_example("HORSE_P1")

sample_input = dict(zip(data["columns"], data["data"][0]))

sample_response = {
    "paso1": {
        "prob_bronce": 0.3, "prob_plata_oro": 0.7
        },
    "paso2": {
        "prob_plata": 0.4, "prob_oro": 0.6
        },
}

style = "padding: 8px; border: 1px solid #ddd;"

feature_descriptions = [
    ("horses_viewed", "Total de caballos vistos", ">= 0", "Float"),
    ("horses_added_to_cart", "Caballos agregados al carrito", ">= 0", "Float"),
    ("avg_horse_price_viewed", "Precio promedio de caballos vistos", ">= 0", "Float"),
    ("max_horse_price_viewed", "Precio máximo de caballos vistos", ">= 0", "Float"),
    ("min_horse_price_viewed", "Precio mínimo de caballos vistos", ">= 0", "Float"),
    ("viewed_premium_horses", "Cantidad de caballos premium vistos", ">= 0", "Float"),
    ("viewed_sport_elite", "Caballos sport/elite vistos", ">= 0", "Float"),
    ("viewed_family_safe", "Caballos family/safe vistos", ">= 0", "Float"),
    ("avg_horse_age", "Edad promedio de caballos vistos", ">= 0", "Float"),
    ("viewed_pro_sellers", "Caballos de vendedores pro vistos", ">= 0", "Float"),
    ("avg_prestige_score_horses", "Prestigio promedio de caballos vistos", ">= 0", "Float"),
    ("unique_regions_horses", "Regiones únicas de caballos vistos", ">= 0", "Float"),
    ("avg_height", "Altura promedio de caballos vistos", ">= 0", "Float"),
    ("avg_weight", "Peso promedio de caballos vistos", ">= 0", "Float"),
    ("has_registry_viewed", "Vio caballos con registro", "0 / 1", "Float"),
    ("has_shipping_viewed", "Vio caballos con envío", "0 / 1", "Float"),
    ("viewed_working_elite", "Caballos working/elite vistos", ">= 0", "Float"),
    ("avg_tech_score", "Score técnico promedio de caballos", ">= 0", "Float"),
    ("avg_temperament", "Temperamento promedio de caballos vistos", ">= 0", "Float"),
    ("avg_comment_length", "Longitud promedio de comentarios", ">= 0", "Float"),
    ("caballos_unicos_vistos", "Caballos únicos vistos", ">= 0", "Float"),
    ("user_prestige_score", "Score de prestigio del usuario", ">= 0", "Float"),
    ("user_region", "Región del usuario", "String", "Float"),
    ("user_card_issuer", "Emisor de tarjeta del usuario", "String", "Float"),
    ("user_domain", "Dominio del usuario", "String", "Float"),
    ("user_antiguedad_dias", "Antigüedad del usuario en días", ">= 0", "Float"),
    ("ratio_recurrencia_horse", "Ratio de recurrencia en caballos", "0–1", "Float"),
    ("max_visitas_mismo_caballo", "Máximo de visitas al mismo caballo", ">= 0", "Float"),
    ("products_viewed", "Total de productos vistos", ">= 0", "Float"),
    ("products_added_to_cart", "Productos agregados al carrito", ">= 0", "Float"),
    ("avg_product_price_viewed", "Precio promedio de productos vistos", ">= 0", "Float"),
    ("max_product_price_viewed", "Precio máximo de productos vistos", ">= 0", "Float"),
    ("unique_categories", "Categorías únicas de productos vistos", ">= 0", "Float"),
    ("viewed_waterproof", "Productos waterproof vistos", ">= 0", "Float"),
    ("viewed_leather", "Productos de cuero vistos", ">= 0", "Float"),
    ("viewed_breathable", "Productos transpirables vistos", ">= 0", "Float"),
    ("viewed_uv_protection", "Productos con protección UV vistos", ">= 0", "Float"),
    ("viewed_machine_washable", "Productos lavables a máquina vistos", ">= 0", "Float"),
    ("avg_prestige_score_products", "Prestigio promedio de productos vistos", ">= 0", "Float"),
    ("productos_unicos_vistos", "Productos únicos vistos", ">= 0", "Float"),
    ("ratio_recurrencia_prods", "Ratio de recurrencia en productos", "0–1", "Float"),
    ("max_visitas_mismo_producto", "Máximo de visitas al mismo producto", ">= 0", "Float"),
    ("total_views", "Total de vistas combinadas", ">= 0", "Float"),
    ("total_cart_adds", "Total de agregados al carrito", ">= 0", "Float"),
    ("ratio_cart_horse", "Ratio carrito/vistas caballos", "0–1", "Float"),
    ("ratio_cart_prods", "Ratio carrito/vistas productos", "0–1", "Float"),
    ("ratio_cart_global", "Ratio carrito/vistas global", "0–1", "Float"),
    ("rango_precio_horse", "Rango de precios de caballos vistos", ">= 0", "Float"),
    ("prestige_gap", "Diferencia de prestigio horse vs prods", ">= 0", "Float"),
    ("ratio_horse_views", "Ratio de vistas de caballos vs total", "0–1", "Float"),
    ("has_both_interests", "Tiene interés en caballos y productos", "0 / 1", "Float"),
]

feature_rows = "\n".join([
    f"<tr><td style={style}>{name}</td><td style={style}>{desc}</td><td style={style}>{rng}</td><td style={style}>{typ}</td></tr>"
    for name, desc, rng, typ in feature_descriptions
])

feature_table = f"""
<div style="overflow-x: auto;">
    <table border="1" style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="padding: 12px; text-align: left;">Feature Name</th>
                <th style="padding: 12px; text-align: left;">Description</th>
                <th style="padding: 12px; text-align: left;">Typical Range</th>
                <th style="padding: 12px; text-align: left;">Type</th>
            </tr>
        </thead>
        <tbody>
            {feature_rows}
        </tbody>
    </table>
</div>
"""

def get_docs_html() -> str:
    request_example = json.dumps({"features": sample_input}, indent=4)
    response_example = json.dumps(sample_response, indent=4)
    python_example = json.dumps(sample_input, indent=8)

    return f"""
<html>
<head>
    <title>EquineLead API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #2a6496; border-bottom: 1px solid #eee; }}
        h2 {{ color: #3a7abf; }}
        .endpoint {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .code-block {{ background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .try-button {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 10px 15px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .badge {{ display: inline-block; background: #2a6496; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }}
    </style>
</head>
<body>
    <h1>🐴 EquineLead API</h1>
    <p>Lead scoring API for equestrian e-commerce. Classifies users into <strong>Lead Bronce</strong>, <strong>Lead Plata</strong>, or <strong>Lead Oro</strong> based on their browsing behavior.</p>

    <div class="endpoint">
        <h2>Endpoints</h2>
        <p><span class="badge">POST</span> <code>/horse/predict</code> — Lead scoring basado en comportamiento con caballos</p>
        <p><span class="badge">POST</span> <code>/prods/predict</code> — Lead scoring basado en comportamiento con productos</p>
    </div>

    <h2>How it works</h2>
    <ol>
        <li><strong>Paso 1</strong> — Determina si el usuario es un lead potencial (Plata/Oro) o Bronce.</li>
        <li><strong>Paso 2</strong> — Clasifica entre Plata y Oro.</li>
    </ol>

    <h2>Request Format</h2>
    <div class="code-block">
        <pre>{request_example}</pre>
    </div>

    <h2>Expected Response</h2>
    <div class="code-block">
        <pre>{response_example}</pre>
    </div>

    <h2>Python Example</h2>
    <div class="code-block">
        <pre>import requests

payload = {{"features": {python_example}}}

# Horse endpoint
API_URL = "https://your-api-url/horse/predict"

# Prods endpoint
API_URL = "https://your-api-url/prods/predict"

payload = {"features": payload}

response = requests.post(API_URL, json=payload)

print(f"Status code: {{response.status_code}}")
print("Prediction:", response.json())

print(response.json())</pre>
    </div>

    <a href="/docs" class="try-button">Try it in Interactive Docs →</a>

    <h2>Feature Descriptions</h2>
    {feature_table}
</body>
</html>
"""