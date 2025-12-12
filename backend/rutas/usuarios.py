from fastapi import APIRouter, HTTPException
from db.conexion import coleccion_usuarios
from modelos.usuario import Usuario
from bson import ObjectId

router = APIRouter()

@router.post("/usuarios/crear")
async def crear_usuario(usuario: Usuario):
    existing = await coleccion_usuarios.find_one({"correo": usuario.correo})
    if existing:
        return {"mensaje": "Usuario ya existente"}
    resultado = await coleccion_usuarios.insert_one(usuario.model_dump())
    return {"mensaje": "Usuario creado correctamente", "_id": str(resultado.inserted_id)}

@router.get("/usuarios/{correo}")
async def obtener_usuario(correo: str):
    usuario = await coleccion_usuarios.find_one({"correo": correo})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario["_id"] = str(usuario["_id"]) 
    return usuario
