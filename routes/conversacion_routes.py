from flask import Blueprint, jsonify
from services.conversacion_service import listar_conversaciones

conversacion_bp = Blueprint("conversaciones", __name__)

@conversacion_bp.route("/api/conversaciones", methods=["GET"])
def obtener_conversaciones():
    """
    Devuelve todas las conversaciones almacenadas.
    """
    conversaciones = listar_conversaciones()
    for c in conversaciones:
        c["_id"] = str(c["_id"])
    return jsonify(conversaciones)