# routes/webhook_routes.py
from flask import Blueprint, request, jsonify
from services.conversacion_service import guardar_conversacion
from services.ubicacion_service import guardar_ubicacion, obtener_ubicacion
from services.restaurante_service import listar_restaurantes
from geopy.distance import geodesic
import requests
import os
import re
from services.ia_service import generar_respuesta_ia
webhook_bp = Blueprint("webhook", __name__)

# ---------------------------------------------
# FUNCIÓN PRINCIPAL: Webhook de WhatsApp
# ---------------------------------------------
@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Mensaje entrante:", data)

    mensaje_usuario = ""
    usuario_id = None
    ubicacion_usuario = None

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        mensajes = entry.get("messages", [])

        if mensajes:
            msg = mensajes[0]
            usuario_id = msg["from"]

            # 🧭 Mensaje con ubicación
            if msg.get("location"):
                lat = msg["location"]["latitude"]
                lon = msg["location"]["longitude"]
                ubicacion_usuario = {"lat": lat, "lon": lon}
                guardar_ubicacion(usuario_id, lat, lon)
                mensaje_usuario = "ubicacion_enviada"

            # 💬 Mensaje de texto
            elif msg.get("text"):
                mensaje_usuario = msg["text"]["body"].lower()

    except Exception as e:
        print("❌ Error procesando mensaje:", e)
        return jsonify({"error": "Formato inválido"}), 400

    if not mensaje_usuario:
        return jsonify({"error": "Mensaje vacío"}), 400

    # ---------------------------------------------
    # Si el usuario no ha enviado ubicación, pedirla
    # ---------------------------------------------
    ubic = obtener_ubicacion(usuario_id)
    if ubic:
        ubicacion_usuario = {"lat": ubic["lat"], "lon": ubic["lon"]}
    elif mensaje_usuario != "ubicacion_enviada":
        enviar_mensaje_whatsapp(
            usuario_id,
            "📍 Por favor, comparte tu ubicación para mostrarte restaurantes cercanos."
        )
        return jsonify({"respuesta": "ubicacion_pedida"}), 200

    # ---------------------------------------------
    # Detectar tipo de comida en el mensaje
    # ---------------------------------------------
    tipos_comida = [
        "pizza", "hamburguesa", "choripán", "taco", "sushi",
        "pollo", "arepa", "pasta", "ensalada", "empanada",
        "mexicana", "italiana", "china", "rápida", "típica", "postres", "café"
    ]

    tipo_detectado = None
    for tipo in tipos_comida:
        if re.search(rf"\b{tipo}\b", mensaje_usuario):
            tipo_detectado = tipo
            break

    if not tipo_detectado and mensaje_usuario not in ["ubicacion_enviada", "hola"]:
        enviar_mensaje_whatsapp(
            usuario_id,
            "🍽️ ¿Qué tipo de comida te gustaría hoy? (Ej: pizza, sushi, comida mexicana...)"
        )
        return jsonify({"respuesta": "esperando_tipo"}), 200

    # ---------------------------------------------
    # Filtrar restaurantes según tipo y ubicación
    # ---------------------------------------------
    restaurantes = listar_restaurantes()
    restaurantes_filtrados = []

    for r in restaurantes:
        if tipo_detectado and tipo_detectado not in r["tipo"].lower():
            continue
        if ubicacion_usuario and "lat" in r and "lon" in r:
            distancia = geodesic(
                (ubicacion_usuario["lat"], ubicacion_usuario["lon"]),
                (r["lat"], r["lon"])
            ).km
            if distancia <= 3:
                r["distancia_km"] = round(distancia, 2)
                restaurantes_filtrados.append(r)

    # ---------------------------------------------
    # Construir la respuesta
    # ---------------------------------------------
    if not restaurantes_filtrados:
        respuesta = f"No encontré restaurantes cercanos de *{tipo_detectado or 'ese tipo'}* 😢"
    else:
        respuesta = generar_respuesta_ia(mensaje_usuario, restaurantes_filtrados)

    # 💾 Guardar conversación
    guardar_conversacion(usuario_id, mensaje_usuario, respuesta)

    # 📤 Enviar respuesta
    enviar_mensaje_whatsapp(usuario_id, respuesta)

    print("🤖 Respuesta enviada:", respuesta)
    return jsonify({"respuesta": respuesta}), 200


# ---------------------------------------------
# Enviar mensaje por WhatsApp Cloud API
# ---------------------------------------------
def enviar_mensaje_whatsapp(numero, texto):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    if not token or not phone_number_id:
        print("⚠️ Falta configurar WHATSAPP_TOKEN o PHONE_NUMBER_ID en .env")
        return

    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"✅ Mensaje enviado correctamente a {numero}")
    else:
        print(f"❌ Error al enviar mensaje a {numero}: {response.text}")


# ---------------------------------------------
# Verificación del webhook (GET)
# ---------------------------------------------
# ✅ GET: verificación de token de Meta
@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = os.getenv("VERIFY_TOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            print("✅ Webhook verificado correctamente")
            return challenge, 200
        else:
            print("❌ Token de verificación inválido")
            return "Error: token inválido", 403

    return "Error: parámetros faltantes", 400
