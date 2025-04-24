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
    recetas = Receta.query.all()
    recetas_json = [{"id": receta.id, "nombre": receta.nombre, "descripcion": receta.descripcion} for receta in recetas]
    return jsonify(recetas_json)

# ✅ Ruta unificada para buscador con Fuse.js
@main.route('/api/todo', methods=['GET'])
def api_todo():
    recetas = Receta.query.all()
    ingredientes = Ingrediente.query.all()
    platos = Plato.query.all()
    data = {
        "recetas": [{"id": r.id, "nombre": r.nombre, "descripcion": r.descripcion} for r in recetas],
        "ingredientes": [{"nombre": i.nombre, "receta_id": i.receta_id} for i in ingredientes],
        "platos": [{"nombre": p.nombre, "carta_id": p.carta_id} for p in platos]
    }
    return jsonify(data)

# Mostrar detalle de una receta
@main.route('/receta/<int:id>')
def mostrar_receta(id):
    receta = Receta.query.get_or_404(id)
    return render_template('mostrar_receta.html', receta=receta)

# Listar todas las cartas
@main.route('/cartas')
def cartas():
    cartas = Carta.query.all()
    return render_template('cartas.html', cartas=cartas)

# Ver una carta específica
@main.route('/carta/<int:id>')
def carta(id):
    carta = Carta.query.get_or_404(id)
    platos = Plato.query.filter_by(carta_id=id).all()
    return render_template('carta_actual.html', carta=carta, platos=platos)

# Ver la carta actual (última)
@main.route('/carta_actual')
def carta_actual():
    carta = Carta.query.order_by(Carta.id.desc()).first()
    platos = Plato.query.filter_by(carta_id=carta.id).all() if carta else []
    return render_template('carta_actual.html', carta=carta, platos=platos)

# Crear nueva carta
@main.route('/crear_carta', methods=['GET', 'POST'])
def crear_carta():
    recetas = Receta.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        autor = request.form['autor']
        carta = Carta(nombre=nombre, autor=autor)
        db.session.add(carta)
        db.session.commit()
        return redirect(url_for('main.cartas'))
    return render_template('crear_carta.html', recetas=recetas)

# Crear nuevo plato para una carta
@main.route('/crear_plato/<int:carta_id>', methods=['GET', 'POST'])
def crear_plato(carta_id):
    carta = Carta.query.get_or_404(carta_id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        ingredientes = request.form['ingredientes']
        autor = request.form['autor']
        plato = Plato(nombre=nombre, ingredientes=ingredientes, autor=autor, carta_id=carta.id)
        db.session.add(plato)
        db.session.commit()
        return redirect(url_for('main.cartas'))
    return render_template('crear_plato.html', carta=carta)

# Crear nueva receta
@main.route('/crear_receta', methods=['GET', 'POST'])
def crear_receta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        autor = request.form['autor']
        metodo = request.form['metodo']
        ingredientes_data = request.form.getlist('ingredientes[]')
        cantidades_data = request.form.getlist('cantidades[]')
        unidades_data = request.form.getlist('unidades[]')
        if not nombre or not autor or not metodo:
            return "Por favor, complete todos los campos", 400
        receta = Receta(nombre=nombre, autor=autor, metodo=metodo)
        db.session.add(receta)
        db.session.commit()
        for i in range(len(ingredientes_data)):
            ingrediente = Ingrediente(
                nombre=ingredientes_data[i],
                cantidad=cantidades_data[i],
                unidad=unidades_data[i],
                receta_id=receta.id
            )
            db.session.add(ingrediente)
        db.session.commit()
        return redirect(url_for('main.ver_recetas'))
    return render_template('crear_receta_independiente.html')

# Crear ingrediente adicional en receta existente
@main.route('/crear_ingrediente/<int:receta_id>', methods=['GET', 'POST'])
def crear_ingrediente(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        unidad = request.form.get('unidad', '')
        if not nombre or not cantidad:
            return render_template('crear_ingrediente.html', receta=receta, error="Por favor, complete todos los campos.")
        ingrediente = Ingrediente(nombre=nombre, cantidad=cantidad, unidad=unidad, receta_id=receta.id)
        db.session.add(ingrediente)
        db.session.commit()
        return redirect(url_for('main.mostrar_receta', id=receta.id))
    return render_template('crear_ingrediente.html', receta=receta)

# API para búsqueda rápida (para script)
@main.route('/buscar_recetas')
def buscar_recetas():
    query = request.args.get('q', '')
    recetas = Receta.query.all()
    platos = Plato.query.all()
    ingredientes = Ingrediente.query.all()
    recetas_json = []
    for receta in recetas:
        recetas_json.append({
            "id": receta.id,
            "nombre": receta.nombre,
            "descripcion": receta.descripcion,
            "plato": {"id": receta.plato.id, "nombre": receta.plato.nombre} if receta.plato else None,
            "ingredientes": [{"id": ing.id, "nombre": ing.nombre} for ing in receta.ingredientes]
        })
    platos_json = [{"id": p.id, "nombre": p.nombre} for p in platos]
    ingredientes_json = [{"id": i.id, "nombre": i.nombre} for i in ingredientes]
    return jsonify({"recetas": recetas_json, "platos": platos_json, "ingredientes": ingredientes_json})

# Vista de recetas con mensaje opcional
@main.route('/recetas')
def ver_recetas():
    query = request.args.get('q')
    mensaje = None
    if query:
        mensaje = f"No se encontraron resultados para '{query}'. Mostrando todas las recetas."
    recetas = Receta.query.all()
    return render_template('recetas.html', recetas=recetas, mensaje=mensaje)
