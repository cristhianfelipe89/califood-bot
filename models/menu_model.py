"""
Modelo de Menú asociado a un restaurante.
"""
from bson import ObjectId

def menu_schema(data):
    return {
        "_id": str(data.get("_id", ObjectId())),
        "restaurante_id": str(data.get("restaurante_id")),
        "productos": data.get("productos", []),  # [{nombre, precio}]
    }
