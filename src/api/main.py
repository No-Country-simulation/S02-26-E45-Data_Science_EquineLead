from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .docs import (
    get_horse_html,
    get_overview_html,
    get_prods_html,
    get_recommender_html,
)
from .routers import engine, horse, prods

app = FastAPI(
    title="EquineLead API",
    description="""API de lead scoring y recomendación
    de caballos para e-commerce ecuestre.""",
    version="1.0.0",
    docs_url="/docs",  # podés cambiar la ruta si querés
)

app.add_route("/docs/overview", lambda r: HTMLResponse(get_overview_html()))
app.add_route("/docs/horse", lambda r: HTMLResponse(get_horse_html()))
app.add_route("/docs/prods", lambda r: HTMLResponse(get_prods_html()))
app.add_route("/docs/recommender", lambda r: HTMLResponse(get_recommender_html()))

app.include_router(horse.router)
app.include_router(prods.router)
app.include_router(engine.router)


@app.get("/", response_class=HTMLResponse)
def api_root():
    return get_overview_html()
