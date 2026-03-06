import json

from .layout import page
from .samples import sample_input_recommender, sample_response_recommender

FEATURE_DESCRIPTIONS = [
    ("breed", "Raza del caballo", "e.g. 'andalusian', 'thoroughbred'", "str"),
    ("color", "Color del pelaje", "e.g. 'bay', 'black', 'chestnut'", "str"),
    ("price", "Precio de referencia en USD", ">= 0", "float"),
]


def get_recommender_html() -> str:
    rows = "\n".join(
        f"<tr><td>{n}</td><td>{d}</td><td>{r}</td><td>{t}</td></tr>"
        for n, d, r, t in FEATURE_DESCRIPTIONS
    )
    request_example = json.dumps(sample_input_recommender, indent=4)
    response_example = json.dumps(sample_response_recommender, indent=4)
    python_example = json.dumps(sample_input_recommender, indent=8)

    content = f"""
    <h2><span class="badge-green">POST</span> <code>/recommender/recommend</code></h2>
    <p>Devuelve los 5 caballos más similares usando KNN con similitud coseno sobre raza,
      color y precio.</p>
    <p>La distancia coseno va de <strong>0</strong> (idéntico) a <strong>1</strong>
    (completamente distinto).</p>

    <h3>Request</h3>
    <div class="code-block"><pre>{request_example}</pre></div>

    <h3>Response</h3>
    <div class="code-block"><pre>{response_example}</pre></div>

    <h3>Python Example</h3>
    <div class="code-block"><pre>import requests

payload = {python_example}
response = requests.post("https://your-api-url/recommender/recommend", json=payload)
print(response.json())</pre></div>

    <a href="/docs" class="try-button">Try it in Interactive Docs →</a>

    <h3>Features</h3>
    <table>
        <thead><tr><th>Feature</th><th>Descripción</th><th>Rango</th><th>Tipo</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """
    return page("Recommender", "🔍 Recommender", content)
