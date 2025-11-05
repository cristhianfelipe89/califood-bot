"""
Rutas para manejar la API de restaurantes.
"""
from flask import Blueprint, request, jsonify
from services.restaurante_service import (
    crear_restaurante,
    listar_restaurantes,
    obtener_restaurante_por_id,
    buscar_restaurante_por_nombre
)

restaurante_bp = Blueprint("restaurante_bp", __name__)

@restaurante_bp.route("/", methods=["POST"])
def post_restaurante():
    data = request.json
    nuevo_restaurante = crear_restaurante(data)
    return jsonify(nuevo_restaurante), 201

@restaurante_bp.route("/", methods=["GET"])
def get_restaurantes():
    return jsonify(listar_restaurantes()), 200

@restaurante_bp.route("/<id>", methods=["GET"])
def get_restaurante(id):
    restaurante = obtener_restaurante_por_id(id)
    return (jsonify(restaurante), 200) if restaurante else (jsonify({"error": "No encontrado"}), 404)

@restaurante_bp.route("/buscar", methods=["GET"])
def get_restaurante_por_nombre():
    nombre = request.args.get("nombre")
    if not nombre:
        return jsonify({"error": "Falta el parámetro 'nombre'"}), 400
    restaurante = buscar_restaurante_por_nombre(nombre)
    return (jsonify(restaurante), 200) if restaurante else (jsonify({"error": "No encontrado"}), 404)
