import os
import sys
import json
from bson import ObjectId

# 🔧 Asegura que Python pueda encontrar db.py (en la raíz del proyecto)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from db import get_db  # ahora sí lo encontrará correctamente

# Conexión a la base
db = get_db()

# Cargar restaurantes existentes
restaurantes = list(db.restaurantes.find())

# Definir platos base por tipo
plantillas = {
    "comida rápida": [
        {"nombre": "Hamburguesa clásica", "precio": 16000},
        {"nombre": "Perro caliente especial", "precio": 12000}
    ],
    "comida típica": [
        {"nombre": "Sancocho valluno", "precio": 20000},
        {"nombre": "Chuleta valluna", "precio": 18000}
    ],
    "comida japonesa": [
        {"nombre": "Sushi roll tempura", "precio": 28000},
        {"nombre": "Sashimi de atún", "precio": 26000}
    ],
    "comida mexicana": [
        {"nombre": "Tacos al pastor", "precio": 16000},
        {"nombre": "Burrito mixto", "precio": 18000}
    ],
    "comida italiana": [
        {"nombre": "Pizza margarita", "precio": 20000},
        {"nombre": "Lasaña boloñesa", "precio": 22000}
    ],
    "postres": [
        {"nombre": "Cheesecake", "precio": 10000},
        {"nombre": "Brownie con helado", "precio": 9000}
    ],
    "cafetería": [
        {"nombre": "Capuchino", "precio": 7000},
        {"nombre": "Tinto campesino", "precio": 3000}
    ],
    "comida china": [
        {"nombre": "Arroz chino especial", "precio": 15000},
        {"nombre": "Pollo agridulce", "precio": 17000}
    ],
    "comida saludable": [
        {"nombre": "Ensalada César", "precio": 16000},
        {"nombre": "Wrap de pollo", "precio": 15000}
    ],
    "jugos naturales": [
        {"nombre": "Jugo de mango biche", "precio": 6000},
        {"nombre": "Jugo de maracuyá", "precio": 6000}
    ]
}

menus = []

for r in restaurantes:
    tipo = r.get("tipo", "").strip().lower()
    base_platos = plantillas.get(tipo, [{"nombre": "Plato del día", "precio": 12000}])

    for plato in base_platos:
        menus.append({
            "nombre": plato["nombre"],
            "precio": plato["precio"],
            "categoria": tipo.title(),
            "restaurant_id": {"$oid": str(r["_id"])}
        })

# Guardar en JSON
with open("menus.json", "w", encoding="utf-8") as f:
    json.dump(menus, f, ensure_ascii=False, indent=2)

print(f"✅ Generado menus.json con {len(menus)} platos.")
