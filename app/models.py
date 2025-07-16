from . import db  # Importa la instancia de db desde __init__.py


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    posicion = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.posicion})>"




class Receta(db.Model):
    __tablename__ = 'recetas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    metodo = db.Column(db.Text, nullable=False)



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
