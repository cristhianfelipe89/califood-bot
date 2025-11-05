from db import get_db
from bson import ObjectId
from models.menu_model import menu_schema

db = get_db()

def crear_menu(data):
    result = db["menus"].insert_one(data)
    data["_id"] = str(result.inserted_id)
    return menu_schema(data)

def listar_menus():
    menus = list(db["menus"].find())
    return [menu_schema(m) for m in menus]

def obtener_menu_por_restaurante(restaurante_id):
    menus = list(db["menus"].find({"restaurante_id": restaurante_id}))
    return [menu_schema(m) for m in menus]
