from flask import Flask, request
import requests
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------------
# 🔹 Cargar variables de entorno (.env)
# ---------------------------------------------------
load_dotenv()

# Inicializar Flask y OpenAI
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔹 Credenciales de WhatsApp Cloud API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ---------------------------------------------------
# 🔹 Cargar base de datos local (.csv)
# ---------------------------------------------------
DATA_PATH = "./datos/sitios.csv"
try:
    sitios_df = pd.read_csv(DATA_PATH)
    print("✅ Base de datos cargada con éxito.")
except Exception as e:
    print("❌ Error cargando el archivo CSV:", e)
    sitios_df = pd.DataFrame()  # DataFrame vacío por seguridad

# ---------------------------------------------------
# 🔸 Función para enviar mensaje por WhatsApp
# ---------------------------------------------------
def enviar_mensaje_whatsapp(numero, mensaje):
    try:
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensaje}
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("✅ Mensaje enviado correctamente a:", numero)
    except Exception as e:
        print("❌ Error enviando mensaje:", e)

# ---------------------------------------------------
# 🔸 Función para buscar sitios en el CSV
# ---------------------------------------------------
def buscar_sitios(usuario_input):
    """Busca lugares que coincidan con el tipo o zona mencionada por el usuario."""
    if sitios_df.empty:
        return None

    input_lower = usuario_input.lower()

    # Filtrar por coincidencias de palabras clave en tipo o zona
    resultados = sitios_df[
        sitios_df.apply(
            lambda fila: any(
                palabra in str(fila["tipo"]).lower() or palabra in str(fila["zona"]).lower()
                for palabra in input_lower.split()
            ),
            axis=1
        )
    ]

    if resultados.empty:
        return None

    # Tomar los primeros 5 resultados
    respuesta = "🍽️ Te recomiendo estos lugares:\n\n"
    for _, fila in resultados.head(5).iterrows():
        respuesta += (
            f"📍 *{fila['nombre']}*\n"
            f"Tipo: {fila['tipo']}\n"
            f"Zona: {fila['zona']}\n"
            f"Precio: {fila['precio']}\n"
            f"📞 {fila['contacto']}\n"
            f"📘 {fila['facebook']}\n"
            f"📸 {fila['instagram']}\n"
            f"🎵 {fila['tiktok']}\n\n"
        )
    return respuesta.strip()

# ---------------------------------------------------
# 🔸 Función para generar respuesta con OpenAI GPT
# ---------------------------------------------------
def generar_respuesta_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un agente conversacional especializado en gastronomía "
                        "y emprendimientos de comida en Cali. "
                        "Recomienda lugares, precios, zonas y redes sociales de negocios locales."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error con OpenAI:", e)
        return "Lo siento, tuve un error al generar la respuesta. Inténtalo más tarde."

# ---------------------------------------------------
# 🔸 Endpoint de verificación de Meta (GET)
# ---------------------------------------------------
@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente.")
        return challenge
    else:
        return "Token inválido", 403

# ---------------------------------------------------
# 🔸 Endpoint para recibir mensajes (POST)
# ---------------------------------------------------
@app.route("/webhook", methods=["POST"])
def recibir_mensajes():
    data = request.get_json()
    print("📩 Evento recibido:", data)

    try:
        mensajes = data["entry"][0]["changes"][0]["value"].get("messages", [])
        if mensajes:
            mensaje = mensajes[0]
            numero = mensaje["from"]
            texto_usuario = mensaje["text"]["body"]

            print(f"📥 Mensaje de {numero}: {texto_usuario}")

            # Buscar primero en el CSV
            respuesta_csv = buscar_sitios(texto_usuario)

            if respuesta_csv:
                respuesta = respuesta_csv
            else:
                # Si no hay coincidencias, usar GPT
                respuesta = generar_respuesta_gpt(texto_usuario)

            # Enviar respuesta por WhatsApp
            enviar_mensaje_whatsapp(numero, respuesta)

    except Exception as e:
        print("❌ Error procesando el mensaje:", e)

    return "EVENT_RECEIVED", 200

# ---------------------------------------------------
# 🔸 Iniciar servidor Flask
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
