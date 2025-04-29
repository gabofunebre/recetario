# seed.py - Población inicial con nueva estructura Carta → Seccion → Plato → Receta → Ingrediente

from datetime import datetime
from app import create_app, db
from app.models import Usuario, Carta, Seccion, Plato, Receta, Ingrediente


def seed():
    app = create_app()
    with app.app_context():
        # Borrar y crear tablas
        db.drop_all()
        db.create_all()

        # Usuarios de ejemplo
        alice = Usuario(nombre='Alice', posicion='Chef Principal')
        bob   = Usuario(nombre='Bob', posicion='Sous Chef')
        db.session.add_all([alice, bob])
        db.session.flush()

        # Carta de prueba
        carta = Carta(
            nombre='Carta de Prueba',
            autor='Alice',
            fecha=datetime.utcnow().date()
        )
        db.session.add(carta)
        db.session.flush()

        # Sección de Entradas
        entradas = Seccion(
            nombre='Entradas',
            carta_id=carta.id
        )
        db.session.add(entradas)
        db.session.flush()

        # Plato: Ensalada César
        plato1 = Plato(
            nombre='Ensalada César',
            descripcion='Lechuga, pollo, queso y aderezo casero',
            seccion_id=entradas.id
        )
        db.session.add(plato1)
        db.session.flush()

        # Receta asociada al plato
        receta1 = Receta(
            nombre='Aderezo César',
            autor='Alice',
            descripcion='Salsa clásica para la ensalada',
            metodo='Mezclar aceite, huevo, anchoas, limón y parmesano',
            plato_id=plato1.id
        )
        db.session.add(receta1)
        db.session.flush()

        # Ingredientes de la receta
        ingredientes_receta1 = [
            Ingrediente(nombre='Aceite de Oliva', cantidad='100', unidad='ml', receta_id=receta1.id),
            Ingrediente(nombre='Huevo', cantidad='1', unidad='unidad', receta_id=receta1.id),
            Ingrediente(nombre='Anchoas', cantidad='4', unidad='filetes', receta_id=receta1.id)
        ]
        db.session.add_all(ingredientes_receta1)

        # Sección de Principales
        principales = Seccion(
            nombre='Principales',
            carta_id=carta.id
        )
        db.session.add(principales)
        db.session.flush()

        # Plato: Pollo al Horno
        plato2 = Plato(
            nombre='Pollo al Horno',
            descripcion='Pollo marinado y al horno con hierbas',
            seccion_id=principales.id
        )
        db.session.add(plato2)
        db.session.flush()

        # Recetas: Salsa y Guarnición
        salsa = Receta(
            nombre='Salsa de Hierbas',
            autor='Bob',
            descripcion='Salsa para el pollo',
            metodo='Mezclar crema, hierbas frescas y ajo',
            plato_id=plato2.id
        )
        papas = Receta(
            nombre='Papas Asadas',
            autor='Bob',
            descripcion='Papas al horno con romero',
            metodo='Cortar papas, sazonar y hornear',
            plato_id=plato2.id
        )
        db.session.add_all([salsa, papas])
        db.session.flush()

        ingredientes_salsa = [
            Ingrediente(nombre='Crema', cantidad='200', unidad='ml', receta_id=salsa.id),
            Ingrediente(nombre='Hierbas', cantidad='10', unidad='gramos', receta_id=salsa.id)
        ]
        ingredientes_papas = [
            Ingrediente(nombre='Papas', cantidad='500', unidad='gramos', receta_id=papas.id),
            Ingrediente(nombre='Romero', cantidad='5', unidad='gramos', receta_id=papas.id)
        ]
        db.session.add_all(ingredientes_salsa + ingredientes_papas)

        # Confirmar cambios
        db.session.commit()

        print('Seed: datos iniciales creados correctamente.')


if __name__ == '__main__':
    seed()
