"""
Servicio para manejar la ubicación de los usuarios.
"""
from db import get_db
from models.ubicacion_model import nueva_ubicacion

def guardar_ubicacion(usuario, lat, lon):
    db = get_db()
    doc = nueva_ubicacion(usuario, lat, lon)
    db.ubicaciones.update_one(
        {"usuario": usuario},
        {"$set": doc},
        upsert=True
    )

def obtener_ubicacion(usuario):
    db = get_db()
    return db.ubicaciones.find_one({"usuario": usuario})
