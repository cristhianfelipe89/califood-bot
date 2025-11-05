"""
Servicio para manejar operaciones CRUD de restaurantes.
"""
from db import get_db
from bson import ObjectId
from models.restaurante_model import restaurante_schema

db = get_db()

def crear_restaurante(data):
    result = db["restaurantes"].insert_one(data)
    data["_id"] = str(result.inserted_id)
    return restaurante_schema(data)

def listar_restaurantes():
    restaurantes = list(db["restaurantes"].find())
    return [restaurante_schema(r) for r in restaurantes]

def obtener_restaurante_por_id(restaurante_id):
    restaurante = db["restaurantes"].find_one({"_id": ObjectId(restaurante_id)})
    return restaurante_schema(restaurante) if restaurante else None

def buscar_restaurante_por_nombre(nombre):
    restaurante = db["restaurantes"].find_one({"nombre": {"$regex": nombre, "$options": "i"}})
    return restaurante_schema(restaurante) if restaurante else None
