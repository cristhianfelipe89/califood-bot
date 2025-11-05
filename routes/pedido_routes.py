from flask import Blueprint, request, jsonify
from services.pedido_service import crear_pedido, listar_pedidos

pedido_bp = Blueprint("pedido_bp", __name__)

@pedido_bp.route("/", methods=["POST"])
def post_pedido():
    data = request.json
    return jsonify(crear_pedido(data)), 201

@pedido_bp.route("/", methods=["GET"])
def get_pedidos():
    return jsonify(listar_pedidos()), 200
