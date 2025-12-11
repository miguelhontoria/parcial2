from fastapi import APIRouter, HTTPException
from db import db
from models import Usuario

router = APIRouter()

@router.post("/usuarios")
async def crear_usuario(usuario: Usuario):
    await db.usuarios.insert_one(usuario.dict())
    return {"estado": "ok", "usuario": usuario}

@router.get("/usuarios")
async def obtener_todos_usuarios():
    usuarios = await db.usuarios.find().to_list(100)
    for u in usuarios:
        u["_id"] = str(u["_id"]) 
    return {"usuarios": usuarios}

@router.get("/usuarios/{email}")
async def obtener_usuario(email: str):
    usuario = await db.usuarios.find_one({"email": email})
    if usuario:
        usuario["_id"] = str(usuario["_id"])
        return usuario
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.get("/usuarios/{email}/marcadores")
async def obtener_marcadores(email: str):
    usuario = await db.usuarios.find_one({"email": email})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for m in usuario["marcadores"]:
        if "_id" in m:
            m["_id"] = str(m["_id"])
    return {"marcadores": usuario["marcadores"]}
