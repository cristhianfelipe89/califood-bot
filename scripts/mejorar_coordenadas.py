# scripts/mejorar_coordenadas.py
"""
Script para mejorar la precisión de las coordenadas en la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db

def verificar_y_mejorar_coordenadas():
    """Verifica y mejora la precisión de las coordenadas"""
    db = get_db()
    
    # Coordenadas mejoradas con más decimales
    coordenadas_mejoradas = {
        "Choripán de Juanelo": {
            "lat": 3.461099,
            "lng": -76.529898
        },
        "Hamburguesas Don Pepe": {
            "lat": 3.426000, 
            "lng": -76.489000
        },
        "Arepísima Gourmet": {
            "lat": 3.353000,
            "lng": -76.532000
        },
        "La Cazuela de Doña Lucha": {
            "lat": 3.451000,
            "lng": -76.534000
        },
        "Bambú Sushi Bar": {
            "lat": 3.468000,
            "lng": -76.523000
        },
        "El Rincón Mexa": {
            "lat": 3.358000,
            "lng": -76.532000
        },
        "La Pizzería del Parque": {
            "lat": 3.442000,
            "lng": -76.560000
        },
        "Postres Anita": {
            "lat": 3.469000,
            "lng": -76.520000
        },
        "Café Aroma": {
            "lat": 3.448000,
            "lng": -76.532000
        },
        "Papas & Salsa": {
            "lat": 3.350000,
            "lng": -76.535000
        },
        "Pekín Wok": {
            "lat": 3.468000,
            "lng": -76.520000
        },
        "Empanadas El Portal": {
            "lat": 3.449000,
            "lng": -76.533000
        },
        "Green Bowl": {
            "lat": 3.441000,
            "lng": -76.561000
        },
        "Juice & Joy": {
            "lat": 3.448000,
            "lng": -76.534000
        },
        "La Trattoria de Nonna": {
            "lat": 3.467000,
            "lng": -76.520000
        },
        "Tamalitos del Valle": {
            "lat": 3.430000,
            "lng": -76.490000
        },
        "Taquitos & Más": {
            "lat": 3.442000,
            "lng": -76.560000
        },
        "ChocoLatte House": {
            "lat": 3.353000,
            "lng": -76.533000
        },
        "Postres La Dulzura": {
            "lat": 3.440000,
            "lng": -76.561000
        },
        "Café La Sucursal": {
            "lat": 3.448000,
            "lng": -76.533000
        },
        "Pizzería Don Mario": {
            "lat": 3.469000,
            "lng": -76.523000
        }
    }
    
    actualizados = 0
    for nombre, coordenadas in coordenadas_mejoradas.items():
        result = db.restaurantes.update_one(
            {"nombre": nombre},
            {"$set": {
                "ubicacion.lat": coordenadas["lat"],
                "ubicacion.lng": coordenadas["lng"],
                "ubicacion.mapa_url": f"https://www.google.com/maps?q={coordenadas['lat']},{coordenadas['lng']}"
            }}
        )
        
        if result.modified_count > 0:
            print(f"✅ Actualizado: {nombre}")
            print(f"   📍 {coordenadas['lat']:.6f}, {coordenadas['lng']:.6f}")
            actualizados += 1
        else:
            print(f"⚠️ No encontrado: {nombre}")
    
    print(f"\n🎯 Total restaurantes actualizados: {actualizados}")

if __name__ == "__main__":
    print("🔄 Mejorando precisión de coordenadas...")
    verificar_y_mejorar_coordenadas()