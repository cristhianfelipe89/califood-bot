# models/ubicacion_model.py
"""
Modelo para almacenar la última ubicación conocida del usuario.
"""

from datetime import datetime

def nueva_ubicacion(usuario, lat, lon):
    """
    Devuelve un diccionario de ubicación para guardar o actualizar.
    """
    return {
        "usuario": usuario,
        "lat": lat,
        "lon": lon,
        "fecha": datetime.now(),
        "mapa_url": generar_url_mapa(lat, lon)  # ← Nueva línea
    }

def generar_url_mapa(lat, lon):
    """
    Genera enlace para abrir en Google Maps
    """
    return f"https://www.google.com/maps?q={lat},{lon}"