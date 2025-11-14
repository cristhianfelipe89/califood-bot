# services/ia_service.py
"""
Servicio de IA MEJORADO: Cálculo PRECISO de distancias con más decimales
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from geopy.distance import geodesic

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def formatear_redes_sociales(redes):
    """Formatea los enlaces de redes sociales de manera legible"""
    if not redes:
        return "No disponibles"
    
    redes_texto = []
    if redes.get('facebook') and redes['facebook'].startswith('http'):
        redes_texto.append(f"📘 [Facebook]({redes['facebook']})")
    if redes.get('instagram') and redes['instagram'].startswith('http'):
        redes_texto.append(f"📷 [Instagram]({redes['instagram']})")
    if redes.get('tiktok') and redes['tiktok'].startswith('http'):
        redes_texto.append(f"🎵 [TikTok]({redes['tiktok']})")
    
    return " | ".join(redes_texto) if redes_texto else "No disponibles"

def calcular_distancias_reales(restaurantes, ubicacion_usuario):
    """
    Calcula distancias reales en km desde la ubicación del usuario a cada restaurante
    CON MÁS PRECISIÓN
    """
    # VERIFICAR que la ubicación del usuario existe
    if not ubicacion_usuario or not ubicacion_usuario.get("lat") or not ubicacion_usuario.get("lon"):
        print("❌ No hay ubicación del usuario para calcular distancias")
        return restaurantes
    
    restaurantes_con_distancias = []
    
    for restaurante in restaurantes:
        restaurante_copy = restaurante.copy()
        ubic_rest = restaurante.get("ubicacion", {})
        lat_rest = ubic_rest.get("lat")
        lon_rest = ubic_rest.get("lng") or ubic_rest.get("lon")
        
        if lat_rest and lon_rest:
            try:
                # Calcular distancia real usando geodesic - CON COORDENADAS EXACTAS
                distancia_km = geodesic(
                    (ubicacion_usuario["lat"], ubicacion_usuario["lon"]),
                    (lat_rest, lon_rest)
                ).km
                
                # Guardar con MÁS decimales para mayor precisión
                restaurante_copy["distancia_real_km"] = round(distancia_km, 3)
                
                print(f"📍 Distancia calculada para {restaurante.get('nombre')}: {distancia_km} km")
                
            except Exception as e:
                print(f"❌ Error calculando distancia para {restaurante.get('nombre')}: {e}")
                restaurante_copy["distancia_real_km"] = None
        else:
            print(f"⚠️ Restaurante {restaurante.get('nombre')} no tiene coordenadas válidas")
            restaurante_copy["distancia_real_km"] = None
        
        restaurantes_con_distancias.append(restaurante_copy)
    
    # Ordenar por distancia real (los más cercanos primero)
    restaurantes_con_distancias.sort(key=lambda x: x.get("distancia_real_km", 9999))
    
    return restaurantes_con_distancias

def formatear_distancia(distancia_km):
    """
    Formatea la distancia de manera legible con más precisión
    """
    if distancia_km is None:
        return "Distancia no disponible"
    
    if distancia_km < 0.05:  # Menos de 50 metros
        return f"A {int(distancia_km * 1000)} metros"
    elif distancia_km < 0.1:  # Menos de 100 metros
        return f"A {int(distancia_km * 1000)} metros"
    elif distancia_km < 1:  # Menos de 1 km
        metros = int(distancia_km * 1000)
        return f"A {metros} m"
    else:  # 1 km o más
        # Mostrar con 2 decimales para distancias largas
        if distancia_km < 10:
            return f"A {distancia_km:.2f} km"
        else:
            return f"A {distancia_km:.1f} km"

def generar_respuesta_ia(mensaje_usuario, restaurantes, ubicacion_usuario=None, contexto=""):
    """
    Versión MEJORADA: Cálculo PRECISO de distancias
    """
    
    if not restaurantes:
        return "🔍 No tengo restaurantes registrados en este momento. Pronto agregaré más opciones para ti. 😊"

    # CALCULAR DISTANCIAS REALES SI HAY UBICACIÓN DEL USUARIO
    restaurantes_con_distancias = calcular_distancias_reales(restaurantes, ubicacion_usuario)

    # Construir información detallada de restaurantes con enlaces a mapas PRECISOS
    restaurantes_info = []
    for r in restaurantes_con_distancias[:15]:
        # Mostrar distancia real calculada - USAR FUNCIÓN DE FORMATEO
        distancia_texto = ""
        if r.get('distancia_real_km') is not None:
            distancia_texto = formatear_distancia(r['distancia_real_km'])
        else:
            distancia_texto = "Distancia no disponible"
        
        # Generar enlace al mapa CON COORDENADAS EXACTAS
        ubic = r.get('ubicacion', {})
        lat_rest = ubic.get('lat')
        lon_rest = ubic.get('lng') or ubic.get('lon')
        
        # Usar coordenadas exactas sin redondear para el enlace
        mapa_url = ubic.get('mapa_url') 
        if not mapa_url and lat_rest and lon_rest:
            # Usar todas las coordenadas disponibles para máxima precisión
            mapa_url = f"https://www.google.com/maps?q={lat_rest},{lon_rest}"
        
        direccion_con_enlace = f"🗺️ [Ver en Google Maps]({mapa_url})" if mapa_url and mapa_url.startswith('http') else ubic.get('direccion', 'No disponible')
        
        # Mostrar etiquetas específicas si existen
        etiquetas_texto = ""
        if r.get('subtipo'):
            etiquetas_texto = f"• 🏷️ Especialidad: {', '.join(r['subtipo'][:3])}\n"
        
        # AGREGAR REDES SOCIALES CON ENLACES REALES
        redes_texto = formatear_redes_sociales(r.get('redes', {}))
        
        info = f"""
🍽️ {r.get('nombre', 'Sin nombre')}
• 🏷️ Tipo: {r.get('tipo', 'No especificado')}
{etiquetas_texto}• 📍 Zona: {r.get('zona', 'No especificada')}
• 💰 Precio: {r.get('precio', 'No especificado')}
• 📞 Contacto: {r.get('contacto', 'No disponible')}
• 🌐 Redes: {redes_texto}
• 🗺️ Dirección: {direccion_con_enlace}
• 📏 {distancia_texto}
"""
        restaurantes_info.append(info)

    restaurantes_texto = "\n".join(restaurantes_info)

    # Información de contexto mejorada con coordenadas exactas
    ubicacion_exacta = ""
    if ubicacion_usuario:
        ubicacion_exacta = f"({ubicacion_usuario['lat']:.6f}, {ubicacion_usuario['lon']:.6f})"
    
    info_contexto = f"""
CONTEXTO DE LA CONVERSACIÓN:
{contexto}

UBICACIÓN ACTUAL DEL USUARIO: {'✅ Disponible ' + ubicacion_exacta if ubicacion_usuario else '❌ No disponible'}

MENSAJE DEL USUARIO: "{mensaje_usuario}"

TOTAL RESTAURANTES FILTRADOS: {len(restaurantes_con_distancias)}
"""

    prompt = f"""
Eres CaliFoodBot, un asistente gastronómico experto en Cali con acceso a base de datos real.

{info_contexto}

INFORMACIÓN DE RESTAURANTES DISPONIBLES (FILTRADOS):
{restaurantes_texto}

INSTRUCCIONES CRÍTICAS:

1. **DISTANCIAS REALES**: Las distancias mostradas son cálculos REALES basados en coordenadas GPS
2. **ENLACES EXACTOS**: Usa los enlaces EXACTOS proporcionados
3. **FORMATO CONSISTENTE**: Mantén el mismo formato para todos los restaurantes
4. **NO MODIFICAR DISTANCIAS**: Muestra las distancias exactamente como están formateadas

Ahora responde al usuario mostrando los restaurantes con sus distancias reales calculadas:
"""

    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensaje_usuario},
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Error con OpenAI:", e)
        return generar_respuesta_fallback_mejorada(restaurantes_con_distancias, ubicacion_usuario, contexto)

def generar_respuesta_fallback_mejorada(restaurantes, ubicacion_usuario, contexto):
    """Fallback mejorado cuando OpenAI falla"""
    
    if not restaurantes:
        return "😔 No encontré restaurantes que coincidan con tu búsqueda. ¿Quieres intentar con otros criterios?"
    
    # Ordenar por distancia real
    restaurantes_ordenados = calcular_distancias_reales(restaurantes, ubicacion_usuario)
    
    respuesta = "🍽️ ¡Encontré estas opciones para ti!\n\n"
    
    for i, r in enumerate(restaurantes_ordenados[:5], 1):
        # Mostrar distancia real si está disponible - USAR FUNCIÓN DE FORMATEO
        distancia_texto = ""
        if r.get('distancia_real_km') is not None:
            distancia_texto = formatear_distancia(r['distancia_real_km'])
        else:
            distancia_texto = "Distancia no disponible"
        
        # Mostrar etiquetas si existen
        etiquetas_texto = ""
        if r.get('subtipo'):
            etiquetas_texto = f"Especialidad: {', '.join(r['subtipo'][:2])}\n"
        
        # AGREGAR REDES SOCIALES EN FALLBACK
        redes_texto = formatear_redes_sociales(r.get('redes', {}))
        
        # Generar enlace al mapa
        ubic = r.get('ubicacion', {})
        mapa_url = ubic.get('mapa_url')
        if not mapa_url:
            lat_rest = ubic.get('lat')
            lon_rest = ubic.get('lng') or ubic.get('lon')
            if lat_rest and lon_rest:
                mapa_url = f"https://www.google.com/maps?q={lat_rest},{lon_rest}"
        
        direccion_con_enlace = f"[Ver en Google Maps]({mapa_url})" if mapa_url else ubic.get('direccion', 'No disponible')
        
        respuesta += f"""*{r.get('nombre', 'Sin nombre')}*
- Tipo: {r.get('tipo', 'No especificado')}
{'- ' + etiquetas_texto if etiquetas_texto else ''}- Zona: {r.get('zona', 'No especificada')}
- Precio: {r.get('precio', 'No especificado')}
- Contacto: {r.get('contacto', 'No disponible')}
- Redes: {redes_texto}
- Dirección: {direccion_con_enlace}
- {distancia_texto}

"""
    
    respuesta += "💡 ¿Quieres filtrar por tipo específico, zona o precio?"
    
    return respuesta

def obtener_emoji_tipo(tipo):
    """Devuelve emoji según el tipo de comida"""
    tipo = tipo.lower()
    if 'pizza' in tipo or 'italiana' in tipo:
        return '🍕'
    elif 'sushi' in tipo or 'japonesa' in tipo:
        return '🍣'
    elif 'mexicana' in tipo:
        return '🌮'
    elif 'hamburguesa' in tipo or 'rápida' in tipo:
        return '🍔'
    elif 'café' in tipo or 'cafetería' in tipo:
        return '☕'
    elif 'postre' in tipo:
        return '🍰'
    elif 'típica' in tipo:
        return '🥘'
    elif 'china' in tipo:
        return '🥡'
    elif 'saludable' in tipo:
        return '🥗'
    elif 'jugo' in tipo:
        return '🥤'
    else:
        return '🍽️'