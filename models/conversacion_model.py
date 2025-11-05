"""
Modelo para registrar conversaciones del usuario con el bot.
"""

from datetime import datetime

def nueva_conversacion(usuario, mensaje, respuesta):
    """
    Devuelve un diccionario listo para insertar en MongoDB.
    """
    return {
        "usuario": usuario,
        "mensaje": mensaje,
        "respuesta": respuesta,
        "fecha": datetime.now()
    }
