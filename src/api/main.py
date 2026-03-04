from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .routers import horse, prods
from api_docs import get_docs_html

app = FastAPI(title="EquineLead API")

app.include_router(horse.router)
app.include_router(prods.router)

@app.get("/", response_class=HTMLResponse)
def api_root():
    return get_docs_html()