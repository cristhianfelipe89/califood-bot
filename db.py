"""
Conexión a MongoDB para Califood-Bot.
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    print(f"✅ Conectado exitosamente a MongoDB: {MONGO_DB_NAME}")
except Exception as e:
    print("❌ Error al conectar con MongoDB:", e)
    db = None

def get_db():
    if db is None:
        raise ConnectionError("La conexión a MongoDB no está disponible.")
    return db
