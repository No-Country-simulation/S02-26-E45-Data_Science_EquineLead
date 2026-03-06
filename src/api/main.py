from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .routers import horse, prods, engine
from .docs import (
    get_overview_html,
    get_horse_html,
    get_prods_html,
    get_recommender_html,
)

app = FastAPI(title="EquineLead API")

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
