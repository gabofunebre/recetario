from app import create_app, db
from app.models import Usuario, Receta, Ingrediente


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        alice = Usuario(nombre='Alice', posicion='Chef')
        bob = Usuario(nombre='Bob', posicion='Ayudante')
        db.session.add_all([alice, bob])
        db.session.flush()

        r1 = Receta(nombre='Tostadas', autor='Alice', descripcion='Tostadas con manteca', metodo='Tostar pan y untar manteca')
        db.session.add(r1)
        db.session.flush()
        db.session.add_all([
            Ingrediente(nombre='Pan', cantidad='2', unidad='rebanadas', receta_id=r1.id),
            Ingrediente(nombre='Manteca', cantidad='10', unidad='gramos', receta_id=r1.id),
        ])

        r2 = Receta(nombre='Ensalada básica', autor='Bob', descripcion='Ensalada sencilla', metodo='Cortar y mezclar todo')
        db.session.add(r2)
        db.session.flush()
        db.session.add_all([
            Ingrediente(nombre='Lechuga', cantidad='1', unidad='unidad', receta_id=r2.id),
            Ingrediente(nombre='Tomate', cantidad='2', unidad='unidad', receta_id=r2.id),
        ])

        db.session.commit()
        print('Seed: datos iniciales creados correctamente.')


if __name__ == '__main__':
    seed()
