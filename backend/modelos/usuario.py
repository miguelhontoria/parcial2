from pydantic import BaseModel
from typing import List, Optional

class Marcador(BaseModel):
    ciudad: str
    latitud: float
    longitud: float
    imagenURI: Optional[str] = None

class Usuario(BaseModel):
    correo: str
    token_oauth: str
    marcadores: List[Marcador] = []
