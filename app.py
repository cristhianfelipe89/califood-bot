from flask import Flask
from routes.restaurante_routes import restaurante_bp
from routes.menu_routes import menu_bp
from routes.pedido_routes import pedido_bp
from waitress import serve  #se importa waitress para evitar error al reload    
from routes.webhook_routes import webhook_bp
from services.whatsapp_service import enviar_mensaje
from routes.conversacion_routes import conversacion_bp
from routes.ubicacion_routes import ubicacion_bp



app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(restaurante_bp, url_prefix="/api/restaurantes")
app.register_blueprint(menu_bp, url_prefix="/api/menus")
app.register_blueprint(pedido_bp, url_prefix="/api/pedidos")
app.register_blueprint(webhook_bp)
app.register_blueprint(conversacion_bp)
app.register_blueprint(ubicacion_bp)

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    print("🚀 Servidor iniciando con Waitress en http://localhost:5000")
    serve(app, host="127.0.0.1", port=5000)
