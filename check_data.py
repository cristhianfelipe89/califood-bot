# check_data.py
from db import get_db

db = get_db()

def verificar_restaurantes():
    restaurantes = list(db.restaurantes.find())
    print(f"📊 Total restaurantes: {len(restaurantes)}")
    
    for r in restaurantes:
        ubicacion = r.get("ubicacion", {})
        # Usar la misma lógica flexible que el modelo
        longitud = ubicacion.get("lng") or ubicacion.get("lon")
        
        print(f"\n📍 {r.get('nombre')}")
        print(f"   Tipo: {r.get('tipo')}")
        print(f"   Ubicación: {ubicacion}")
        print(f"   Tiene lat/lng: {'lat' in ubicacion and longitud is not None}")
        print(f"   Lat: {ubicacion.get('lat')}, Lng: {longitud}")

if __name__ == "__main__":
    verificar_restaurantes()