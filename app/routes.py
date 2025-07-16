from flask import render_template, request, redirect, url_for, Blueprint, jsonify, flash
from . import db
from .models import Usuario, Receta, Ingrediente
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

# Serialización de recetas para API
def _serialize_receta(receta):
    return {
        "id": receta.id,
        "nombre": receta.nombre,
        "descripcion": receta.descripcion,
        "ingredientes": [{"id": ing.id, "nombre": ing.nombre} for ing in receta.ingredientes]
    }

@main.route('/buscar_recetas')
def buscar_recetas():
    recetas = Receta.query.all()
    ingredientes = Ingrediente.query.all()
    return jsonify({
        "recetas": [_serialize_receta(r) for r in recetas],
        "ingredientes": [{"id": i.id, "nombre": i.nombre} for i in ingredientes]
    })

@main.route('/api/autores', methods=['GET'])
def api_autores():
    usuarios = [u.nombre for u in Usuario.query.all()]
    autores_receta = [r.autor for r in Receta.query.with_entities(Receta.autor).distinct()]
    nombres = []
    for name in usuarios + autores_receta:
        if name and name not in nombres:
            nombres.append(name)
    return jsonify([{"nombre": n} for n in nombres])


@main.route('/crear_receta', methods=['GET', 'POST'])
def crear_receta():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        autor = request.form.get('autor', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        metodo = request.form.get('metodo', '').strip()
        ingredientes_data = request.form.getlist('ingredientes[]')
        cantidades_data = request.form.getlist('cantidades[]')
        unidades_data = request.form.getlist('unidades[]')
        if not nombre or not autor or not metodo:
            return "Por favor, complete todos los campos", 400
        receta = Receta(
            nombre=nombre,
            autor=autor,
            descripcion=descripcion,
            metodo=metodo
        )
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

@main.route('/receta/<int:id>')
def mostrar_receta(id):
    receta = Receta.query.get_or_404(id)
    return render_template('mostrar_receta.html', receta=receta)

@main.route('/recetas')
def ver_recetas():
    query = request.args.get('q')
    mensaje = None
    if query:
        mensaje = f"No se encontraron resultados para '{query}'. Mostrando todas las recetas."  
    recetas = Receta.query.all()
    return render_template('recetas.html', recetas=recetas, mensaje=mensaje)
