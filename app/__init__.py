from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instancia global de SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración de la URI de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recetario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializamos la base de datos con la app
    db.init_app(app)

    # Registramos las rutas o blueprints
    with app.app_context():
        from . import routes, models
        from .routes import main
        app.register_blueprint(main)

        # Solo creamos las tablas si no existen (para evitar sobrescribir datos)
        try:
            db.create_all()  # Crea las tablas de la base de datos
        except Exception as e:
            print(f"Error al crear las tablas: {e}")

    return app
