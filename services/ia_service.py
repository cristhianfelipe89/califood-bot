"""
Servicio de IA MEJORADO: Filtros avanzados por ubicación, zona, tipo, precio y nombre
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_respuesta_ia(mensaje_usuario, restaurantes, ubicacion_usuario=None, contexto=""):
    """
    Versión MEJORADA: Filtros avanzados y manejo inteligente de ubicación
    """
    
    if not restaurantes:
        return "🔍 No tengo restaurantes registrados en este momento. Pronto agregaré más opciones para ti. 😊"

    # Construir información detallada de restaurantes
    restaurantes_info = []
    for r in restaurantes[:12]:  # Mostrar más para mejor contexto
        distancia_texto = f"📍 A {r.get('distancia_km', '?')} km" if r.get('distancia_km') else ""
        
        info = f"""
🍽️ {r.get('nombre', 'Sin nombre')}
• 🏷️ Tipo: {r.get('tipo', 'No especificado')}
• 📍 Zona: {r.get('zona', 'No especificada')}
• 💰 Precio: {r.get('precio', 'No especificado')}
• 📞 Contacto: {r.get('contacto', 'No disponible')}
• 🗺️ Dirección: {r.get('ubicacion', {}).get('direccion', 'No disponible')}
{distancia_texto}
"""
        restaurantes_info.append(info)

    restaurantes_texto = "\n".join(restaurantes_info)

    # Información de contexto mejorada
    info_contexto = f"""
CONTEXTO DE LA CONVERSACIÓN:
{contexto}

UBICACIÓN ACTUAL DEL USUARIO: {'✅ Disponible' if ubicacion_usuario else '❌ No disponible'}

MENSAJE DEL USUARIO: "{mensaje_usuario}"

TOTAL RESTAURANTES FILTRADOS: {len(restaurantes)}
"""

    prompt = f"""
Eres CaliFoodBot, un asistente gastronómico experto en Cali con acceso a base de datos real.

{info_contexto}

INFORMACIÓN DE RESTAURANTES DISPONIBLES (FILTRADOS):
{restaurantes_texto}

INSTRUCCIONES MEJORADAS:

1. **FILTRADO INTELIGENTE**:
   - Si usuario menciona TIPO: pizza, sushi, mexicana, italiana, etc.
   - Si usuario menciona ZONA: norte, sur, centro, granada, etc.
   - Si usuario menciona PRECIO: barato, económico, medio, alto, lujoso
   - Si usuario menciona NOMBRE: buscar coincidencias en nombres
   - SIEMPRE considerar DISTANCIA si hay ubicación

2. **MANEJO DE UBICACIÓN**:
   - Priorizar restaurantes más cercanos
   - Mencionar distancias cuando sean relevantes
   - Si usuario pide "cerca" o "cercano", enfatizar proximidad

3. **ESTRUCTURA DE RESPUESTA**:
   - Saludo contextual
   - Confirmación de filtros aplicados
   - Lista de 3-5 restaurantes más relevantes
   - Información completa: nombre, tipo, zona, precio, contacto, distancia
   - Recomendación específica basada en criterios

4. **CASOS ESPECIALES**:
   - "Actualizar ubicación": Confirmar que se puede enviar nueva ubicación
   - "Restaurantes cerca": Enfocar en proximidad
   - Búsqueda muy específica: Ser preciso en los resultados

5. **TONO**: Útil, preciso y amigable.

EJEMPLOS MEJORADOS:

USUARIO: "Quiero pizza en el norte"
RESPUESTA: "¡Perfecto! Encontré pizzerías en el norte de Cali:

1. 🍕 Pizzería Don Mario - A 0.8km
   📍 Granada · 💰 Alta · 📞 317 111 2233
   🗺️ Granada, Cali

2. 🍕 La Trattoria de Nonna - A 1.2km
   📍 Granada · 💰 Alta · 📞 302 711 0090
   🗺️ Granada, Cali

Te recomiendo Pizzería Don Mario por ser la más cercana."

USUARIO: "Comida barata en el centro"
RESPUESTA: "¡Claro! Opciones económicas en el centro:

1. 🥟 Empanadas El Portal - A 0.3km
   📍 Comida rápida · 💰 Baja · 📞 314 229 6645
   🗺️ Centro, Cali

2. ☕ Café Aroma - A 0.5km
   📍 Cafetería · 💰 Media · 📞 301 456 3322
   🗺️ Centro, Cali

3. 🥤 Juice & Joy - A 0.6km
   📍 Jugos naturales · 💰 Baja · 📞 301 883 2244
   🗺️ Centro, Cali"

USUARIO: "Actualizar mi ubicación"
RESPUESTA: "📍 ¡Por supuesto! Puedes actualizar tu ubicación enviándome tu nueva ubicación usando el clip 📎 en WhatsApp. Así podré recomendarte restaurantes más precisos según tu nueva ubicación."

Ahora responde al usuario de manera útil y precisa:
"""

    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensaje_usuario},
            ],
            temperature=0.2,  # Bajo para más precisión
            max_tokens=700
        )
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Error con OpenAI:", e)
        return generar_respuesta_fallback_mejorada(restaurantes, ubicacion_usuario, contexto)

def generar_respuesta_fallback_mejorada(restaurantes, ubicacion_usuario, contexto):
    """Fallback mejorado cuando OpenAI falla"""
    
    if not restaurantes:
        return "😔 No encontré restaurantes que coincidan con tu búsqueda. ¿Quieres intentar con otros criterios?"
    
    # Ordenar por distancia si hay ubicación
    if ubicacion_usuario:
        restaurantes_ordenados = sorted(restaurantes, 
                                      key=lambda x: x.get('distancia_km', 999))
    else:
        restaurantes_ordenados = restaurantes
    
    respuesta = "🍽️ ¡Encontré estas opciones para ti!\n\n"
    
    for i, r in enumerate(restaurantes_ordenados[:5], 1):
        distancia_texto = f"📍 A {r.get('distancia_km', '?')} km" if r.get('distancia_km') else ""
        emoji_tipo = obtener_emoji_tipo(r.get('tipo', ''))
        
        respuesta += f"""{emoji_tipo} {r.get('nombre', 'Sin nombre')}
   🏷️ {r.get('tipo', 'No especificado')}
   📍 {r.get('zona', 'No especificada')} {distancia_texto}
   💰 {r.get('precio', 'No especificado')}
   📞 {r.get('contacto', 'No disponible')}\n\n"""
    
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