from flask import render_template, request, redirect, url_for, Blueprint, jsonify, flash
from . import db
from .models import Usuario, Carta, Seccion, Plato, Receta, Ingrediente
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
        "plato": {"id": receta.plato.id, "nombre": receta.plato.nombre} if receta.plato else None,
        "ingredientes": [{"id": ing.id, "nombre": ing.nombre} for ing in receta.ingredientes]
    }

@main.route('/buscar_recetas')
def buscar_recetas():
    recetas = Receta.query.all()
    platos = Plato.query.all()
    ingredientes = Ingrediente.query.all()
    return jsonify({
        "recetas": [_serialize_receta(r) for r in recetas],
        "platos": [{"id": p.id, "nombre": p.nombre} for p in platos],
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

@main.route('/cartas')
def cartas():
    cartas = Carta.query.order_by(Carta.id.desc()).all()
    return render_template('cartas.html', cartas=cartas)

@main.route('/carta/<int:id>')
def carta(id):
    carta = Carta.query.get_or_404(id)
    secciones = Seccion.query.filter_by(carta_id=carta.id).all()
    return render_template('carta_actual.html', carta=carta, secciones=secciones)

@main.route('/carta_actual')
def carta_actual():
    carta = Carta.query.order_by(Carta.id.desc()).first()
    secciones = Seccion.query.filter_by(carta_id=carta.id).all() if carta else []
    return render_template('carta_actual.html', carta=carta, secciones=secciones)

@main.route('/crear_carta', methods=['GET', 'POST'])
def crear_carta():
    if request.method == 'POST':
        payload = request.form.get('payload')
        if not payload:
            flash('Datos inválidos para crear la carta', 'danger')
            return redirect(url_for('main.crear_carta'))
        data = json.loads(payload)
        # 1) Crear la carta (sin autor por ahora)
        carta = Carta(nombre=data.get('nombreCarta'), autor=None)
        db.session.add(carta)
        db.session.flush()
        # 2) Crear secciones y platos
        for sec in data.get('secciones', []):
            seccion = Seccion(nombre=sec.get('nombre'), carta_id=carta.id)
            db.session.add(seccion)
            db.session.flush()
            for p in sec.get('platos', []):
                plato = Plato(
                    nombre=p.get('nombre'),
                    descripcion=p.get('descripcion'),
                    seccion_id=seccion.id
                )
                db.session.add(plato)
        db.session.commit()
        flash('Carta creada correctamente.', 'success')
        return redirect(url_for('main.cartas'))
    return render_template('crear_carta.html')

@main.route('/crear_plato/<int:carta_id>', methods=['GET', 'POST'])
def crear_plato(carta_id):
    carta = Carta.query.get_or_404(carta_id)
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        if not nombre:
            return "Por favor, complete todos los campos", 400
        # Ahora Plato requiere seccion_id, lanzar error o escoger primera sección
        plato = Plato(nombre=nombre, descripcion=descripcion, seccion_id=None)
        db.session.add(plato)
        db.session.commit()
        return redirect(url_for('main.cartas'))
    return render_template('crear_plato.html', carta=carta)

@main.route('/crear_receta', methods=['GET', 'POST'])
def crear_receta():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        autor = request.form.get('autor', '').strip()
        metodo = request.form.get('metodo', '').strip()
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
