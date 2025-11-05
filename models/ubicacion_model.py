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
        "fecha": datetime.now()
    }
