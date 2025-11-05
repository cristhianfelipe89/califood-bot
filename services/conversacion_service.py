"""
Servicio para guardar y consultar conversaciones.
"""
from db import get_db
from models.conversacion_model import nueva_conversacion

def guardar_conversacion(usuario, mensaje, respuesta):
    db = get_db()
    conv = nueva_conversacion(usuario, mensaje, respuesta)
    db.conversaciones.insert_one(conv)

def listar_conversaciones(usuario=None):
    db = get_db()
    filtro = {"usuario": usuario} if usuario else {}
    return list(db.conversaciones.find(filtro).sort("fecha", -1))
