from pydantic import BaseModel
from typing import List
from datetime import datetime
from modelos.reseña import Reseña

class Usuario(BaseModel):
    correo: str
    nombre: str
    token_oauth: str
    token_emision: datetime
    token_caducidad: datetime
    reseñas: List[Reseña] = []