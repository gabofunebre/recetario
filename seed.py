# seed.py - Población inicial de datos para Recetario
# Ajusta la URI de la base de datos según tu configuración

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Importa tus modelos y la instancia de db
from routes import db
from models import Usuario, Receta, Ingrediente, Plato, Carta


def create_app():
    app = Flask(__name__)
    # Usa la variable de entorno DATABASE_URL o sqlite por defecto
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        # Para PostgreSQL o MySQL puedes usar una URL completa
        # Ej: os.getenv('DATABASE_URL', 'sqlite:///recetario.db')
        'sqlite:///recetario.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def seed():
    app = create_app()
    with app.app_context():
        # Reinicia la base de datos
        db.drop_all()
        db.create_all()

        # --- Usuarios ---
        u1 = Usuario(nombre='Alice', posicion='Chef Principal')
        u2 = Usuario(nombre='Bob', posicion='Sous Chef')
        db.session.add_all([u1, u2])

        # --- Recetas y sus ingredientes ---
        r1 = Receta(
            nombre='Tortilla de Patatas',
            autor='Alice',
            descripcion='Clásica tortilla española con patatas y cebolla.',
            metodo='1. Pelar y cortar patatas. 2. Freír en aceite. 3. Batir huevos. 4. Mezclar todo y cuajar.'
        )
        db.session.add(r1)
        db.session.flush()  # Para obtener r1.id
        i1 = Ingrediente(nombre='Patatas', cantidad='500', unidad='gramos', receta_id=r1.id)
        i2 = Ingrediente(nombre='Huevos', cantidad='4', unidad='unidad', receta_id=r1.id)
        i3 = Ingrediente(nombre='Cebolla', cantidad='1', unidad='unidad', receta_id=r1.id)
        db.session.add_all([i1, i2, i3])

        r2 = Receta(
            nombre='Gazpacho Andaluz',
            autor='Bob',
            descripcion='Sopa fría de tomate ideal para verano.',
            metodo='1. Lumpiar y cortar verduras. 2. Triturar todo. 3. Enfriar en nevera.'
        )
        db.session.add(r2)
        db.session.flush()
        i4 = Ingrediente(nombre='Tomate', cantidad='1', unidad='kilogramo', receta_id=r2.id)
        i5 = Ingrediente(nombre='Pepino', cantidad='1', unidad='unidad', receta_id=r2.id)
        i6 = Ingrediente(nombre='Pimiento Verde', cantidad='1', unidad='unidad', receta_id=r2.id)
        db.session.add_all([i4, i5, i6])

        # Guarda las recetas primeras
        db.session.commit()

        # --- Carta y Platos ---
        c1 = Carta(nombre='Carta de Hoy', autor='Alice', fecha=datetime.utcnow().date())
        db.session.add(c1)
        db.session.flush()

        # Crea platos basados en las recetas anteriores
        plato1 = Plato(
            nombre=r1.nombre,
            ingredientes=', '.join([ing.nombre for ing in r1.ingredientes]),
            autor=r1.autor,
            carta_id=c1.id
        )
        plato2 = Plato(
            nombre=r2.nombre,
            ingredientes=', '.join([ing.nombre for ing in r2.ingredientes]),
            autor=r2.autor,
            carta_id=c1.id
        )
        db.session.add_all([plato1, plato2])

        # Confirma todos los cambios
        db.session.commit()

        print('Seed: datos iniciales creados correctamente.')


if __name__ == '__main__':
    seed()
