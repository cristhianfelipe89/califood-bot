from db import get_db
from bson import ObjectId
from datetime import datetime
from models.pedido_model import pedido_schema

db = get_db()

def crear_pedido(data):
    productos = data["productos"]
    total = sum(item["cantidad"] * item["precio_unitario"] for item in productos)

    pedido = {
        "restaurante_id": ObjectId(data["restaurante_id"]),
        "menu_id": ObjectId(data["menu_id"]),
        "productos": productos,
        "total": total,
        "fecha": datetime.now()
    }

    result = db["pedidos"].insert_one(pedido)
    pedido["_id"] = str(result.inserted_id)
    return pedido_schema(pedido)

def listar_pedidos():
    pedidos = list(db["pedidos"].find())
    return [pedido_schema(p) for p in pedidos]
