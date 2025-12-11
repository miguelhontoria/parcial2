import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes import usuarios, visitas, marcadores
from auth import router as auth_router

app = FastAPI(title=os.getenv("APP_NAME", "MiMapa"))

# Routers (una sola vez)
app.include_router(usuarios.router)
app.include_router(visitas.router)
app.include_router(marcadores.router)
app.include_router(auth_router)

# CORS
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
def home():
    return FileResponse(os.path.join(frontend_path, "index.html"))