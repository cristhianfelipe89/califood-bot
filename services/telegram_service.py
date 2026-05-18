import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def enviar_mensaje_telegram(chat_id, texto):
    """
    Envía un mensaje de texto a través de la API de Telegram.
    """
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown", # Permite enviar texto en negrita y enlaces funcionales
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Mensaje enviado correctamente a Telegram (Chat ID: {chat_id})")
            return True
        else:
            print(f"❌ Error al enviar mensaje a Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción al enviar mensaje a Telegram: {e}")
        return False