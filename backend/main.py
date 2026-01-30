from fastapi import FastAPI, Request, Depends
from backend import database
from backend.models import models
from backend.services import auth
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.routers import api
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

# Create Tables
models.Base.metadata.create_all(bind=database.engine)

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
async def dashboard(
    request: Request,
    user: models.User = Depends(auth.get_current_user_or_redirect),
    db: database.SessionLocal = Depends(database.get_db)
):
    projects = db.query(models.Project).filter(models.Project.user_id == user.id).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "projects": projects
    })

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Make sure upload dir exists
    os.makedirs("uploads", exist_ok=True)
    print("Server ishga tushmoqda: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
