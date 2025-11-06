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
# FUNCIÓN PRINCIPAL: Webhook de WhatsApp MEJORADO
# ---------------------------------------------
@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Mensaje entrante:", data)

    mensaje_usuario = ""
    usuario_id = None
    ubicacion_usuario = None
    es_ubicacion = False
    actualizar_ubicacion = False

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
                es_ubicacion = True
                print(f"📍 Ubicación recibida/actualizada: {lat}, {lon}")

            # 💬 Mensaje de texto
            elif msg.get("text"):
                mensaje_usuario = msg["text"]["body"].lower()
                print(f"💬 Mensaje texto: {mensaje_usuario}")

    except Exception as e:
        print("❌ Error procesando mensaje:", e)
        return jsonify({"error": "Formato inválido"}), 400

    if not mensaje_usuario:
        return jsonify({"error": "Mensaje vacío"}), 400

    # ---------------------------------------------
    # DETECCIÓN DE ACTUALIZACIÓN DE UBICACIÓN
    # ---------------------------------------------
    if any(palabra in mensaje_usuario for palabra in ["actualizar ubicacion", "actualizar ubicación", "nueva ubicacion", "cambiar ubicacion"]):
        respuesta = "📍 ¡Por supuesto! Puedes actualizar tu ubicación enviándome tu nueva ubicación usando el clip 📎 en WhatsApp. Así tendré información más precisa para recomendarte."
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": "solicitud_actualizar_ubicacion"}), 200

    # ---------------------------------------------
    # FLUJO CONVERSACIONAL MEJORADO
    # ---------------------------------------------

    # 1. OBTENER UBICACIÓN GUARDADA (siempre verificar la más reciente)
    ubic = obtener_ubicacion(usuario_id)
    if ubic:
        ubicacion_usuario = {"lat": ubic["lat"], "lon": ubic["lon"]}
        print(f"📍 Ubicación guardada: {ubicacion_usuario}")

    # 2. MANEJO DE SALUDOS INICIALES MEJORADO
    saludos = ["hola", "hi", "hello", "buenos dias", "buenas tardes", "buenas", "buenas noches"]
    if mensaje_usuario in saludos:
        if ubicacion_usuario:
            respuesta = """👋 ¡Hola! Soy CaliFoodBot 🍽️

Veo que ya tienes ubicación guardada. ¿Qué te apetece comer hoy?

Puedes:
• Decirme un tipo específico: "pizza", "sushi", "comida mexicana"
• Pedir por zona: "en el norte", "en el centro"  
• Buscar por precio: "comida barata", "restaurante económico"
• O decir "no sé" para recomendarte variedad cerca de ti

También puedes actualizar tu ubicación en cualquier momento."""
        else:
            respuesta = """👋 ¡Hola! Soy CaliFoodBot 🍽️

Para recomendarte los mejores restaurantes cercanos en Cali, necesito tu ubicación.

📍 Por favor, comparte tu ubicación usando el clip 📎 en WhatsApp.

Luego podrás:
• Buscar por tipo de comida
• Filtrar por zona
• Encontrar opciones por precio
• Recibir recomendaciones personalizadas"""
        
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": respuesta}), 200

    # 3. SI ACABA DE ENVIAR UBICACIÓN
    if es_ubicacion:
        respuesta = """📍 ¡Perfecto! Ubicación recibida. 

🍽️ Ahora puedes:
• Pedir un tipo específico: "quiero pizza", "busco sushi"
• Filtrar por zona: "en el norte", "en el centro"
• Buscar por precio: "comida económica", "restaurante barato"  
• O decir "no sé" para recomendarte variedad cerca de ti

¿Qué te gustaría comer?"""
        
        guardar_conversacion(usuario_id, "ubicacion_enviada", respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": "ubicacion_recibida"}), 200

    # 4. SI NO TIENE UBICACIÓN Y NO ES SALUDO
    if not ubicacion_usuario:
        respuesta = "📍 Para poder recomendarte restaurantes cercanos, necesito tu ubicación. Por favor, compártela usando el clip 📎 en WhatsApp. También puedes actualizarla en cualquier momento si te mueves."
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": "ubicacion_requerida"}), 200

    # 5. PROCESAR CONSULTA CON UBICACIÓN DISPONIBLE - FILTRADO MEJORADO
    restaurantes = listar_restaurantes()
    
    # Calcular distancias para TODOS los restaurantes
    restaurantes_con_distancia = []
    for r in restaurantes:
        ubic_rest = r.get("ubicacion", {})
        lat_rest = ubic_rest.get("lat")
        lon_rest = ubic_rest.get("lng") or ubic_rest.get("lon")
        
        if lat_rest and lon_rest:
            try:
                distancia = geodesic(
                    (ubicacion_usuario["lat"], ubicacion_usuario["lon"]),
                    (lat_rest, lon_rest)
                ).km
                r["distancia_km"] = round(distancia, 2)
                restaurantes_con_distancia.append(r)
            except Exception as e:
                print(f"❌ Error calculando distancia: {e}")
                restaurantes_con_distancia.append(r)

    # Ordenar por distancia
    restaurantes_ordenados = sorted(restaurantes_con_distancia, 
                                  key=lambda x: x.get("distancia_km", 999))

    # 6. FILTRADO AVANZADO MULTI-CRITERIO
    contexto = "Usuario con ubicación disponible"
    restaurantes_filtrados = restaurantes_ordenados.copy()
    
    # Detectar si no sabe qué quiere
    no_sabe = any(palabra in mensaje_usuario for palabra in [
        "no sé", "no se", "no idea", "no tengo idea", "qué recomiendas", 
        "recomiéndame", "sugiere", "qué hay", "variedad"
    ])
    
    if no_sabe:
        contexto = "Usuario pide variedad - mostrar opciones cercanas"
        # Ya está ordenado por distancia
    else:
        # FILTRO POR TIPO DE COMIDA
        tipos_comida = {
            "pizza": ["pizza", "pizzas", "pizzería"],
            "hamburguesa": ["hamburguesa", "hamburguesas", "burger", "hamburgues"],
            "choripán": ["choripán", "choripan", "chori"],
            "taco": ["taco", "tacos"],
            "sushi": ["sushi", "japonés", "japonesa", "japones"],
            "pollo": ["pollo", "polla", "broaster"],
            "arepa": ["arepa", "arepas"],
            "pasta": ["pasta", "pastas", "espagueti", "lasaña", "lasagna"],
            "ensalada": ["ensalada", "ensaladas"],
            "empanada": ["empanada", "empanadas"],
            "mexicana": ["mexicana", "mexicano", "tacos", "burrito", "mexican"],
            "italiana": ["italiana", "italiano", "pasta", "pizza", "italian"],
            "china": ["china", "chino", "arroz chino", "comida china"],
            "rápida": ["rápida", "comida rápida", "fast food", "rapida"],
            "típica": ["típica", "tradicional", "valluna", "sancocho", "tipica"],
            "postres": ["postres", "postre", "dulce", "helado", "dulces"],
            "café": ["café", "cafe", "cafetería", "capuchino", "cafeteria"],
            "saludable": ["saludable", "salud", "healthy", "fit"],
            "jugos": ["jugos", "jugo", "naturales", "zumo"]
        }

        tipo_detectado = None
        for tipo, palabras in tipos_comida.items():
            if any(palabra in mensaje_usuario for palabra in palabras):
                tipo_detectado = tipo
                break
        
        # FILTRO POR ZONA
        zonas = {
            "norte": ["norte", "granada", "chipichape"],
            "sur": ["sur", "ciudad jardín", "ciudad jardin", "limonar"],
            "centro": ["centro", "san antonio"],
            "oeste": ["oeste", "normandía", "normandia"],
            "oriente": ["oriente", "este"]
        }
        
        zona_detectada = None
        for zona, palabras in zonas.items():
            if any(palabra in mensaje_usuario for palabra in palabras):
                zona_detectada = zona
                break
        
        # FILTRO POR PRECIO
        precios = {
            "baja": ["barato", "barata", "económico", "economico", "económica", "bajo", "baja", "low cost"],
            "media": ["medio", "media", "moderado", "moderada", "normal"],
            "alta": ["alto", "alta", "lujoso", "lujosa", "premium", "caro", "cara"]
        }
        
        precio_detectado = None
        for precio, palabras in precios.items():
            if any(palabra in mensaje_usuario for palabra in palabras):
                precio_detectado = precio
                break
        
        # FILTRO POR NOMBRE (búsqueda directa)
        nombre_detectado = None
        for r in restaurantes_ordenados:
            if r['nombre'].lower() in mensaje_usuario:
                nombre_detectado = r['nombre']
                break
        
        # APLICAR FILTROS EN CASCADA
        if tipo_detectado:
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if tipo_detectado in r.get("tipo", "").lower()]
            contexto = f"Usuario busca {tipo_detectado}"
        
        if zona_detectada:
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if zona_detectada in r.get("zona", "").lower()]
            contexto += f" en {zona_detectada}"
        
        if precio_detectado:
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if precio_detectado in r.get("precio", "").lower()]
            contexto += f" precio {precio_detectado}"
        
        if nombre_detectado:
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if nombre_detectado.lower() in r.get("nombre", "").lower()]
            contexto = f"Búsqueda por nombre: {nombre_detectado}"
        
        # FILTRO POR CERCANÍA ESPECÍFICA
        if any(palabra in mensaje_usuario for palabra in ["cerca", "cercano", "cercana", "cercanía", "próximo", "próxima"]):
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if r.get("distancia_km", 999) <= 2.0]  # Dentro de 2km
            contexto += " (muy cercanos)"

    # 7. GENERAR RESPUESTA CON IA MEJORADA
    if not restaurantes_filtrados:
        if no_sabe:
            respuesta = "😔 No tengo restaurantes registrados cerca de tu ubicación actual. ¿Quieres actualizar tu ubicación o buscar en otra zona?"
        else:
            # Ofrecer alternativas sin filtros
            restaurantes_alternativos = restaurantes_ordenados[:5]
            if restaurantes_alternativos:
                respuesta = f"🔍 No encontré restaurantes que coincidan exactamente con tu búsqueda. Te recomiendo estas opciones cercanas:\n\n"
                for i, r in enumerate(restaurantes_alternativos, 1):
                    distancia_texto = f"📍 A {r.get('distancia_km', '?')} km" if r.get('distancia_km') else ""
                    respuesta += f"{i}. {r['nombre']} - {r['tipo']} - {r['zona']} {distancia_texto}\n"
                respuesta += "\n💡 También puedes actualizar tu ubicación si te has movido."
            else:
                respuesta = "😔 No tengo restaurantes disponibles. Por favor, actualiza tu ubicación si te has movido."
    else:
        respuesta = generar_respuesta_ia(mensaje_usuario, restaurantes_filtrados, ubicacion_usuario, contexto)

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

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Mensaje enviado correctamente a {numero}")
        else:
            print(f"❌ Error al enviar mensaje a {numero}: {response.text}")
    except Exception as e:
        print(f"❌ Excepción al enviar mensaje: {e}")


# ---------------------------------------------
# Verificación del webhook (GET)
# ---------------------------------------------
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