from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.routers import api
import os
from dotenv import load_dotenv

load_dotenv()


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

# ... existing code ...

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("frontend/static/favicon.png")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Make sure upload dir exists
    os.makedirs("uploads", exist_ok=True)
    # Allow overriding host and port via environment variables (useful for local dev)
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "9000"))
    print(f"Server ishga tushmoqda: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
