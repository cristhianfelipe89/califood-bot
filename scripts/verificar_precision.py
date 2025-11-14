# scripts/verificar_precision.py
"""
Script para verificar la precisión de las coordenadas y distancias
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.restaurante_service import listar_restaurantes
from services.ubicacion_service import obtener_ubicacion
from services.ia_service import calcular_distancias_reales
from geopy.distance import geodesic

def verificar_precision_coordenadas(usuario_id="573185963855"):
    """Verifica la precisión de las coordenadas guardadas"""
    
    # Obtener ubicación del usuario
    ubicacion_usuario = obtener_ubicacion(usuario_id)
    
    if not ubicacion_usuario:
        print("❌ El usuario no tiene ubicación guardada")
        return
    
    print("🎯 VERIFICACIÓN DE PRECISIÓN DE COORDENADAS")
    print(f"📍 Ubicación guardada del usuario:")
    print(f"   Latitud: {ubicacion_usuario['lat']}") 
    print(f"   Longitud: {ubicacion_usuario['lon']}")
    print(f"   (6 decimales ≈ 0.1 m de precisión)")
    print()
    
    restaurantes = listar_restaurantes()
    
    print("🔍 VERIFICANDO COORDENADAS DE RESTAURANTES:")
    problemas = []
    for r in restaurantes[:10]:  # Revisar solo los primeros 10
        ubic = r.get('ubicacion', {})
        lat = ubic.get('lat')
        lon = ubic.get('lng') or ubic.get('lon')
        
        if lat and lon:
            # Verificar precisión de coordenadas
            if isinstance(lat, float) and isinstance(lon, float):
                decimales_lat = len(str(lat).split('.')[1]) if '.' in str(lat) else 0
                decimales_lon = len(str(lon).split('.')[1]) if '.' in str(lon) else 0
                
                if decimales_lat < 4 or decimales_lon < 4:
                    problemas.append(f"⚠️ {r['nombre']}: Pocos decimales (lat:{decimales_lat}, lon:{decimales_lon})")
            else:
                problemas.append(f"❌ {r['nombre']}: Coordenadas no son números")
        else:
            problemas.append(f"❌ {r['nombre']}: Sin coordenadas")
    
    if problemas:
        print("📋 PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   {problema}")
    else:
        print("✅ Todas las coordenadas tienen buena precisión")
    
    return problemas

def comparar_distancias(usuario_id="573185963855"):
    """Compara distancias calculadas vs Google Maps"""
    
    ubicacion_usuario = obtener_ubicacion(usuario_id)
    if not ubicacion_usuario:
        return
    
    print("\n📏 COMPARACIÓN DE DISTANCIAS:")
    print(f"📍 Desde: {ubicacion_usuario['lat']:.6f}, {ubicacion_usuario['lon']:.6f}")
    print()
    
    restaurantes = listar_restaurantes()
    restaurantes_con_distancias = calcular_distancias_reales(restaurantes, ubicacion_usuario)
    
    for i, r in enumerate(restaurantes_con_distancias[:5], 1):
        distancia = r.get('distancia_real_km')
        ubic = r.get('ubicacion', {})
        lat_rest = ubic.get('lat')
        lon_rest = ubic.get('lng') or ubic.get('lon')
        
        if distancia and lat_rest and lon_rest:
            # Generar enlace de Google Maps para verificación
            enlace_maps = f"https://www.google.com/maps/dir/{ubicacion_usuario['lat']},{ubicacion_usuario['lon']}/{lat_rest},{lon_rest}"
            
            print(f"{i}. {r['nombre']}")
            print(f"   📍 Coordenadas: {lat_rest:.6f}, {lon_rest:.6f}")
            print(f"   📏 Distancia calculada: {distancia:.3f} km")
            print(f"   🔗 Verificar en Maps: {enlace_maps}")
            print()

if __name__ == "__main__":
    usuario = input("ID de usuario (default: 573185963855): ").strip() or "573185963855"
    verificar_precision_coordenadas(usuario)
    comparar_distancias(usuario)