from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from . import db
from .models import Carta, Plato, Receta, Ingrediente
from datetime import datetime

# Crea el blueprint para las rutas principales
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


# Ruta para obtener las recetas en formato JSON
@main.route('/api/recetas', methods=['GET'])
def api_recetas():
    recetas = Receta.query.all()  # Obtener todas las recetas desde la base de datos
    recetas_json = [{"id": receta.id, "nombre": receta.nombre, "descripcion": receta.descripcion} for receta in recetas]
    return jsonify(recetas_json)


# Ruta para ver una receta
@main.route('/receta/<int:id>')
def mostrar_receta(id):
    receta = Receta.query.get_or_404(id)
    ingredientes = Ingrediente.query.filter_by(receta_id=id).all()
    return render_template('mostrar_receta.html', receta=receta, ingredientes=ingredientes)

# Ruta para ver todas las cartas
@main.route('/cartas')
def cartas():
    cartas = Carta.query.all()
    return render_template('cartas.html', cartas=cartas)

# Ruta para ver la carta actual (la más reciente)
@main.route('/carta_actual')
def carta_actual():
    carta = Carta.query.order_by(Carta.id.desc()).first()
    platos = Plato.query.filter_by(carta_id=carta.id).all() if carta else []
    return render_template('carta_actual.html', carta=carta, platos=platos)

# Ruta para crear una nueva carta
@main.route('/crear_carta', methods=['GET', 'POST'])
def crear_carta():
    recetas = Receta.query.all()  # Trae todas las recetas
    if request.method == 'POST':
        nombre = request.form['nombre']
        autor = request.form['autor']
        receta_id = request.form['recetas']  # Obtenemos la receta seleccionada
        carta = Carta(nombre=nombre, autor=autor)
        db.session.add(carta)
        db.session.commit()

        # Asociar la receta al plato si es necesario, puedes expandir esta lógica
        # En caso de que desees que se cree un plato automáticamente o asociar recetas más tarde

        return redirect(url_for('main.cartas'))  # Redirige a la lista de cartas
    return render_template('crear_carta.html', recetas=recetas)  # Pasa las recetas disponibles a la plantilla


# Ruta para crear un plato en una carta específica
@main.route('/crear_plato/<int:carta_id>', methods=['GET', 'POST'])
def crear_plato(carta_id):
    carta = Carta.query.get(carta_id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        ingredientes = request.form['ingredientes']
        autor = request.form['autor']
        plato = Plato(nombre=nombre, ingredientes=ingredientes, autor=autor, carta_id=carta.id)
        db.session.add(plato)
        db.session.commit()
        return redirect(url_for('main.cartas'))  # Redirige a la lista de cartas
    return render_template('crear_plato.html', carta=carta)

# Ruta para crear una receta con ingredientes
@main.route('/crear_receta', methods=['GET', 'POST'])
def crear_receta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        autor = request.form['autor']
        metodo = request.form['metodo']
        ingredientes_data = request.form.getlist('ingredientes[]')  # Lista de ingredientes
        cantidades_data = request.form.getlist('cantidades[]')  # Lista de cantidades
        unidades_data = request.form.getlist('unidades[]')  # Lista de unidades
        
        # Asegúrate de que los datos no estén vacíos
        if not nombre or not autor or not metodo:
            return "Por favor, complete todos los campos", 400  # Error si algún campo está vacío
        
        # Crear la receta
        receta = Receta(nombre=nombre, autor=autor, metodo=metodo)
        db.session.add(receta)
        db.session.commit()

        # Crear ingredientes y asociarlos a la receta
        for i in range(len(ingredientes_data)):
            ingrediente = Ingrediente(
                nombre=ingredientes_data[i],
                cantidad=cantidades_data[i],
                unidad=unidades_data[i],
                receta_id=receta.id
            )
            db.session.add(ingrediente)
        
        db.session.commit()
        return redirect(url_for('main.cartas'))  # Redirige a la lista de cartas

    return render_template('crear_receta_independiente.html')  # Si es GET, muestra el formulario de crear receta

# Ruta para crear un ingrediente en una receta específica
@main.route('/crear_ingrediente/<int:receta_id>', methods=['GET', 'POST'])
def crear_ingrediente(receta_id):
    receta = Receta.query.get(receta_id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        
        # Validación de los campos
        if not nombre or not cantidad:
            return render_template('crear_ingrediente.html', receta=receta, error="Por favor, complete todos los campos.")
        
        # Crear el ingrediente
        ingrediente = Ingrediente(nombre=nombre, cantidad=cantidad, receta_id=receta.id)
        db.session.add(ingrediente)
        db.session.commit()
        return redirect(url_for('main.mostrar_receta', id=receta.id))  # Redirige a la receta específica
    return render_template('crear_ingrediente.html', receta=receta)


# Ruta para buscar recetas en la base de datos
@main.route('/buscar_recetas', methods=['GET'])
def buscar_recetas():
    query = request.args.get('q', '')  # Obtener la consulta de búsqueda desde los parámetros GET
    if query:
        recetas = Receta.query.filter(Receta.nombre.ilike(f'%{query}%')).all()  # Filtrar recetas por nombre
    else:
        recetas = []

    # Convertir las recetas a un formato JSON para enviarlas al frontend
    recetas_json = [{"id": receta.id, "nombre": receta.nombre} for receta in recetas]
    return jsonify(recetas_json)
