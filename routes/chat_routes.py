# routes/chat_routes.py
"""
Rutas del chat conversacional.
"""

from flask import Blueprint, request, jsonify
from services.ia_service import generar_respuesta_ia

chat_bp = Blueprint("chat_bp", __name__)


@chat_bp.route("/", methods=["POST"])
def chat():
    data = request.json
    if "mensaje" not in data:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    respuesta = generar_respuesta_ia(data["mensaje"])
    return jsonify({"respuesta": respuesta})
