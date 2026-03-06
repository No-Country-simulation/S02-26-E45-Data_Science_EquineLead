import json

from .layout import page
from .samples import sample_input_horses, sample_response

FEATURE_DESCRIPTIONS = [
    ("horses_viewed", "Total de caballos vistos", ">= 0", "int64"),
    ("horses_added_to_cart", "Caballos agregados al carrito", ">= 0", "int64"),
    ("max_horse_price_viewed", "Precio máximo de caballos vistos", ">= 0", "float64"),
    ("viewed_premium_horses", "Caballos premium vistos", ">= 0", "int64"),
    ("viewed_sport_elite", "Caballos sport/elite vistos", ">= 0", "int64"),
    ("viewed_family_safe", "Caballos family/safe vistos", ">= 0", "int64"),
    ("avg_horse_age", "Edad promedio de caballos vistos", ">= 0", "float64"),
    ("viewed_pro_sellers", "Caballos de vendedores pro vistos", ">= 0", "int64"),
    (
        "avg_prestige_score_horses",
        "Prestigio promedio de caballos vistos",
        ">= 0",
        "float64",
    ),
    ("avg_height", "Altura promedio de caballos vistos", ">= 0", "float64"),
    ("avg_weight", "Peso promedio de caballos vistos", ">= 0", "float64"),
    ("has_registry_viewed", "Vio caballos con registro", "0 / 1", "int64"),
    ("has_shipping_viewed", "Vio caballos con envío", "0 / 1", "int64"),
    ("viewed_working_elite", "Caballos working/elite vistos", ">= 0", "int64"),
    ("avg_tech_score", "Score técnico promedio", ">= 0", "float64"),
    ("avg_temperament", "Temperamento promedio de caballos vistos", ">= 0", "float64"),
    ("avg_comment_length", "Longitud promedio de comentarios", ">= 0", "float64"),
    ("caballos_unicos_vistos", "Caballos únicos vistos", ">= 0", "int64"),
    ("ratio_recurrencia_horse", "Ratio de recurrencia en caballos", "0–1", "float64"),
    (
        "max_visitas_mismo_caballo",
        "Máximo de visitas al mismo caballo",
        ">= 0",
        "int64",
    ),
    ("rango_precio_horse", "Rango de precios de caballos vistos", ">= 0", "int64"),
    ("ratio_cart_horse", "Ratio carrito/vistas caballos", "0–1", "float64"),
    ("user_prestige_score", "Score de prestigio del usuario", ">= 0", "int64"),
    ("user_region", "Región del usuario", ">= 0", "int64"),
    ("user_card_issuer", "Emisor de tarjeta del usuario", ">= 0", "int64"),
    ("user_domain", "Dominio del usuario", ">= 0", "int64"),
    ("user_antiguedad_dias", "Antigüedad del usuario en días", ">= 0", "int64"),
]


def get_horse_html() -> str:
    rows = "\n".join(
        f"<tr><td>{n}</td><td>{d}</td><td>{r}</td><td>{t}</td></tr>"
        for n, d, r, t in FEATURE_DESCRIPTIONS
    )
    request_example = json.dumps({"features": sample_input_horses}, indent=4)
    response_example = json.dumps(sample_response, indent=4)
    python_example = json.dumps(sample_input_horses, indent=8)

    content = f"""
    <h2><span class="badge">POST</span> <code>/horse/predict</code></h2>
<p>Lead scoring basado en el comportamiento de navegación del usuario con caballos.</p>

    <h3>Request</h3>
    <div class="code-block"><pre>{request_example}</pre></div>

    <h3>Response</h3>
    <div class="code-block"><pre>{response_example}</pre></div>

    <h3>Python Example</h3>
    <div class="code-block"><pre>import requests

payload = {{"features": {python_example}}}
response = requests.post("https://your-api-url/horse/predict", json=payload)
print(response.json())</pre></div>

    <a href="/docs" class="try-button">Try it in Interactive Docs →</a>

    <h3>Features</h3>
    <table>
        <thead><tr><th>Feature</th><th>Descripción</th><th>Rango</th><th>Tipo</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """
    return page("Horse Predict", "🐴 Horse", content)
