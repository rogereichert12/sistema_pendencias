from flask import Flask
from app.routes.auth_routes import auth_blueprint
from app.routes.dashboard_routes import dashboard_blueprint
from app.routes.cliente_routes import cliente_blueprint
from app.routes.export_routes import export_blueprint
from app.routes.pendencias_routes import pendencias_blueprint  # Certifique-se de importar isso
from app.routes.produtos_routes import produtos_blueprint
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registra os Blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(cliente_blueprint, url_prefix="/clientes")
    app.register_blueprint(export_blueprint, url_prefix="/clientes/export")
    app.register_blueprint(pendencias_blueprint, url_prefix="/pendencias")  # Registra a blueprint de pendências
    app.register_blueprint(produtos_blueprint, url_prefix="/produtos")

    return app
