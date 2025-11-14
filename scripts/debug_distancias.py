# scripts/debug_distancias.py
"""
Script para debuggear el cálculo de distancias con ubicación REAL del usuario
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.restaurante_service import listar_restaurantes
from services.ia_service import calcular_distancias_reales, formatear_distancia
from services.ubicacion_service import obtener_ubicacion

def debug_distancias_usuario(usuario_id="573057134568"):
    """Debug usando la ubicación REAL de un usuario"""
    
    # Obtener ubicación guardada del usuario
    ubicacion_usuario = obtener_ubicacion(usuario_id)
    
    if not ubicacion_usuario:
        print("❌ El usuario no tiene ubicación guardada")
        print("💡 Envía una ubicación por WhatsApp primero")
        return
    
    print(f"📍 Ubicación REAL del usuario {usuario_id}: {ubicacion_usuario}")
    print("\n🔍 Calculando distancias desde esta ubicación...\n")
    
    restaurantes = listar_restaurantes()
    print(f"📊 Total restaurantes: {len(restaurantes)}")
    
    # Verificar coordenadas de restaurantes
    restaurantes_con_coordenadas = []
    for r in restaurantes:
        ubic = r.get('ubicacion', {})
        if ubic.get('lat') and (ubic.get('lng') or ubic.get('lon')):
            restaurantes_con_coordenadas.append(r)
    
    print(f"📍 Restaurantes con coordenadas: {len(restaurantes_con_coordenadas)}")
    
    # Calcular distancias desde la ubicación REAL del usuario
    restaurantes_con_distancias = calcular_distancias_reales(restaurantes_con_coordenadas, ubicacion_usuario)
    
    print(f"\n📏 DISTANCIAS DESDE TU UBICACIÓN ACTUAL:\n")
    for i, r in enumerate(restaurantes_con_distancias[:15], 1):
        distancia = r.get('distancia_real_km')
        distancia_formateada = formatear_distancia(distancia) if distancia is not None else "Sin calcular"
        
        print(f"{i}. {r['nombre']}")
        print(f"   📍 {r['zona']} - {r['tipo']}")
        print(f"   🗺️ Coordenadas restaurante: {r['ubicacion'].get('lat')}, {r['ubicacion'].get('lng')}")
        print(f"   📏 Distancia desde TI: {distancia_formateada} ({distancia} km)")
        print(f"   🏷️ Etiquetas: {r.get('subtipo', [])}")
        print()

def debug_distancias_personalizada(lat, lon):
    """Debug con una ubicación personalizada"""
    ubicacion_personalizada = {"lat": lat, "lon": lon}
    
    print(f"📍 Ubicación personalizada: {ubicacion_personalizada}")
    print("\n🔍 Calculando distancias...\n")
    
    restaurantes = listar_restaurantes()
    restaurantes_con_distancias = calcular_distancias_reales(restaurantes, ubicacion_personalizada)
    
    print(f"📏 TOP 10 RESTAURANTES MÁS CERCANOS:\n")
    for i, r in enumerate(restaurantes_con_distancias[:10], 1):
        distancia = r.get('distancia_real_km')
        distancia_formateada = formatear_distancia(distancia) if distancia is not None else "Sin calcular"
        
        print(f"{i}. {r['nombre']} - {distancia_formateada}")
        print(f"   {r['tipo']} · {r['zona']} · {r['precio']}")

if __name__ == "__main__":
    print("🔍 DEBUG DE DISTANCIAS")
    print("1. Con ubicación de usuario guardada")
    print("2. Con ubicación personalizada")
    
    opcion = input("Selecciona opción (1/2): ").strip()
    
    if opcion == "1":
        usuario = input("ID de usuario (default: 573057134568): ").strip() or "573057134568"
        debug_distancias_usuario(usuario)
    elif opcion == "2":
        try:
            lat = float(input("Latitud (ej: 3.4516): "))
            lon = float(input("Longitud (ej: -76.5320): "))
            debug_distancias_personalizada(lat, lon)
        except ValueError:
            print("❌ Coordenadas inválidas")
    else:
        print("❌ Opción inválida")