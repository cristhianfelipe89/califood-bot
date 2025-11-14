"""
Servicio para manejar operaciones CRUD de restaurantes.
"""
from db import get_db
from bson import ObjectId
from models.restaurante_model import restaurante_schema

db = get_db()

def crear_restaurante(data):
    # Asegurar estructura correcta de ubicación
    if "ubicacion" not in data:
        data["ubicacion"] = {}
    if "redes" not in data:
        data["redes"] = {}
    
    result = db["restaurantes"].insert_one(data)
    data["_id"] = str(result.inserted_id)
    return restaurante_schema(data)

def listar_restaurantes():
    restaurantes = list(db["restaurantes"].find())
    return [restaurante_schema(r) for r in restaurantes]

def obtener_restaurante_por_id(restaurante_id):
    try:
        restaurante = db["restaurantes"].find_one({"_id": ObjectId(restaurante_id)})
        return restaurante_schema(restaurante) if restaurante else None
    except:
        return None

def buscar_restaurante_por_nombre(nombre):
    restaurante = db["restaurantes"].find_one({"nombre": {"$regex": nombre, "$options": "i"}})
    return restaurante_schema(restaurante) if restaurante else None
# services/restaurante_service.py (AGREGAR FUNCIÓN)

# services/restaurante_service.py (AGREGAR ESTA FUNCIÓN)
def obtener_restaurantes_cercanos(ubicacion_usuario, limite=5, radio_km=5.0):
    """
    Obtiene restaurantes cercanos a una ubicación específica
    """
    from geopy.distance import geodesic
    
    todos_restaurantes = listar_restaurantes()
    restaurantes_con_distancia = []
    
    for r in todos_restaurantes:
        ubic_rest = r.get("ubicacion", {})
        lat_rest = ubic_rest.get("lat")
        lon_rest = ubic_rest.get("lng") or ubic_rest.get("lon")
        
        if lat_rest and lon_rest:
            try:
                distancia = geodesic(
                    (ubicacion_usuario["lat"], ubicacion_usuario["lon"]),
                    (lat_rest, lon_rest)
                ).km
                
                if distancia <= radio_km:
                    r["distancia_km"] = round(distancia, 2)
                    restaurantes_con_distancia.append(r)
            except Exception as e:
                print(f"❌ Error calculando distancia: {e}")
    
    # Ordenar por distancia y limitar resultados
    restaurantes_ordenados = sorted(restaurantes_con_distancia, 
                                  key=lambda x: x.get("distancia_km", 999))
    
    return restaurantes_ordenados[:limite]
    