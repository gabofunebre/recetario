from datetime import datetime

from . import db  # Importa la instancia de db desde __init__.py

class Carta(db.Model):
    __tablename__ = 'cartas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, default=datetime.utcnow)  # Fecha de creación de la carta
    autor = db.Column(db.String(100))  # Autor de la carta (chef, responsable, etc.)

    # Relación con los platos asociados a esta carta
    platos = db.relationship('Plato', backref='carta', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Carta {self.nombre}>"


class Plato(db.Model):
    __tablename__ = 'platos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.Text)  # Ingredientes como texto libre (no vinculados a `Ingrediente`)
    autor = db.Column(db.String(100))  # Autor o responsable del plato

    # Clave foránea a la carta a la que pertenece
    carta_id = db.Column(db.Integer, db.ForeignKey('cartas.id'), nullable=False)

    # Relación con recetas asociadas al plato
    recetas = db.relationship('Receta', backref='plato', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Plato {self.nombre}>"


class Receta(db.Model):
    __tablename__ = 'recetas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)  # Descripción opcional
    metodo = db.Column(db.Text, nullable=False)  # Método de preparación

    # Clave foránea opcional a plato
    plato_id = db.Column(db.Integer, db.ForeignKey('platos.id'), nullable=True)

    # Relación con ingredientes (con cantidades y unidades)
    ingredientes = db.relationship('Ingrediente', backref='receta', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Receta {self.nombre}>"


class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.String(50))  # Cantidad (por ejemplo: 100)
    unidad = db.Column(db.String(20))  # Unidad (por ejemplo: g, ml, tazas)

    # Clave foránea a la receta correspondiente
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)

    def __repr__(self):
        return f"<Ingrediente {self.nombre} ({self.cantidad} {self.unidad})>"

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    posicion = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.posicion})>"

