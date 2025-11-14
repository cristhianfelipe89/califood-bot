# scripts/verificar_permisos.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def verificar_permisos_app():
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    
    if not token:
        print("❌ WHATSAPP_TOKEN no encontrado")
        return
    
    # Verificar permisos de la app
    url = f"https://graph.facebook.com/v18.0/me/permissions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"🔐 Estado de la solicitud: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Permisos de la aplicación:")
            for perm in data.get('data', []):
                print(f"   • {perm['permission']}: {perm['status']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")

def verificar_configuracion_numero():
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    
    if not token or not phone_number_id:
        print("❌ Faltan configuraciones en .env")
        return
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n📱 Estado del número: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Configuración del número:")
            print(f"   • Número: {data.get('display_phone_number')}")
            print(f"   • ID: {data.get('id')}")
            print(f"   • Calidad: {data.get('quality_rating')}")
            print(f"   • Estado: {data.get('verified_name')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")

if __name__ == "__main__":
    print("🔍 Verificando configuración de WhatsApp Business API...")
    verificar_permisos_app()
    verificar_configuracion_numero()