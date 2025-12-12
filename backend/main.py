import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from rutas import usuarios, reseñas
from auth import router as auth_router

app = FastAPI(title=os.getenv("APP_NAME", "ReViews"))

app.include_router(usuarios.router)
app.include_router(reseñas.router)
app.include_router(auth_router)

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "https://parcial2-82eb.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
def home():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/auth/sesion")
def obtener_sesion(request: Request):
    correo = request.cookies.get("session_email")
    return {"correo": correo if correo else None}
