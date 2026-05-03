from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes.call      import router as call_router
from app.routes.token     import router as token_router
from app.routes.make_call import router as make_call_router
import os

app = FastAPI(title="Auris", version="2.0.0")

app.include_router(call_router)
app.include_router(token_router)
app.include_router(make_call_router)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve Browser Client HTML"""
    html_path = os.path.join(os.path.dirname(__file__), "app", "templates", "browser.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health():
    return {"status": "Auris running 🚀"}