# services/whatsapp_service.py
"""
Servicio para enviar mensajes por WhatsApp usando la API de Meta.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def enviar_mensaje(numero, texto):
    """
    Envía un mensaje de texto a través de la API de WhatsApp Cloud.
    """
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ No se encontró configuración de WhatsApp en .env")
        return

    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 200:
            print(f"✅ Mensaje enviado correctamente a: {numero}")
        else:
            print(f"❌ Error al enviar mensaje ({r.status_code}): {r.text}")
    except Exception as e:
        print("❌ Excepción al enviar mensaje:", e)
