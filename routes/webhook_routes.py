# routes/webhook_routes.py
from flask import Blueprint, request, jsonify
from services.conversacion_service import guardar_conversacion
from services.ubicacion_service import guardar_ubicacion, obtener_ubicacion
from services.restaurante_service import listar_restaurantes
from services.ia_service import calcular_distancias_reales, generar_respuesta_ia
from services.telegram_service import enviar_mensaje_telegram
from geopy.distance import geodesic
import threading
import os

webhook_bp = Blueprint("webhook", __name__)

def procesar_mensaje_background(data):
    """
    Esta función se ejecuta en segundo plano. Hace el trabajo pesado de buscar 
    restaurantes y consultar a la IA sin hacer que Telegram espere.
    """
    mensaje_usuario = ""
    usuario_id = None
    ubicacion_usuario = None
    es_ubicacion = False

    try:
        msg = data["message"]
        usuario_id = str(msg["chat"]["id"])

        # 🧭 Mensaje con ubicación
        if "location" in msg:
            lat = msg["location"]["latitude"]
            lon = msg["location"]["longitude"]
            ubicacion_usuario = {"lat": lat, "lon": lon}
            guardar_ubicacion(usuario_id, lat, lon)
            mensaje_usuario = "ubicacion_enviada"
            es_ubicacion = True
            print(f"📍 Ubicación recibida: {lat}, {lon}")

        # 💬 Mensaje de texto
        elif "text" in msg:
            # 🛡️ SEGURIDAD: Cortamos el mensaje a 300 caracteres para evitar abusos de tokens
            mensaje_usuario = msg["text"][:300].lower()
            print(f"💬 Mensaje texto: {mensaje_usuario}")

        else:
            return

    except Exception as e:
        print("❌ Error extrayendo datos del mensaje:", e)
        return

    # ==========================================
    # FLUJO CONVERSACIONAL Y MANEJO DE UBICACIÓN
    # ==========================================
    ubic = obtener_ubicacion(usuario_id)
    if ubic:
        ubicacion_usuario = {"lat": ubic["lat"], "lon": ubic["lon"]}

    # 1. SALUDOS
    saludos = ["hola", "hi", "hello", "buenos dias", "buenas tardes", "buenas", "buenas noches", "/start"]
    if mensaje_usuario in saludos:
        if ubicacion_usuario:
            respuesta = """👋 ¡Hola! Soy CaliFoodBot 🍽️\n\nVeo que ya tienes ubicación guardada. ¿Qué te apetece comer hoy?\n\n• Específico: "choripán", "hamburguesas", "pizza", "sushi"\n• Por tipo: "comida mexicana", "comida rápida", "postres"\n• Por zona: "en el norte", "en el centro"\n• Por precio: "comida barata", "restaurante económico"\n• O di "no sé" para variedad cerca\n\n📍 También puedes actualizar tu ubicación enviándome tu nueva ubicación usando el clip 📎."""
        else:
            respuesta = """👋 ¡Hola! Soy CaliFoodBot 🍽️\n\nPara recomendarte los mejores restaurantes cercanos en Cali, necesito tu ubicación.\n📍 Por favor, comparte tu ubicación usando el clip 📎 en Telegram.\nLuego podrás buscar por tipo, zona o precio."""
        
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_telegram(usuario_id, respuesta)
        return

    # 2. CORTESÍAS Y DESPEDIDAS
    cortesias = ["gracias", "muchas gracias", "mil gracias", "ok", "vale", "perfecto", "listo", "adiós", "adios", "chao", "hasta luego", "genial", "excelente"]
    if mensaje_usuario in cortesias or "gracias" in mensaje_usuario:
        respuesta = "¡Con mucho gusto! 🍽️ Si se te antoja algo más adelante, aquí estaré. ¡Que tengas un gran día!"
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_telegram(usuario_id, respuesta)
        return  

    if es_ubicacion:
        respuesta = """📍 ¡Perfecto! Ubicación recibida.\n\n🍽️ Ahora puedes:\n• "quiero choripán", "busco hamburguesas"\n• Por zona: "en el norte", "en el centro"\n• Por precio: "comida económica"\n• O "no sé" para variedad cerca de ti\n\n¿Qué se te antoja comer?"""
        guardar_conversacion(usuario_id, "ubicacion_enviada", respuesta)
        enviar_mensaje_telegram(usuario_id, respuesta)
        return

    if not ubicacion_usuario:
        respuesta = "📍 Para poder recomendarte restaurantes cercanos, necesito tu ubicación.\nPor favor, compártela usando el clip 📎 en Telegram."
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_telegram(usuario_id, respuesta)
        return

    if any(palabra in mensaje_usuario for palabra in ["actualizar ubicacion", "actualizar ubicación", "nueva ubicacion", "cambiar ubicacion"]):
        respuesta = "📍 ¡Por supuesto! Envíame tu nueva ubicación usando el clip 📎 en Telegram."
        guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
        enviar_mensaje_telegram(usuario_id, respuesta)
        return

    # ==============================================================
    # LÓGICA DE BÚSQUEDA OPTIMIZADA (FILTRO BD -> LÍNEA RECTA -> OSRM)
    # ==============================================================
    
    restaurantes_filtrados = listar_restaurantes()
    contexto = "Usuario con ubicación disponible"
    
    no_sabe = any(palabra in mensaje_usuario for palabra in ["no sé", "no se", "no idea", "no tengo idea", "qué recomiendas", "recomiéndame", "sugiere", "qué hay", "variedad"])
    
    if not no_sabe:
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

        if etiqueta_detectada:
            restaurantes_temp = [r for r in restaurantes_filtrados if r.get('subtipo') and any(etiqueta_detectada in str(subtipo).lower() for subtipo in r['subtipo'])]
            contexto = f"Usuario busca {etiqueta_detectada}"
            
            if not restaurantes_temp:
                restaurantes_temp = [r for r in restaurantes_filtrados if etiqueta_detectada in r.get("tipo", "").lower()]
                contexto = f"Usuario busca {etiqueta_detectada} (en tipo general)"
            
            restaurantes_filtrados = restaurantes_temp

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
            restaurantes_filtrados = [r for r in restaurantes_filtrados if zona_detectada in r.get("zona", "").lower()]
            contexto += f" en {zona_detectada}"

    for r in restaurantes_filtrados:
        ubic = r.get("ubicacion", {})
        lat_rest = ubic.get("lat")
        lon_rest = ubic.get("lng") or ubic.get("lon")
        
        if lat_rest and lon_rest:
            r["distancia_lineal"] = geodesic((ubicacion_usuario["lat"], ubicacion_usuario["lon"]), (lat_rest, lon_rest)).km
        else:
            r["distancia_lineal"] = 999
            
    if any(palabra in mensaje_usuario for palabra in ["cerca", "cercano", "cercana", "cercanía", "próximo", "prxima"]):
        restaurantes_filtrados = [r for r in restaurantes_filtrados if r["distancia_lineal"] <= 2.5] 
        contexto += " (muy cercanos)"

    restaurantes_filtrados.sort(key=lambda x: x["distancia_lineal"])
    top_cercanos = restaurantes_filtrados[:15]

    restaurantes_con_distancias = calcular_distancias_reales(top_cercanos, ubicacion_usuario)
    
    if not restaurantes_con_distancias:
        if no_sabe:
            respuesta = "😔 No tengo restaurantes registrados cerca de tu ubicación actual. ¿Quieres actualizar tu ubicación o buscar en otra zona?"
        else:
            todos_cercanos = listar_restaurantes()
            for r in todos_cercanos:
                ubic = r.get("ubicacion", {})
                lat_rest, lon_rest = ubic.get("lat"), (ubic.get("lng") or ubic.get("lon"))
                r["distancia_lineal"] = geodesic((ubicacion_usuario["lat"], ubicacion_usuario["lon"]), (lat_rest, lon_rest)).km if (lat_rest and lon_rest) else 999
            
            todos_cercanos.sort(key=lambda x: x["distancia_lineal"])
            alternativos = calcular_distancias_reales(todos_cercanos[:5], ubicacion_usuario)
            
            if alternativos:
                respuesta = f"🔍 No encontré restaurantes que coincidan exactamente con tu búsqueda. Te recomiendo estas opciones cercanas:\n\n"
                from services.ia_service import formatear_distancia
                for i, r in enumerate(alternativos, 1):
                    dist_txt = formatear_distancia(r.get('distancia_real_km'))
                    respuesta += f"{i}. {r['nombre']} - {r['tipo']} - {r['zona']} {dist_txt}\n"
                respuesta += "\n💡 También puedes actualizar tu ubicación si te has movido."
            else:
                respuesta = "😔 No tengo restaurantes disponibles. Por favor, actualiza tu ubicación si te has movido."
    else:
        respuesta = generar_respuesta_ia(mensaje_usuario, restaurantes_con_distancias, ubicacion_usuario, contexto)

    guardar_conversacion(usuario_id, mensaje_usuario, respuesta)
    enviar_mensaje_telegram(usuario_id, respuesta)


@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    # 🛡️ SEGURIDAD: Validar el token secreto de Telegram
    token_secreto = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if token_secreto != "CaliFoodSecreto2026":
        print("⛔ Intento de acceso no autorizado al webhook")
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error": "Datos vacíos"}), 400

    if "message" not in data:
        return jsonify({"status": "Ignorado - no es un mensaje"}), 200

    hilo = threading.Thread(target=procesar_mensaje_background, args=(data,))
    hilo.start()

    return jsonify({"status": "procesando en segundo plano"}), 200


@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    return jsonify({"status": "El webhook está activo y seguro."}), 200