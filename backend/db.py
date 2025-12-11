from dotenv import load_dotenv
import os
import motor.motor_asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client.parc2

coleccion_usuarios = db.usuarios
coleccion_visitas = db.visitas