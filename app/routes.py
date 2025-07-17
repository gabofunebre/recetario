from flask import render_template, request, redirect, url_for, Blueprint, jsonify, flash, current_app, send_from_directory
from werkzeug.utils import secure_filename
from . import db
from .models import Usuario, Receta, Ingrediente
import json

import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)

@main.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(current_app.config['IMAGE_UPLOADS'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_uploaded_images():
    """Return list of uploaded image files regardless of input name."""
    archivos = request.files.getlist('imagenes')
    if not archivos:
        archivos = request.files.getlist('imagenes[]')
    return archivos

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

        # Guardar imágenes si se subieron
        archivos = _get_uploaded_images()
        if archivos:
            carpeta = os.path.join(current_app.config['IMAGE_UPLOADS'], str(receta.id))
            os.makedirs(carpeta, exist_ok=True)
            for f in archivos:
                if f and allowed_file(f.filename):
                    nombre_seguro = secure_filename(f.filename)
                    f.save(os.path.join(carpeta, nombre_seguro))

        return redirect(url_for('main.ver_recetas'))
    return render_template('crear_receta_independiente.html')

@main.route('/receta/<int:id>')
def mostrar_receta(id):
    receta = Receta.query.get_or_404(id)
    carpeta = os.path.join(current_app.config['IMAGE_UPLOADS'], str(id))
    imagenes = []
    if os.path.isdir(carpeta):
        for nombre in os.listdir(carpeta):
            if allowed_file(nombre):
                imagenes.append(f"{id}/{nombre}")
    imagenes.sort()
    return render_template('mostrar_receta.html', receta=receta, imagenes=imagenes)

@main.route('/recetas')
def ver_recetas():
    query = request.args.get('q')
    mensaje = None
    if query:
        mensaje = f"No se encontraron resultados para '{query}'. Mostrando todas las recetas."  
    recetas = Receta.query.all()
    return render_template('recetas.html', recetas=recetas, mensaje=mensaje)

@main.route('/receta/<int:id>/editar', methods=['GET', 'POST'])
def editar_receta(id):
    receta = Receta.query.get_or_404(id)
    carpeta = os.path.join(current_app.config['IMAGE_UPLOADS'], str(id))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        autor = request.form.get('autor', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        metodo = request.form.get('metodo', '').strip()
        if not nombre or not autor or not metodo:
            return "Por favor, complete todos los campos", 400
        receta.nombre = nombre
        receta.autor = autor
        receta.descripcion = descripcion
        receta.metodo = metodo
        # Actualizar ingredientes
        Ingrediente.query.filter_by(receta_id=receta.id).delete()
        ingredientes_data = request.form.getlist('ingredientes[]')
        cantidades_data = request.form.getlist('cantidades[]')
        unidades_data = request.form.getlist('unidades[]')
        for i in range(len(ingredientes_data)):
            ing = Ingrediente(
                nombre=ingredientes_data[i],
                cantidad=cantidades_data[i],
                unidad=unidades_data[i],
                receta_id=receta.id
            )
            db.session.add(ing)
        # Eliminar imágenes seleccionadas
        eliminar = request.form.getlist('eliminar_imagenes')
        for relpath in eliminar:
            path = os.path.join(current_app.config['IMAGE_UPLOADS'], relpath)
            if os.path.isfile(path):
                os.remove(path)
        # Guardar nuevas imágenes
        archivos = _get_uploaded_images()
        if archivos:
            os.makedirs(carpeta, exist_ok=True)
            for f in archivos:
                if f and allowed_file(f.filename):
                    nombre_seguro = secure_filename(f.filename)
                    f.save(os.path.join(carpeta, nombre_seguro))
        db.session.commit()
        return redirect(url_for('main.ver_recetas'))

    imagenes = []
    if os.path.isdir(carpeta):
        for nombre in os.listdir(carpeta):
            if allowed_file(nombre):
                imagenes.append(f"{id}/{nombre}")
    imagenes.sort()
    return render_template('editar_receta.html', receta=receta, imagenes=imagenes)


@main.route('/receta/<int:id>/eliminar', methods=['POST'])
def eliminar_receta(id):
    receta = Receta.query.get_or_404(id)
    db.session.delete(receta)
    db.session.commit()
    carpeta = os.path.join(current_app.config['IMAGE_UPLOADS'], str(id))
    if os.path.isdir(carpeta):
        import shutil
        shutil.rmtree(carpeta)
    flash('Receta eliminada correctamente')
    return redirect(url_for('main.ver_recetas'))
