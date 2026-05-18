# routes/webhook_routes.py
from flask import Blueprint, request, jsonify
from services.conversacion_service import guardar_conversacion
from services.ubicacion_service import guardar_ubicacion, obtener_ubicacion
from services.restaurante_service import listar_restaurantes
from services.ia_service import calcular_distancias_reales, generar_respuesta_ia
import requests
import os

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Mensaje entrante:", data)

    if not data:
        return jsonify({"error": "Datos vacíos"}), 400

    mensaje_usuario = ""
    usuario_id = None
    ubicacion_usuario = None
    es_ubicacion = False

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        mensajes = entry.get("messages", [])

        if not mensajes:
            return jsonify({"error": "No hay mensajes"}), 400

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

        else:
            return jsonify({"error": "Tipo de mensaje no soportado"}), 400

    except Exception as e:
        print("❌ Error procesando mensaje:", e)
        return jsonify({"error": "Formato inválido"}), 400

    # FLUJO CONVERSACIONAL MEJORADO
    ubic = obtener_ubicacion(usuario_id)
    if ubic:
        ubicacion_usuario = {"lat": ubic["lat"], "lon": ubic["lon"]}
        print(f"📍 Ubicación guardada: {ubicacion_usuario}")

    # MANEJO DE SALUDOS INICIALES
    saludos = ["hola", "hi", "hello", "buenos dias", "buenas tardes", "buenas", "buenas noches"]
    if mensaje_usuario in saludos:
        if ubicacion_usuario:
            respuesta = """👋 ¡Hola! Soy CaliFoodBot 🍽️

Veo que ya tienes ubicación guardada. ¿Qué te apetece comer hoy?

Puedes:
• Específico: "choripán", "hamburguesas", "pizza", "sushi"
• Por tipo: "comida mexicana", "comida rápida", "postres"  
• Por zona: "en el norte", "en el centro"
• Por precio: "comida barata", "restaurante económico"
• O decir "no sé" para recomendarte variedad cerca

También puedes actualizar tu ubicación en cualquier momento."""
        else:
            respuesta = """👋 ¡Hola! Soy CaliFoodBot 🍽️

Para recomendarte los mejores restaurantes cercanos en Cali, necesito tu ubicación.

📍 Por favor, comparte tu ubicación usando el clip 📎 en WhatsApp.

Luego podrás buscar por tipo específico, zona o precio."""
        
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": respuesta}), 200

    # SI ACABA DE ENVIAR UBICACIÓN
    if es_ubicacion:
        respuesta = """📍 ¡Perfecto! Ubicación recibida. 

🍽️ Ahora puedes:
• Pedir algo específico: "quiero choripán", "busco hamburguesas"
• Filtrar por zona: "en el norte", "en el centro"
• Buscar por precio: "comida económica", "restaurante barato"  
• O decir "no sé" para recomendarte variedad cerca de ti

¿Qué se te antoja comer?"""
        
        guardar_conversacion(usuario_id, "ubicacion_enviada", respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": "ubicacion_recibida"}), 200

    # SI NO TIENE UBICACIÓN Y NO ES SALUDO
    if not ubicacion_usuario:
        respuesta = "📍 Para poder recomendarte restaurantes cercanos, necesito tu ubicación. Por favor, compártela usando el clip 📎 en WhatsApp. También puedes actualizarla en cualquier momento si te mueves."
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": "ubicacion_requerida"}), 200

    # DETECCIÓN DE ACTUALIZACIÓN DE UBICACIÓN
    if any(palabra in mensaje_usuario for palabra in ["actualizar ubicacion", "actualizar ubicación", "nueva ubicacion", "cambiar ubicacion"]):
        respuesta = "📍 ¡Por supuesto! Puedes actualizar tu ubicación enviándome tu nueva ubicación usando el clip 📎 en WhatsApp. Así tendré información más precisa para recomendarte."
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_whatsapp(usuario_id, respuesta)
        return jsonify({"respuesta": "solicitud_actualizar_ubicacion"}), 200

    # PROCESAR CONSULTA CON UBICACIÓN DISPONIBLE
    restaurantes = listar_restaurantes()
    
    # Calcular distancias REALES para todos los restaurantes
    restaurantes_con_distancias = calcular_distancias_reales(restaurantes, ubicacion_usuario)

    # FILTRADO AVANZADO MULTI-CRITERIO
    contexto = "Usuario con ubicación disponible"
    restaurantes_filtrados = restaurantes_con_distancias.copy()
    
    # Detectar si no sabe qué quiere
    no_sabe = any(palabra in mensaje_usuario for palabra in [
        "no sé", "no se", "no idea", "no tengo idea", "qué recomiendas", 
        "recomiéndame", "sugiere", "qué hay", "variedad"
    ])
    
    if not no_sabe:
        # FILTRO POR ETIQUETAS ESPECÍFICAS
        etiquetas_especificas = {
            "choripán": ["choripán", "choripan", "chori"],
            "hamburguesa": ["hamburguesa", "hamburguesas", "burger", "hamburgues"],
            "pizza": ["pizza", "pizzas", "pizzería"],
            "taco": ["taco", "tacos", "taquitos"],
            "sushi": ["sushi", "rolls", "sashimi"],
            "arepa": ["arepa", "arepas"],
            "empanada": ["empanada", "empanadas"],
            "pasta": ["pasta", "pastas", "espagueti", "lasaña", "lasagna"],
            "postre": ["postre", "postres", "dulce", "helado", "torta"],
            "café": ["café", "cafe", "capuchino", "expreso"]
        }

        etiqueta_detectada = None
        for etiqueta, palabras in etiquetas_especificas.items():
            if any(palabra in mensaje_usuario for palabra in palabras):
                etiqueta_detectada = etiqueta
                break

        # APLICAR FILTRO POR ETIQUETA ESPECÍFICA
        if etiqueta_detectada:
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if r.get('subtipo') and any(etiqueta_detectada in str(subtipo).lower() for subtipo in r['subtipo'])]
            contexto = f"Usuario busca {etiqueta_detectada}"
            
            # Si no hay resultados con etiqueta específica, buscar en tipo general
            if not restaurantes_filtrados:
                restaurantes_filtrados = [r for r in restaurantes_con_distancias 
                                        if etiqueta_detectada in r.get("tipo", "").lower()]
                contexto = f"Usuario busca {etiqueta_detectada} (en tipo general)"

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
        
        if zona_detectada:
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if zona_detectada in r.get("zona", "").lower()]
            contexto += f" en {zona_detectada}"

        # FILTRO POR CERCANÍA ESPECÍFICA
        if any(palabra in mensaje_usuario for palabra in ["cerca", "cercano", "cercana", "cercanía", "próximo", "próxima"]):
            restaurantes_filtrados = [r for r in restaurantes_filtrados 
                                    if r.get("distancia_real_km", 999) <= 2.0]
            contexto += " (muy cercanos)"

    # GENERAR RESPUESTA CON IA MEJORADA
    if not restaurantes_filtrados:
        if no_sabe:
            respuesta = "😔 No tengo restaurantes registrados cerca de tu ubicación actual. ¿Quieres actualizar tu ubicación o buscar en otra zona?"
        else:
            # Ofrecer alternativas sin filtros
            restaurantes_alternativos = restaurantes_con_distancias[:5]
        if restaurantes_alternativos:
            respuesta = f"🔍 No encontré restaurantes que coincidan exactamente con tu búsqueda. Te recomiendo estas opciones cercanas:\n\n"
            for i, r in enumerate(restaurantes_alternativos, 1):
               from services.ia_service import formatear_distancia
            distancia_texto = formatear_distancia(r.get('distancia_real_km'))
            respuesta += f"{i}. {r['nombre']} - {r['tipo']} - {r['zona']} {distancia_texto}\n"
            respuesta += "\n💡 También puedes actualizar tu ubicación si te has movido."
        else:
            respuesta = "😔 No tengo restaurantes disponibles. Por favor, actualiza tu ubicación si te has movido."
    else:
        respuesta = generar_respuesta_ia(mensaje_usuario, restaurantes_filtrados, ubicacion_usuario, contexto)

    # Guardar conversación y enviar respuesta
    guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
    success = enviar_mensaje_whatsapp(usuario_id, respuesta)

    if success:
        print("🤖 Respuesta enviada:", respuesta)
        return jsonify({"respuesta": respuesta}), 200
    else:
        return jsonify({"error": "Error enviando mensaje"}), 500


def enviar_mensaje_whatsapp(numero, texto):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")

    if not token:
        print("❌ WHATSAPP_TOKEN no configurado en .env")
        return False
        
    if not phone_number_id:
        print("❌ PHONE_NUMBER_ID no configurado en .env")
        return False

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
            return True
        else:
            error_data = response.json()
            print(f"❌ Error al enviar mensaje a {numero}: {response.status_code}")
            print(f"📄 Detalles: {error_data}")
            return False
    except Exception as e:
        print(f"❌ Excepción al enviar mensaje: {e}")
        return False


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