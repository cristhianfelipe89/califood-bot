# scripts/actualizar_todo.py
"""
Script para actualizar TODO: etiquetas, URLs de mapa y verificar coordenadas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db

def verificar_coordenadas_restaurantes():
    """Verifica que todos los restaurantes tengan coordenadas válidas"""
    db = get_db()
    
    restaurantes = list(db.restaurantes.find())
    problemas = []
    
    for r in restaurantes:
        ubicacion = r.get("ubicacion", {})
        lat = ubicacion.get("lat")
        lon = ubicacion.get("lng") or ubicacion.get("lon")
        
        if not lat or not lon:
            problemas.append(f"❌ {r['nombre']}: Sin coordenadas")
        elif not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            problemas.append(f"⚠️ {r['nombre']}: Coordenadas inválidas ({lat}, {lon})")
    
    if problemas:
        print("\n🔍 PROBLEMAS CON COORDENADAS:")
        for problema in problemas:
            print(problema)
    else:
        print("✅ Todas las coordenadas son válidas")
    
    return len(problemas)

def actualizar_etiquetas_restaurantes():
    db = get_db()
    
    actualizaciones = [
        {
            "nombre": "Arepísima Gourmet",
            "subtipo": ["arepas", "comida rápida", "venezolana"]
        },
        {
            "nombre": "Hamburguesas Don Pepe", 
            "subtipo": ["hamburguesas", "comida rápida", "hamburgues", "burger"]
        },
        {
            "nombre": "Papas & Salsa",
            "subtipo": ["papas", "comida rápida", "snacks", "aperitivos"]
        },
        {
            "nombre": "Empanadas El Portal",
            "subtipo": ["empanadas", "comida rápida", "frituras", "snacks"]
        },
        {
            "nombre": "Choripán de Juanelo",
            "subtipo": ["choripán", "choripan", "chori", "comida rápida", "parrilla", "sándwiches"]
        },
        {
            "nombre": "La Pizzería del Parque",
            "subtipo": ["pizza", "comida italiana", "pizzas", "masa"]
        },
        {
            "nombre": "La Trattoria de Nonna", 
            "subtipo": ["pasta", "comida italiana", "lasaña", "espagueti", "pizza"]
        },
        {
            "nombre": "Pizzería Don Mario",
            "subtipo": ["pizza", "comida italiana", "pizzas", "masa"]
        },
        {
            "nombre": "El Rincón Mexa",
            "subtipo": ["tacos", "comida mexicana", "burritos", "mexicana", "picante"]
        },
        {
            "nombre": "Taquitos & Más",
            "subtipo": ["tacos", "comida mexicana", "taquitos", "mexicana"]
        },
        {
            "nombre": "Bambú Sushi Bar",
            "subtipo": ["sushi", "comida japonesa", "sashimi", "rolls", "japonesa"]
        },
        {
            "nombre": "Pekín Wok", 
            "subtipo": ["comida china", "arroz chino", "chop suey", "wok", "china"]
        },
        {
            "nombre": "La Cazuela de Doña Lucha",
            "subtipo": ["comida típica", "valluna", "sancocho", "bandeja paisa", "tradicional"]
        },
        {
            "nombre": "Tamalitos del Valle",
            "subtipo": ["tamales", "comida típica", "valluna", "tradicional"]
        },
        {
            "nombre": "Postres Anita",
            "subtipo": ["postres", "dulces", "helados", "repostería", "postre"]
        },
        {
            "nombre": "ChocoLatte House",
            "subtipo": ["café", "postres", "chocolate", "capuchino", "cafetería"]
        },
        {
            "nombre": "Café Aroma",
            "subtipo": ["café", "cafetería", "capuchino", "té", "desayunos"]
        },
        {
            "nombre": "Postres La Dulzura",
            "subtipo": ["postres", "dulces", "tortas", "repostería", "postre"]
        },
        {
            "nombre": "Café La Sucursal", 
            "subtipo": ["café", "cafetería", "capuchino", "té", "desayunos"]
        },
        {
            "nombre": "Green Bowl",
            "subtipo": ["comida saludable", "ensaladas", "bowls", "saludable", "fit"]
        },
        {
            "nombre": "Juice & Joy",
            "subtipo": ["jugos", "jugos naturales", "batidos", "saludable", "zumo"]
        }
    ]
    
    etiquetas_actualizadas = 0
    for actualizacion in actualizaciones:
        result = db.restaurantes.update_one(
            {"nombre": actualizacion["nombre"]},
            {"$set": {"subtipo": actualizacion["subtipo"]}}
        )
        if result.modified_count > 0:
            print(f"✅ Etiquetas: {actualizacion['nombre']}")
            etiquetas_actualizadas += 1
        else:
            print(f"⚠️ No encontrado: {actualizacion['nombre']}")
    
    return etiquetas_actualizadas

def actualizar_urls_mapa_restaurantes():
    db = get_db()
    
    restaurantes = list(db.restaurantes.find())
    urls_actualizadas = 0
    
    for restaurante in restaurantes:
        ubicacion = restaurante.get("ubicacion", {})
        lat = ubicacion.get("lat")
        lon = ubicacion.get("lng") or ubicacion.get("lon")
        
        if lat and lon:
            mapa_url = f"https://www.google.com/maps?q={lat},{lon}"
            
            result = db.restaurantes.update_one(
                {"_id": restaurante["_id"]},
                {"$set": {"ubicacion.mapa_url": mapa_url}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Mapa: {restaurante['nombre']}")
                urls_actualizadas += 1
    
    return urls_actualizadas

def main():
    print("🔄 Iniciando actualización completa...")
    
    print("\n🔍 Verificando coordenadas...")
    problemas = verificar_coordenadas_restaurantes()
    
    print("\n📝 Actualizando etiquetas...")
    etiquetas_count = actualizar_etiquetas_restaurantes()
    
    print("\n🗺️ Actualizando URLs de mapa...")
    urls_count = actualizar_urls_mapa_restaurantes()
    
    print(f"\n🎉 ACTUALIZACIÓN COMPLETADA:")
    print(f"   • Problemas de coordenadas: {problemas}")
    print(f"   • Etiquetas actualizadas: {etiquetas_count}")
    print(f"   • URLs de mapa actualizadas: {urls_count}")
    
    if problemas == 0:
        print(f"\n🚀 El sistema está listo para usar con ubicaciones y etiquetas!")
        print("💡 Ejecuta: python scripts/debug_distancias.py para verificar distancias")
    else:
        print(f"\n⚠️ Hay {problemas} problemas con las coordenadas. Revisa la base de datos.")

if __name__ == "__main__":
    main()