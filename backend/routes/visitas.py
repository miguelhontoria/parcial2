from fastapi import APIRouter
from db import db
from models import Visita

router = APIRouter()

@router.post("/visitas")
async def crear_visita(visita: Visita):
    resultado = await db.visitas.insert_one(visita.dict())
    visita_dict = visita.dict()
    visita_dict["_id"] = str(resultado.inserted_id)
    return {"estado": "ok", "visita": visita_dict}

@router.get("/visitas/{email_propietario}")
async def obtener_visitas(email_propietario: str):
    visitas = await db.visitas.find({"email_propietario": email_propietario}).sort("timestamp", -1).to_list(100)
    for v in visitas:
        v["_id"] = str(v["_id"])
    return {"visitas": visitas}
