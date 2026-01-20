from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.routers import api
import os

app = FastAPI()

# Mounts
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Include Router
app.include_router(api.router)

# Pages
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Make sure upload dir exists
    os.makedirs("uploads", exist_ok=True)
    print("Server ishga tushmoqda: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
