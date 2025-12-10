from fastapi import APIRouter, Request
from db.conexion import coleccion_usuarios, coleccion_visitas
from modelos.visita import Visita
from datetime import datetime, timezone

router = APIRouter()

@router.get("/usuarios/{correo}/visitar")
async def visitar_usuario(correo: str, request: Request):
    visitante = request.cookies.get("session_email")
    if not visitante:
        return {"error": "Debes iniciar sesión para visitar mapas"}

    visitante_data = await coleccion_usuarios.find_one({"correo": visitante})
    token_oauth = visitante_data.get("token_oauth") if visitante_data else None

    visita = Visita(
        correo_visitado=correo,
        correo_visitante=visitante,
        fecha_hora=datetime.now(timezone.utc),
        token_oauth=token_oauth or ""
    )
    await coleccion_visitas.insert_one(visita.model_dump())

    usuario = await coleccion_usuarios.find_one({"correo": correo})
    if usuario:
        marcadores = usuario.get("marcadores", [])
        return {
            "correo": correo,
            "marcadores": marcadores
        }
    return {"error": "Usuario no encontrado"}

@router.get("/usuarios/{correo}/visitas")
async def obtener_visitas(correo: str):
    visitas = await coleccion_visitas.find({"correo_visitado": correo}).sort("fecha_hora", -1).to_list(None)
    for v in visitas:
        if "_id" in v:
            v["_id"] = str(v["_id"])
    return {"visitas": visitas}
