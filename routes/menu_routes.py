from flask import Blueprint, request, jsonify
from services.menu_service import crear_menu, listar_menus, obtener_menu_por_restaurante

menu_bp = Blueprint("menu_bp", __name__)

@menu_bp.route("/", methods=["POST"])
def post_menu():
    data = request.json
    return jsonify(crear_menu(data)), 201

@menu_bp.route("/", methods=["GET"])
def get_menus():
    return jsonify(listar_menus()), 200

@menu_bp.route("/restaurante/<restaurante_id>", methods=["GET"])
def get_menu_por_restaurante(restaurante_id):
    return jsonify(obtener_menu_por_restaurante(restaurante_id)), 200
