from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone

class Marcador(BaseModel):
    ciudad: str
    latitud: float
    longitud: float
    url_imagen: Optional[str] = None

class Usuario(BaseModel):
    correo: EmailStr
    token: str
    marcadores: List[Marcador] = []

class Visita(BaseModel):
    email_propietario: EmailStr
    email_visitante: EmailStr
    token: str
    timestamp: datetime = datetime.now(timezone.utc)
