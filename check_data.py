#  check_data.py
from db import get_db

db = get_db()

def verificar_restaurantes():
    restaurantes = list(db.restaurantes.find())
    print(f"📊 Total restaurantes: {len(restaurantes)}")
    
    for r in restaurantes:
        redes = r.get("redes", {})
        ubicacion = r.get("ubicacion", {})
        
        print(f"\n📍 {r.get('nombre')}")
        print(f"   Tipo: {r.get('tipo')}")
        print(f"   Zona: {r.get('zona')}")
        
        # Verificar redes sociales
        print(f"   📱 REDES SOCIALES:")
        print(f"      Facebook: {redes.get('facebook', 'No tiene')}")
        print(f"      Instagram: {redes.get('instagram', 'No tiene')}")
        print(f"      TikTok: {redes.get('tiktok', 'No tiene')}")
        
        # Verificar si tiene al menos una red social
        tiene_redes = any(redes.get(red) for red in ['facebook', 'instagram', 'tiktok'])
        print(f"   ✅ Tiene redes sociales: {tiene_redes}")
        
        # Verificar ubicación
        longitud = ubicacion.get("lng") or ubicacion.get("lon")
        print(f"   🗺️ Ubicación: {ubicacion.get('direccion', 'No disponible')}")
        print(f"      Lat: {ubicacion.get('lat')}, Lng: {longitud}")

def verificar_estructura_redes():
    """Verifica específicamente la estructura de las redes sociales"""
    restaurantes = list(db.restaurantes.find())
    
    print(f"\n🔍 VERIFICACIÓN ESTRUCTURA REDES SOCIALES")
    print("=" * 50)
    
    for r in restaurantes:
        nombre = r.get('nombre')
        redes = r.get("redes", {})
        
        print(f"\n🍽️ {nombre}")
        print(f"   Tipo objeto 'redes': {type(redes)}")
        print(f"   Contenido 'redes': {redes}")
        
        # Verificar cada red individualmente
        for red_nombre in ['facebook', 'instagram', 'tiktok']:
            red_url = redes.get(red_nombre)
            print(f"   {red_nombre.upper()}: '{red_url}' (tipo: {type(red_url)})")
            
            # Verificar si es un string válido
            if red_url:
                es_valido = isinstance(red_url, str) and red_url.startswith('http')
                print(f"      ✅ Válido: {es_valido}")
            else:
                print(f"      ❌ No tiene o es inválido")

def contar_redes_sociales():
    """Cuenta cuántos restaurantes tienen cada tipo de red social"""
    restaurantes = list(db.restaurantes.find())
    
    stats = {
        'total_restaurantes': len(restaurantes),
        'con_facebook': 0,
        'con_instagram': 0,
        'con_tiktok': 0,
        'con_almenos_una_red': 0,
        'sin_redes': 0
    }
    
    for r in restaurantes:
        redes = r.get("redes", {})
        
        tiene_facebook = bool(redes.get('facebook'))
        tiene_instagram = bool(redes.get('instagram'))
        tiene_tiktok = bool(redes.get('tiktok'))
        tiene_almenos_una = tiene_facebook or tiene_instagram or tiene_tiktok
        
        if tiene_facebook: stats['con_facebook'] += 1
        if tiene_instagram: stats['con_instagram'] += 1
        if tiene_tiktok: stats['con_tiktok'] += 1
        if tiene_almenos_una: 
            stats['con_almenos_una_red'] += 1
        else:
            stats['sin_redes'] += 1
    
    print(f"\n📈 ESTADÍSTICAS DE REDES SOCIALES")
    print("=" * 40)
    print(f"Total restaurantes: {stats['total_restaurantes']}")
    print(f"Con Facebook: {stats['con_facebook']}")
    print(f"Con Instagram: {stats['con_instagram']}")
    print(f"Con TikTok: {stats['con_tiktok']}")
    print(f"Con al menos una red: {stats['con_almenos_una_red']}")
    print(f"Sin redes sociales: {stats['sin_redes']}")

if __name__ == "__main__":
    print("🔍 INICIANDO VERIFICACIÓN DE DATOS")
    print("=" * 50)
    
    # Ejecutar todas las verificaciones
    verificar_restaurantes()
    verificar_estructura_redes()
    contar_redes_sociales()
    
    print(f"\n✅ Verificación completada")