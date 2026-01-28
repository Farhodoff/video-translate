from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Basic routes
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("frontend/static/favicon.png")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Vercel deployment test"}

# For Vercel
handler = app
