# utils/map_utils.py
"""
Utilidades para generar enlaces a mapas
"""

def generar_url_google_maps(lat, lon):
    """Genera URL para Google Maps"""
    return f"https://www.google.com/maps?q={lat},{lon}"

def generar_url_google_maps_directions(from_lat, from_lon, to_lat, to_lon):
    """Genera URL para direcciones en Google Maps"""
    return f"https://www.google.com/maps/dir/{from_lat},{from_lon}/{to_lat},{to_lon}"

def generar_url_waze(lat, lon):
    """Genera URL para Waze"""
    return f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"

def generar_enlaces_ubicacion(lat, lon, direccion=None):
    """Genera múltiples opciones de enlaces de mapas"""
    return {
        "google_maps": generar_url_google_maps(lat, lon),
        "waze": generar_url_waze(lat, lon),
        "direccion": direccion or f"{lat}, {lon}"
    }