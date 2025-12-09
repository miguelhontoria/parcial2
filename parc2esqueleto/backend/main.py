import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import rutas.usuarios
import rutas.visitas
import rutas.marcadores
from auth import router as auth_router
from fastapi import Request

app = FastAPI(title=os.getenv("APP_NAME", "MiMapa"))

app.include_router(usuarios.router)
app.include_router(visitas.router)
app.include_router(marcadores.router)
app.include_router(auth_router)

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

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
def home():
    return FileResponse(os.path.join(frontend_path, "index.html"))

app.include_router(usuarios.router)
app.include_router(visitas.router)
app.include_router(marcadores.router)
app.include_router(auth_router)

@app.get("/auth/sesion")
def obtener_sesion(request: Request):
    correo = request.cookies.get("session_email")
    if correo:
        return {"correo": correo}
    return {"correo": None}
