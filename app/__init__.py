import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instancia global de SQLAlchemy (la usás en models.py)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Clave secreta necesaria para sesiones (flash, login, etc.)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')

    # Configuración de la URI de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recetario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Habilitar modo de desarrollo y depuración
    app.config['FLASK_ENV'] = 'development'  # Configura el entorno como desarrollo
    app.config['DEBUG'] = True  # Habilita la depuración

    # Inicializamos SQLAlchemy con la app
    db.init_app(app)

    # Registrar blueprints y modelos
    with app.app_context():
        from . import routes, models
        from .routes import main  # Blueprint principal
        app.register_blueprint(main)

        # Crear las tablas si aún no existen
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error al crear las tablas: {e}")

    return app
