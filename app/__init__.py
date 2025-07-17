import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instancia global de SQLAlchemy (la usás en models.py)
db = SQLAlchemy()

# Track if the tables were successfully created
_tables_created = False

def create_app():
    app = Flask(__name__)

    # Clave secreta necesaria para sesiones (flash, login, etc.)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')


    # Configuración de la URI de la base de datos
    # Por defecto se conecta al contenedor "db" definido en docker-compose.
    database_url = os.getenv(
        'DATABASE_URL',
        'postgresql://recetario:recetario@db:5432/recetario'
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Carpeta para subir imágenes
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    image_dir = os.path.join(base_dir, 'data', 'images')
    os.makedirs(image_dir, exist_ok=True)
    app.config['IMAGE_UPLOADS'] = image_dir

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
            global _tables_created
            _tables_created = True
        except Exception as e:
            app.logger.error(f"Error al crear las tablas: {e}")

    def _ensure_tables_exist():
        """Intenta crear las tablas si aún no fueron creadas."""
        global _tables_created
        if _tables_created:
            return
        try:
            db.create_all()
            _tables_created = True
        except Exception as e:
            app.logger.error(f"Error al crear las tablas: {e}")

    # Intentar de nuevo en cada request hasta que la DB esté lista
    @app.before_request
    def check_tables():
        _ensure_tables_exist()

    return app
