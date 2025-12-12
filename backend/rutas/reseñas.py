from fastapi import APIRouter, Request, HTTPException, Depends, Form, UploadFile, File
from db.conexion import coleccion_reseñas, coleccion_usuarios
from bson import ObjectId
import httpx
import os
import cloudinary.uploader
router = APIRouter()

def require_auth(request: Request):
    correo = request.cookies.get("session_email")
    if not correo:
        raise HTTPException(status_code=401, detail="No autenticado")
    return correo

@router.get("/reseñas")
async def obtener_reseñas(email: str = Depends(require_auth)):
    reseñas = await coleccion_reseñas.find().to_list(None)
    resultado = []
    for r in reseñas:
        r["_id"] = str(r["_id"])  
        resultado.append({
            "_id": r["_id"],
            "establecimiento": r.get("establecimiento"),
            "direccion": r.get("direccion"),
            "latitud": r.get("latitud"),
            "longitud": r.get("longitud"),
            "valoracion": r.get("valoracion"),
        })
    return {"reseñas": resultado}

@router.get("/reseñas/{direccion}")
async def obtener_reseña_por_direccion(direccion: str, email: str = Depends(require_auth)):
    reseña = await coleccion_reseñas.find_one({"direccion": direccion})
    if not reseña:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    reseña["_id"] = str(reseña["_id"])  
    return reseña

@router.post("/reseñas")
async def crear_reseña(
    establecimiento: str = Form(...),
    direccion: str = Form(...),
    valoracion: int = Form(...),
    imagen: UploadFile = File(None),
    email: str = Depends(require_auth)
):
    usuario = await coleccion_usuarios.find_one({"correo": email})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    async with httpx.AsyncClient() as client:
        geo_res = await client.get(
            f"https://nominatim.openstreetmap.org/search?format=json&q={direccion}",
            headers={"User-Agent": "ReViews/1.0"}
        )
        geo_data = geo_res.json()
        if not geo_data:
            raise HTTPException(status_code=400, detail="No se pudo geolocalizar la dirección")
        latitud = float(geo_data[0]["lat"])
        longitud = float(geo_data[0]["lon"])

    imagenes = []
    if imagen and imagen.filename:
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
        try:
            resultado = cloudinary.uploader.upload(imagen.file)
            imagenes.append(resultado["secure_url"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")

    reseña = {
        "establecimiento": establecimiento,
        "direccion": direccion,
        "latitud": latitud,
        "longitud": longitud,
        "valoracion": valoracion,
        "correo_autor": usuario["correo"],
        "nombre_autor": usuario.get("nombre"),
        "token_oauth": usuario.get("token_oauth"),
        "token_emision": usuario.get("token_emision"),
        "token_caducidad": usuario.get("token_caducidad"),
        "imagenes": imagenes
    }

    resultado = await coleccion_reseñas.insert_one(reseña)
    reseña["_id"] = str(resultado.inserted_id)

    return {"mensaje": "Reseña creada correctamente", "reseña": reseña}