from pydantic import BaseModel
from typing import List
from datetime import datetime

class Reseña(BaseModel):
    establecimiento: str
    direccion: str
    latitud: float
    longitud: float
    valoracion: int
    correo_autor: str
    nombre_autor: str
    token_oauth: str
    token_emision: datetime
    token_caducidad: datetime
    imagenes: List[str] = []