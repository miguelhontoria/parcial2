import httpx
from modelos.usuario import Marcador
from db.conexion import coleccion_usuarios
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from dotenv import load_dotenv
import os
import cloudinary

router = APIRouter()

async def obtener_coordenadas(ciudad: str):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={ciudad}"
    async with httpx.AsyncClient() as client:
        respuesta = await client.get(url)
        datos = respuesta.json()
        if datos:
            return float(datos[0]["lat"]), float(datos[0]["lon"])
        return None, None
    
def require_auth(request: Request):
    email = request.cookies.get("session_email")
    if not email:
        raise HTTPException(status_code=401, detail="No autenticado")
    return email

@router.post("/usuarios/{correo}/marcadores")
async def añadir_marcador(correo: str, ciudad: str, imagen: UploadFile = File(None), email: str = Depends(require_auth)):
    if correo != email:
        raise HTTPException(status_code=403, detail="No autorizado")
    lat, lon = await obtener_coordenadas(ciudad)
    if not lat or not lon:
        return {"mensaje": "No se encontraron coordenadas para la ciudad"}

    imagenURI = None
    if imagen and imagen.filename:
        if not imagen.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return {"mensaje": "Formato de imagen no permitido. Usa JPG o PNG."}
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
        try:
            resultado = cloudinary.uploader.upload(imagen.file)
            imagenURI = resultado["secure_url"]
        except Exception as e:
            return {"mensaje": f"Error al subir la imagen: {str(e)}"}

    marcador = {
        "ciudad": ciudad,
        "latitud": lat,
        "longitud": lon,
        "imagenURI": imagenURI
    }

    resultado = await coleccion_usuarios.update_one(
        {"correo": correo},
        {"$push": {"marcadores": marcador}}
    )

    if resultado.modified_count == 0:
        return {"mensaje": "No se encontró el usuario o no se pudo actualizar"}

    return {"mensaje": "Marcador añadido correctamente", "marcador": marcador}

