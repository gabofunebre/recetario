# seed.py - Población inicial de datos para Recetario con modelo Carta → Seccion → Plato → Receta → Ingrediente

from datetime import datetime
from app import create_app, db
from app.models import Usuario, Carta, Seccion, Plato, Receta, Ingrediente


def seed():
    app = create_app()
    with app.app_context():
        # Reinicia la base de datos
        db.drop_all()
        db.create_all()

        # --- Usuarios de ejemplo ---
        alice = Usuario(nombre='Alice', posicion='Chef Principal')
        bob = Usuario(nombre='Bob', posicion='Sous Chef')
        db.session.add_all([alice, bob])
        db.session.flush()

        # --- Carta de prueba ---
        carta = Carta(
            nombre='Carta de Prueba',
            autor='Alice',
            fecha=datetime.utcnow().date()
        )
        db.session.add(carta)
        db.session.flush()

        # --- Sección General ---
        seccion = Seccion(
            nombre='General',
            carta_id=carta.id
        )
        db.session.add(seccion)
        db.session.flush()

        # --- Plato y Receta: Tortilla de Patatas ---
        plato1 = Plato(
            nombre='Tortilla de Patatas',
            descripcion='Tortilla española clásica',
            seccion_id=seccion.id
        )
        db.session.add(plato1)
        db.session.flush()

        receta1 = Receta(
            nombre='Tortilla de Patatas',
            autor='Alice',
            descripcion='Receta básica de tortilla de patatas.',
            metodo='1. Pelar y cortar patatas; 2. Freír; 3. Batir huevos; 4. Cuajar',
            plato_id=plato1.id
        )
        db.session.add(receta1)
        db.session.flush()

        ingredientes1 = [
            Ingrediente(nombre='Patatas', cantidad='500', unidad='gramos', receta_id=receta1.id),
            Ingrediente(nombre='Huevos', cantidad='4', unidad='unidad', receta_id=receta1.id),
            Ingrediente(nombre='Cebolla', cantidad='1', unidad='unidad', receta_id=receta1.id)
        ]
        db.session.add_all(ingredientes1)

        # --- Plato y Receta: Gazpacho Andaluz ---
        plato2 = Plato(
            nombre='Gazpacho Andaluz',
            descripcion='Sopa fría de verduras',
            seccion_id=seccion.id
        )
        db.session.add(plato2)
        db.session.flush()

        receta2 = Receta(
            nombre='Gazpacho Andaluz',
            autor='Bob',
            descripcion='Refrescante gazpacho.',
            metodo='1. Cortar verduras; 2. Triturar; 3. Enfriar',
            plato_id=plato2.id
        )
        db.session.add(receta2)
        db.session.flush()

        ingredientes2 = [
            Ingrediente(nombre='Tomate', cantidad='1', unidad='kilogramo', receta_id=receta2.id),
            Ingrediente(nombre='Pepino', cantidad='1', unidad='unidad', receta_id=receta2.id),
            Ingrediente(nombre='Pimiento Verde', cantidad='1', unidad='unidad', receta_id=receta2.id)
        ]
        db.session.add_all(ingredientes2)

        # Confirmar todo
        db.session.commit()

        print('Seed: datos iniciales creados correctamente.')


if __name__ == '__main__':
    seed()
