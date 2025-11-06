"""
Servicio para manejar operaciones CRUD de restaurantes.
"""
from db import get_db
from bson import ObjectId
from models.restaurante_model import restaurante_schema

db = get_db()

def crear_restaurante(data):
    # Asegurar estructura correcta de ubicación
    if "ubicacion" not in data:
        data["ubicacion"] = {}
    if "redes" not in data:
        data["redes"] = {}
    
    result = db["restaurantes"].insert_one(data)
    data["_id"] = str(result.inserted_id)
    return restaurante_schema(data)

def listar_restaurantes():
    restaurantes = list(db["restaurantes"].find())
    return [restaurante_schema(r) for r in restaurantes]

def obtener_restaurante_por_id(restaurante_id):
    try:
        restaurante = db["restaurantes"].find_one({"_id": ObjectId(restaurante_id)})
        return restaurante_schema(restaurante) if restaurante else None
    except:
        return None

def buscar_restaurante_por_nombre(nombre):
    restaurante = db["restaurantes"].find_one({"nombre": {"$regex": nombre, "$options": "i"}})
    return restaurante_schema(restaurante) if restaurante else None