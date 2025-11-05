"""
Modelo de Pedido.
"""
from bson import ObjectId
from datetime import datetime

def pedido_schema(data):
    return {
        "_id": str(data.get("_id", ObjectId())),
        "restaurante_id": str(data.get("restaurante_id")),
        "menu_id": str(data.get("menu_id")),
        "productos": data.get("productos", []),  # [{nombre, cantidad, precio_unitario}]
        "total": data.get("total", 0.0),
        "fecha": data.get("fecha", datetime.now().isoformat())
    }
