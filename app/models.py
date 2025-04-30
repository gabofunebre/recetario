from datetime import datetime

from . import db  # Importa la instancia de db desde __init__.py


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    posicion = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.posicion})>"


class Carta(db.Model):
    __tablename__ = 'cartas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    autor = db.Column(db.String(100))

    # Relación con Sección
    secciones = db.relationship(
        'Seccion', back_populates='carta', cascade='all, delete-orphan', lazy=True
    )

    def __repr__(self):
        return f"<Carta {self.nombre}>"


class Seccion(db.Model):
    __tablename__ = 'secciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    # Clave foránea a Carta
    carta_id = db.Column(db.Integer, db.ForeignKey('cartas.id'), nullable=False)
    carta = db.relationship('Carta', back_populates='secciones')

    # Platos en la sección
    platos = db.relationship(
        'Plato', back_populates='seccion', cascade='all, delete-orphan', lazy=True
    )

    def __repr__(self):
        return f"<Seccion {self.nombre}>"


class Plato(db.Model):
    __tablename__ = 'platos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

    # Clave foránea a Seccion
    seccion_id = db.Column(db.Integer, db.ForeignKey('secciones.id'), nullable=False)
    seccion = db.relationship('Seccion', back_populates='platos')

    # Relación con Receta
    recetas = db.relationship(
        'Receta', back_populates='plato', cascade='all, delete-orphan', lazy=True
    )

    def __repr__(self):
        return f"<Plato {self.nombre}>"


class Receta(db.Model):
    __tablename__ = 'recetas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    metodo = db.Column(db.Text, nullable=False)

    # Clave foránea a Plato (ahora opcional para recetas independientes)
    plato_id = db.Column(db.Integer, db.ForeignKey('platos.id'), nullable=True)
    plato = db.relationship('Plato', back_populates='recetas')

    # Relación con Ingredientes
    ingredientes = db.relationship(
        'Ingrediente', back_populates='receta', cascade='all, delete-orphan', lazy=True
    )

    def __repr__(self):
        return f"<Receta {self.nombre}>"


class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.String(50))
    unidad = db.Column(db.String(20))

    # Clave foránea a Receta
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    receta = db.relationship('Receta', back_populates='ingredientes')

    def __repr__(self):
        return f"<Ingrediente {self.nombre} ({self.cantidad} {self.unidad})>"
