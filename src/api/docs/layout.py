STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=
Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:       #0a0b0f;
    --surface:  #12141a;
    --border:   #1e2130;
    --accent1:  #e8c547;
    --accent2:  #4fc3f7;
    --accent3:  #81c784;
    --muted:    #4a5068;
    --text:     #dde1f0;
    --text-dim: #7a82a0;
    --horse:    #c084fc;
    --prods:    #4fc3f7;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.015) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .page-wrap {
    position: relative; z-index: 1;
    max-width: 900px; margin: 0 auto;
    padding: 32px 24px 80px;
  }

  /* ── HEADER ── */
  .site-header {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 28px;
  }
  .site-logo {
    width: 36px; height: 36px; flex-shrink: 0;
    background: var(--accent1);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    animation: pulse 3s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.65} }
  .site-title {
    font-size: 18px; font-weight: 800; color: var(--text);
  }
  .site-title span { color: var(--accent1); }

  /* ── NAV ── */
  nav {
    display: flex; flex-wrap: wrap; gap: 4px;
    padding: 10px 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 36px;
  }
  nav a {
    font-size: 11px; font-family: 'Space Mono', monospace;
    font-weight: 700; letter-spacing: .06em;
    color: var(--text-dim); text-decoration: none;
    padding: 5px 12px; border-radius: 5px;
    transition: background .2s, color .2s;
  }
  nav a:hover { background: color-mix(in srgb, var(--accent1) 10%, transparent);
  color: var(--text); }
  nav a.active {
    background: color-mix(in srgb, var(--accent1) 15%, transparent);
    color: var(--accent1);
    border: 1px solid color-mix(in srgb, var(--accent1) 35%, transparent);
  }

  /* ── TYPOGRAPHY ── */
  h1 { font-size: 24px; font-weight: 800; color: var(--text); margin-bottom: 8px; }
  h2 {
    font-size: 15px; font-weight: 700; color: var(--accent2);
    font-family: 'Space Mono', monospace; letter-spacing: .08em;
    text-transform: uppercase; margin: 28px 0 14px;
    display: flex; align-items: center; gap: 10px;
  }
  h2::after { content:''; flex:1; height:1px; background:var(--border); }
  h3 { font-size: 13px; color: var(--text-dim); font-family: 'Space Mono', monospace;
  margin: 20px 0 10px; }
  p  { font-size: 13px; color: var(--text-dim); font-family: 'Space Mono', monospace;
  line-height: 1.7; margin-bottom: 12px; }

  /* ── CODE BLOCK ── */
  .code-block {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px; overflow-x: auto; margin-bottom: 16px;
  }
  .code-block pre {
    font-family: 'Space Mono', monospace; font-size: 11px;
    color: var(--accent3); line-height: 1.65; margin: 0;
  }

  /* ── TABLE ── */
  table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
  th {
    background: var(--surface); border: 1px solid var(--border);
    padding: 10px 12px; text-align: left;
    font-size: 10px; font-family: 'Space Mono', monospace;
    letter-spacing: .1em; text-transform: uppercase; color: var(--text-dim);
  }
  td {
    padding: 9px 12px; border: 1px solid var(--border);
    font-size: 12px; font-family: 'Space Mono', monospace; color: var(--text);
  }
  tr:hover td { background: color-mix(in srgb, var(--accent1) 4%, transparent); }
  code {
    background: color-mix(in srgb, var(--accent2) 12%, transparent);
    color: var(--accent2); padding: 2px 6px; border-radius: 3px;
    font-family: 'Space Mono', monospace; font-size: 11px;
  }

  /* ── BADGES ── */
  .badge {
    display: inline-block; padding: 3px 9px; border-radius: 4px;
    font-size: 10px; font-family: 'Space Mono', monospace; font-weight: 700;
    background: color-mix(in srgb, var(--accent2) 18%, transparent);
    color: var(--accent2);
    border: 1px solid color-mix(in srgb, var(--accent2) 35%, transparent);
  }
  .badge-green {
    display: inline-block; padding: 3px 9px; border-radius: 4px;
    font-size: 10px; font-family: 'Space Mono', monospace; font-weight: 700;
    background: color-mix(in srgb, var(--accent3) 18%, transparent);
    color: var(--accent3);
    border: 1px solid color-mix(in srgb, var(--accent3) 35%, transparent);
  }

  /* ── TRY BUTTON ── */
  .try-button {
    display: inline-flex; align-items: center; gap: 8px;
    background: color-mix(in srgb, var(--accent1) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--accent1) 40%, transparent);
    color: var(--accent1); padding: 10px 20px; border-radius: 6px;
    text-decoration: none; font-size: 12px;
    font-family: 'Space Mono', monospace; font-weight: 700; letter-spacing: .06em;
    margin: 14px 0; transition: background .2s, box-shadow .2s;
  }
  .try-button:hover {
    background: color-mix(in srgb, var(--accent1) 20%, transparent);
    box-shadow: 0 4px 20px color-mix(in srgb, var(--accent1) 20%, transparent);
  }

  /* ── LISTS ── */
  ol { padding-left: 20px; }
  ol li {
    font-size: 12px; font-family: 'Space Mono', monospace;
    color: var(--text-dim); margin-bottom: 8px; line-height: 1.6;
  }
  ol li strong { color: var(--text); }
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
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — EquineLead API</title>
  {STYLE}
</head>
<body>
  <div class="page-wrap">
    <div class="site-header">
      <div class="site-logo"></div>
      <div class="site-title">🐴 Equine<span>Lead</span> API</div>
    </div>
    {nav}
    {content}
  </div>
</body>
</html>"""
