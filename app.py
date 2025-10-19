from flask import Flask, request
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# 🔹 Cargar variables de entorno (.env)
load_dotenv()

# Inicializar Flask y OpenAI
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔹 Credenciales de WhatsApp Cloud API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

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

            # Generar respuesta con GPT
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
