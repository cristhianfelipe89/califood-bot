# models/restaurante_model.py (versión flexible)
"""
Modelo de Restaurante con ubicación y redes sociales.
"""
from bson import ObjectId

def restaurante_schema(data):
    ubicacion = data.get("ubicacion", {})
    # Acepta tanto "lon" como "lng"
    longitud = ubicacion.get("lng") or ubicacion.get("lon")
    
    return {
        "_id": str(data.get("_id", ObjectId())),
        "nombre": data.get("nombre"),
        "tipo": data.get("tipo"),
        "zona": data.get("zona"),
        "precio": data.get("precio"),
        "contacto": data.get("contacto"),
        "ubicacion": {
            "direccion": ubicacion.get("direccion"),
            "lat": ubicacion.get("lat"),
            "lng": longitud  # ← Acepta ambos
        },
        "redes": {
            "facebook": data.get("redes", {}).get("facebook"),
            "instagram": data.get("redes", {}).get("instagram"),
            "tiktok": data.get("redes", {}).get("tiktok")
        }
    }