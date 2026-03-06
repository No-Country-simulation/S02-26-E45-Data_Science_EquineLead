import json
from .layout import page
from .samples import sample_input_prods, sample_response

FEATURE_DESCRIPTIONS = [
    ("products_viewed", "Total de productos vistos", ">= 0", "int64"),
    ("products_added_to_cart", "Productos agregados al carrito", ">= 0", "int64"),
    (
        "avg_product_price_viewed",
        "Precio promedio de productos vistos",
        ">= 0",
        "float64",
    ),
    (
        "max_product_price_viewed",
        "Precio máximo de productos vistos",
        ">= 0",
        "float64",
    ),
    ("unique_categories", "Categorías únicas de productos vistos", ">= 0", "int64"),
    ("viewed_waterproof", "Productos waterproof vistos", ">= 0", "int64"),
    ("viewed_leather", "Productos de cuero vistos", ">= 0", "int64"),
    ("viewed_breathable", "Productos transpirables vistos", ">= 0", "int64"),
    ("viewed_uv_protection", "Productos con protección UV vistos", ">= 0", "int64"),
    ("viewed_machine_washable", "Productos lavables a máquina vistos", ">= 0", "int64"),
    (
        "avg_prestige_score_products",
        "Prestigio promedio de productos vistos",
        ">= 0",
        "float64",
    ),
    ("productos_unicos_vistos", "Productos únicos vistos", ">= 0", "int64"),
    ("ratio_recurrencia_prods", "Ratio de recurrencia en productos", "0–1", "float64"),
    ("most_viewed_brand", "Marca de producto más vista", ">= 0", "int64"),
    ("most_viewed_category", "Categoría de producto más vista", ">= 0", "int64"),
    (
        "most_viewed_target_user",
        "Perfil de usuario objetivo más visto",
        ">= 0",
        "int64",
    ),
    ("ratio_cart_prods", "Ratio carrito/vistas productos", "0–1", "float64"),
    ("user_prestige_score", "Score de prestigio del usuario", ">= 0", "int64"),
    ("user_region", "Región del usuario", ">= 0", "int64"),
    ("user_card_issuer", "Emisor de tarjeta del usuario", ">= 0", "int64"),
    ("user_domain", "Dominio del usuario", ">= 0", "int64"),
    ("user_antiguedad_dias", "Antigüedad del usuario en días", ">= 0", "int64"),
]


def get_prods_html() -> str:
    rows = "\n".join(
        f"<tr><td>{n}</td><td>{d}</td><td>{r}</td><td>{t}</td></tr>"
        for n, d, r, t in FEATURE_DESCRIPTIONS
    )
    request_example = json.dumps({"features": sample_input_prods}, indent=4)
    response_example = json.dumps(sample_response, indent=4)
    python_example = json.dumps(sample_input_prods, indent=8)

    content = f"""
    <h2><span class="badge">POST</span> <code>/prods/predict</code></h2>
    <p>Lead scoring basado en el comportamiento de navegación del usuario con productos.</p>

    <h3>Request</h3>
    <div class="code-block"><pre>{request_example}</pre></div>

    <h3>Response</h3>
    <div class="code-block"><pre>{response_example}</pre></div>

    <h3>Python Example</h3>
    <div class="code-block"><pre>import requests

payload = {{"features": {python_example}}}
response = requests.post("https://your-api-url/prods/predict", json=payload)
print(response.json())</pre></div>

    <a href="/docs" class="try-button">Try it in Interactive Docs →</a>

    <h3>Features</h3>
    <table>
        <thead><tr><th>Feature</th><th>Descripción</th><th>Rango</th><th>Tipo</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """
    return page("Prods Predict", "🛒 Prods", content)
