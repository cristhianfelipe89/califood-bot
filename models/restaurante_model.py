"""
Modelo de Restaurante con ubicación y redes sociales.
"""
from bson import ObjectId

def restaurante_schema(data):
    return {
        "_id": str(data.get("_id", ObjectId())),
        "nombre": data.get("nombre"),
        "tipo": data.get("tipo"),
        "zona": data.get("zona"),
        "precio": data.get("precio"),
        "contacto": data.get("contacto"),
        "ubicacion": {
            "direccion": data.get("ubicacion", {}).get("direccion"),
            "lat": data.get("ubicacion", {}).get("lat"),
            "lng": data.get("ubicacion", {}).get("lng")
        },
        "redes": {
            "facebook": data.get("redes", {}).get("facebook"),
            "instagram": data.get("redes", {}).get("instagram"),
            "tiktok": data.get("redes", {}).get("tiktok")
        }
    }

