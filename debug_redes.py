# debug_redes.py
from services.restaurante_service import listar_restaurantes

def verificar_redes_en_servicio():
    print("🔍 VERIFICANDO REDES EN SERVICIO DE RESTAURANTES")
    print("=" * 50)
    
    restaurantes = listar_restaurantes()
    
    for i, r in enumerate(restaurantes[:21]):  # Solo primeros 3 para prueba
        print(f"\n{i+1}. {r.get('nombre')}")
        print(f"   Redes objeto: {r.get('redes')}")
        print(f"   Tipo: {type(r.get('redes'))}")
        print(f"   Facebook: {r.get('redes', {}).get('facebook')}")
        print(f"   Instagram: {r.get('redes', {}).get('instagram')}")
        print(f"   TikTok: {r.get('redes', {}).get('tiktok')}")

if __name__ == "__main__":
    verificar_redes_en_servicio()