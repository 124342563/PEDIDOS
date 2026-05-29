import os
from datetime import datetime
from flask import Flask
from .extensions import db, migrate
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure required folders exist
    for folder_key in ["UPLOAD_FOLDER", "EXPORT_FOLDER", "REMISIONES_FOLDER", "BACKUP_FOLDER", "LOG_FOLDER"]:
        folder = app.config.get(folder_key)
        if folder:
            os.makedirs(folder, exist_ok=True)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes.dashboard import bp as dashboard_bp
    from .routes.clientes import bp as clientes_bp
    from .routes.colaboradores import bp as colaboradores_bp
    from .routes.pedidos import bp as pedidos_bp
    from .routes.entregas import bp as entregas_bp
    from .routes.despachos import bp as despachos_bp
    from .routes.remisiones import bp as remisiones_bp
    from .routes.exportaciones import bp as exportaciones_bp
    from .routes.notificaciones import bp as notificaciones_bp
    from .routes.tracking import bp as tracking_bp
    from .routes.integraciones import bp as integraciones_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp, url_prefix="/clientes")
    app.register_blueprint(colaboradores_bp, url_prefix="/colaboradores")
    app.register_blueprint(pedidos_bp, url_prefix="/pedidos")
    app.register_blueprint(entregas_bp, url_prefix="/entregas")
    app.register_blueprint(despachos_bp, url_prefix="/despachos")
    app.register_blueprint(remisiones_bp, url_prefix="/remisiones")
    app.register_blueprint(exportaciones_bp, url_prefix="/exportaciones")
    app.register_blueprint(notificaciones_bp, url_prefix="/notificaciones")
    app.register_blueprint(tracking_bp, url_prefix="/tracking")
    app.register_blueprint(integraciones_bp, url_prefix="/integraciones")

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            "now": datetime.now,
            "today": datetime.today(),
            "config": app.config,
        }

    return app
