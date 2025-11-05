# services/ia_service.py
"""
Servicio de IA: interpreta los gustos del usuario y genera respuestas naturales
solo con restaurantes existentes en la base de datos.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generar_respuesta_ia(mensaje_usuario, restaurantes):
    """
    Interpreta lo que el usuario desea comer y construye una respuesta amable
    con los restaurantes disponibles que coincidan.
    """

    if not restaurantes:
        return "No tengo restaurantes registrados por ahora, pero pronto agregaré más opciones. 😊"

    # Nombres disponibles en la BD
    nombres = [r["nombre"] for r in restaurantes]

    # Prompt con instrucciones
    prompt = (
        "Eres un asistente gastronómico llamado CaliFoodBot, experto en recomendar comida en Cali. "
        "El usuario te dirá qué quiere comer. "
        "Tu tarea es buscar coincidencias solo entre los siguientes restaurantes:\n"
        f"{', '.join(nombres)}.\n\n"
        "Usa el siguiente formato para responder:\n\n"
        "📍 [nombre del restaurante]\n"
        "Zona: [zona o barrio]\n"
        "💰 Precio: [rango de precio]\n"
        "📞 Contacto: [número de contacto]\n\n"
        "📱 Síguenos:\n"
        "🔹 Facebook\n"
        "📸 Instagram\n"
        "🎵 TikTok\n\n"
        "🗺️ [enlace de Google Maps]\n\n"
        "Si hay varios, muestra hasta 3 opciones, separadas con una línea en blanco. "
        "Habla de forma cálida y natural, como un amigo que conoce bien la ciudad."
    )

    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": mensaje_usuario},
            ],
            temperature=0.7
        )
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Error con OpenAI:", e)
        return "Lo siento, no pude generar una respuesta en este momento."


