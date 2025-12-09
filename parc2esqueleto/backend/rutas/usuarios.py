from fastapi import APIRouter
from modelos.usuario import Usuario, Marcador
from db.conexion import coleccion_usuarios
from bson import ObjectId

router = APIRouter()

@router.post("/usuarios/crear")
async def crear_usuario(usuario: Usuario):
    await coleccion_usuarios.update_one(
        {"correo": usuario.correo},
        {"$setOnInsert": usuario.model_dump()},
        upsert=True
    )
    return {"mensaje": "Usuario creado o ya existente"}

@router.get("/usuarios/{correo}")
async def obtener_usuario(correo: str):
    try:
        usuario = await coleccion_usuarios.find_one({"correo": correo})
        if usuario:
            usuario["_id"] = str(usuario["_id"])  
            return usuario
        return {"mensaje": "Usuario no encontrado"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/usuarios/{correo}/marcadores")
async def añadir_marcador(correo: str, marcador: Marcador):
    await coleccion_usuarios.update_one(
        {"correo": correo},
        {"$push": {"marcadores": marcador.model_dump()}}
    )
    return {"mensaje": "Marcador añadido correctamente", "marcador": marcador.model_dump()}