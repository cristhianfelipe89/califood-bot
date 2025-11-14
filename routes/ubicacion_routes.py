# routes/ubicacion_routes.py
from flask import Blueprint, request, jsonify
from services.ubicacion_service import guardar_ubicacion, obtener_ubicacion

ubicacion_bp = Blueprint("ubicaciones", __name__)

@ubicacion_bp.route("/api/ubicacion", methods=["POST"])
def guardar():
    data = request.get_json()
    usuario = data.get("usuario")
    lat = data.get("lat")
    lon = data.get("lon")

    if not usuario or not lat or not lon:
        return jsonify({"error": "Faltan datos"}), 400

    guardar_ubicacion(usuario, lat, lon)
    return jsonify({"mensaje": "Ubicación guardada"}), 201

@ubicacion_bp.route("/api/ubicacion/<usuario>", methods=["GET"])
def obtener(usuario):
    ubic = obtener_ubicacion(usuario)
    if not ubic:
        return jsonify({"error": "Ubicación no encontrada"}), 404
    
    # Formatear respuesta con enlace al mapa
    respuesta = {
        "usuario": ubic["usuario"],
        "lat": ubic["lat"],
        "lon": ubic["lon"],
        "fecha": ubic["fecha"].isoformat() if ubic.get("fecha") else None,
        "mapa_url": ubic.get("mapa_url", f"https://www.google.com/maps?q={ubic['lat']},{ubic['lon']}")
    }
    
    return jsonify(respuesta)