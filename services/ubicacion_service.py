# services/ubicacion_service.py
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
    ubicacion = db.ubicaciones.find_one({"usuario": usuario})
    if ubicacion:
        # Asegurar que siempre tenga el campo mapa_url
        if "mapa_url" not in ubicacion and "lat" in ubicacion and "lon" in ubicacion:
            ubicacion["mapa_url"] = f"https://www.google.com/maps?q={ubicacion['lat']},{ubicacion['lon']}"
    return ubicacion