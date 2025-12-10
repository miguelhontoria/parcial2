from pydantic import BaseModel
from datetime import datetime

class Visita(BaseModel):
    correo_visitado: str
    correo_visitante: str
    fecha_hora: datetime
    token_oauth: str
