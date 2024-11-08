
from flask import Flask
from .controllers.routes import main

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    # Registra los blueprints
    app.register_blueprint(main)
    app.register_blueprint(mercado_libre_bp)
    app.register_blueprint(celesa_bp)
    app.register_blueprint(configuracion_bp)
    return app
