from .layout import page


def get_overview_html() -> str:
    content = """
    <p>API de lead scoring y recomendación de caballos para e-commerce ecuestre.</p>

    <h2>Endpoints</h2>
    <table>
        <thead><tr><th>Método</th><th>Endpoint</th><th>Descripción</th></tr></thead>
        <tbody>
            <tr><td><span class="badge">POST</span></td><td><code>/horse/predict</code>
            </td><td>Lead scoring por comportamiento con caballos</td></tr>
            <tr><td><span class="badge">POST</span></td><td><code>/prods/predict</code>
            </td><td>Lead scoring por comportamiento con productos</td></tr>
            <tr><td><span class="badge-green">POST</span></td><td>
            <code>/recommender/recommend</code>
            </td><td>Recomendación de caballos similares</td></tr>
        </tbody>
    </table>

    <h2>Lead Scoring — How it works</h2>
    <ol>
        <li><strong>Paso 1</strong> — Determina si el usuario es Bronce o lead potencial
        (Plata/Oro).</li>
        <li><strong>Paso 2</strong> — Si es potencial, clasifica entre Plata y Oro.</li>
    </ol>

    <a href="/docs" class="try-button">Try it in Interactive Docs →</a>
    """
    return page("Overview", "🏠 Overview", content)
