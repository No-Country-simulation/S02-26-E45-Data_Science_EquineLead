STYLE = """
<style>
    body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }
    h1 { color: #2a6496; border-bottom: 1px solid #eee; }
    h2 { color: #3a7abf; }
    h3 { color: #555; }
    nav { background: #f0f4f8; padding: 12px 20px; border-radius: 5px; margin-bottom: 30px; }
    nav a { margin-right: 20px; color: #2a6496; text-decoration: none; font-weight: bold; }
    nav a:hover { text-decoration: underline; }
    nav a.active { color: #e67e22; border-bottom: 2px solid #e67e22; }
    .code-block { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
    .try-button {
        display: inline-block; background: #4CAF50; color: white;
        padding: 10px 15px; text-decoration: none; border-radius: 5px; margin: 10px 0;
    }
    .badge { display: inline-block; background: #2a6496; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }
    .badge-green { display: inline-block; background: #3a9a3a; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #f2f2f2; padding: 12px; text-align: left; }
    td { padding: 8px; border: 1px solid #ddd; }
</style>
"""

NAV = """
<nav>
    <a href="/docs/overview">🏠 Overview</a>
    <a href="/docs/horse">🐴 Horse</a>
    <a href="/docs/prods">🛒 Prods</a>
    <a href="/docs/recommender">🔍 Recommender</a>
    <a href="/docs">⚡ Interactive Docs</a>
</nav>
"""


def page(title: str, active: str, content: str) -> str:
    nav = NAV.replace(f">{active}<", f' class="active">{active}<')
    return f"""
<html>
<head><title>{title} — EquineLead API</title>{STYLE}</head>
<body>
    <h1>🐴 EquineLead API</h1>
    {nav}
    {content}
</body>
</html>
"""
