# models/restaurante_model.py (VERSIÓN FINAL)
"""
Modelo de Restaurante con ubicación, redes sociales y etiquetas específicas.
"""
from bson import ObjectId

def restaurante_schema(data):
    ubicacion = data.get("ubicacion", {})
    # Acepta tanto "lon" como "lng"
    longitud = ubicacion.get("lng") or ubicacion.get("lon")
    
    # Generar URL de mapa si no existe
    mapa_url = ubicacion.get("mapa_url")
    if not mapa_url and ubicacion.get('lat') and longitud:
        mapa_url = f"https://www.google.com/maps?q={ubicacion.get('lat')},{longitud}"
    
     # OBTENER REDES SOCIALES CORRECTAMENTE
    redes_data = data.get("redes", {})
    
    return {
        "_id": str(data.get("_id", ObjectId())),
        "nombre": data.get("nombre"),
        "tipo": data.get("tipo"),
        "subtipo": data.get("subtipo", []),  # Etiquetas específicas
        "zona": data.get("zona"),
        "precio": data.get("precio"),
        "contacto": data.get("contacto"),
        "ubicacion": {
            "direccion": ubicacion.get("direccion"),
            "lat": ubicacion.get("lat"),
            "lng": longitud,
            "mapa_url": mapa_url
        },
        "redes": {
            "facebook": redes_data.get("facebook"),
            "instagram": redes_data.get("instagram"), 
            "tiktok": redes_data.get("tiktok")
        }
    }