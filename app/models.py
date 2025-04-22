from datetime import datetime
from . import db  # Importa la instancia de db desde __init__.py

class Carta(db.Model):
    __tablename__ = 'cartas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    autor = db.Column(db.String(100))
    platos = db.relationship('Plato', backref='carta', cascade='all, delete-orphan', lazy=True)

class Plato(db.Model):
    __tablename__ = 'platos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.Text)  # Ingredientes del plato como descripción libre
    autor = db.Column(db.String(100))
    carta_id = db.Column(db.Integer, db.ForeignKey('cartas.id'), nullable=False)
    recetas = db.relationship('Receta', backref='plato', cascade='all, delete-orphan', lazy=True)

class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    metodo = db.Column(db.Text, nullable=False)
    plato_id = db.Column(db.Integer, db.ForeignKey('platos.id'), nullable=True)  # ahora opcional

    ingredientes = db.relationship('Ingrediente', backref='receta', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Receta {self.nombre}>"

class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.String(50))
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
