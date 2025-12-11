from fastapi import APIRouter, UploadFile, Form, HTTPException
from db import coleccion_usuarios  # usa la misma colección que auth.py
import aiohttp
import cloudinary
import cloudinary.uploader
import os

router = APIRouter()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

@router.get("/usuarios/{email}/marcadores")
async def obtener_marcadores(email: str):
    usuario = await coleccion_usuarios.find_one({"correo": email})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"marcadores": usuario.get("marcadores", [])}

@router.post("/usuarios/{email}/marcadores")
async def crear_marcador(
    email: str,
    ciudad: str = Form(...),
    imagen: UploadFile | None = None,
):
    # Geocoding con Nominatim
    async with aiohttp.ClientSession(headers={"User-Agent": "MiMapa/1.0"}) as session:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={ciudad}"
        async with session.get(url) as resp:
            data = await resp.json()
            if not data:
                raise HTTPException(status_code=404, detail="Ciudad no encontrada")
            latitud = float(data[0]["lat"])
            longitud = float(data[0]["lon"])

    # Subida a Cloudinary
    url_imagen = None
    if imagen:
        result = cloudinary.uploader.upload(imagen.file, folder="mimapa")
        url_imagen = result["secure_url"]

    marcador = {
        "ciudad": ciudad,
        "latitud": latitud,
        "longitud": longitud,
        "url_imagen": url_imagen,
    }

    # Guardar en MongoDB por “correo”
    resultado = await coleccion_usuarios.update_one(
        {"correo": email},
        {"$push": {"marcadores": marcador}},
    )

    if resultado.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"estado": "ok", "marcador": marcador}
