from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from . import db
from .models import Carta, Plato, Receta, Ingrediente, Usuario
from datetime import datetime

# Crea el blueprint para las rutas principales
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

# API para obtener recetas en formato JSON
@main.route('/buscar_recetas')
def buscar_recetas():
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

# API dinámico de autores (usuarios + autores históricos de recetas)
@main.route('/api/autores', methods=['GET'])
def api_autores():
    # Nombres de usuarios registrados
    usuarios = [u.nombre for u in Usuario.query.all()]
    # Nombres de autor existentes en recetas
    autores_receta = [r.autor for r in Receta.query.with_entities(Receta.autor).distinct()]
    # Combinar y eliminar duplicados preservando orden
    nombres = []
    for name in usuarios + autores_receta:
        if name and name not in nombres:
            nombres.append(name)
    # Formatear para JSON
    autores = [{"nombre": n} for n in nombres]
    return jsonify(autores)

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

# Crear nueva receta con autor dinámico
@main.route('/crear_receta', methods=['GET', 'POST'])
def crear_receta():
    if request.method == 'POST':
        autor_id = request.form.get('usuario_id')
        autor_input = request.form.get('autor_busqueda', '').strip()
        # Si el usuario seleccionó de la lista, usarlo, sino usar texto libre
        autor = autor_input
        if autor_id:
            user = Usuario.query.get(int(autor_id))
            if user:
                autor = user.nombre
        nombre = request.form['nombre']
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
            ing = Ingrediente(
                nombre=ingredientes_data[i],
                cantidad=cantidades_data[i],
                unidad=unidades_data[i],
                receta_id=receta.id
            )
            db.session.add(ing)
        db.session.commit()
        return redirect(url_for('main.ver_recetas'))
    return render_template('crear_receta_independiente.html')

# Mostrar detalle de una receta
@main.route('/receta/<int:id>')
def mostrar_receta(id):
    receta = Receta.query.get_or_404(id)
    return render_template('mostrar_receta.html', receta=receta)

# Vista de recetas con mensaje opcional
@main.route('/recetas')
def ver_recetas():
    query = request.args.get('q')
    mensaje = None
    if query:
        mensaje = f"No se encontraron resultados para '{query}'. Mostrando todas las recetas."
    recetas = Receta.query.all()
    return render_template('recetas.html', recetas=recetas, mensaje=mensaje)
