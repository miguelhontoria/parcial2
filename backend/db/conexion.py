from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
cliente = AsyncIOMotorClient(MONGO_URI)
bd = cliente.get_default_database()  
 
coleccion_usuarios = bd["usuarios"]
coleccion_reseñas = bd["reseñas"]