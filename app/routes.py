
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    jsonify,
    flash,
    current_app,
    send_from_directory,
    session,
    abort,
    Response,
    stream_with_context,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import subprocess
import hashlib
from . import db
from .models import Usuario, Receta, Ingrediente
import json

import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

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


def backup_token_required(func):
    """Verifica el token Bearer provisto para los respaldos."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        expected = current_app.config.get('BACKUP_TOKEN')
        if not expected or not auth.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth.split(' ', 1)[1]
        if token != expected:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper


@main.route('/backup/capabilities', methods=['GET'])
@backup_token_required
def backup_capabilities():
    """Ficha técnica del respaldo disponible."""
    return jsonify({
        "version": "v1",
        "types": ["db"],
        "est_seconds": 120,
        "est_size": 104857600,
    })


@main.route('/backup/export', methods=['POST'])
@backup_token_required
def backup_export():
    """Genera y entrega el respaldo de la base de datos."""
    db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    try:
        result = subprocess.run(['pg_dump', db_url], capture_output=True)
    except FileNotFoundError:
        return jsonify({"error": "pg_dump not found"}), 500

    if result.returncode != 0:
        current_app.logger.error(result.stderr.decode())
        return jsonify({"error": "pg_dump failed"}), 500

    data = result.stdout
    checksum = hashlib.sha256(data).hexdigest()
    size = len(data)

    def generate():
        yield data

    response = Response(stream_with_context(generate()), mimetype='application/octet-stream')
    response.headers['X-Checksum-SHA256'] = checksum
    response.headers['X-Size'] = str(size)
    response.headers['X-Format'] = 'sql'
    return response

# ----------------------- AUTENTICACIÓN -----------------------

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        clave = request.form.get('clave', '')
        user = Usuario.query.filter_by(nombre=nombre).first()
        if user and check_password_hash(user.password_hash, clave):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash(f"Bienvenido {user.nombre}. Puedes ver todas las recetas pero editar solo las propias.")
            return redirect(url_for('main.index'))
        flash('Credenciales incorrectas')
    return render_template('login.html')


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        clave = request.form.get('clave', '')
        if not nombre or not clave:
            flash('Completa todos los campos')
        elif Usuario.query.filter_by(nombre=nombre).first():
            flash('El usuario ya existe')
        else:
            user = Usuario(nombre=nombre, password_hash=generate_password_hash(clave))
            db.session.add(user)
            db.session.commit()
            flash('Usuario creado, inicia sesión')
            return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
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
@login_required
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
            metodo=metodo,
            usuario_id=session.get('user_id')
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
                    try:
                        f.save(os.path.join(carpeta, nombre_seguro))
                    except OSError as err:
                        current_app.logger.error(f"Error al guardar {nombre_seguro}: {err}")
                        flash("Error al guardar imágenes")

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
    usuarios = Usuario.query.all()
    return render_template('recetas.html', recetas=recetas, mensaje=mensaje, usuarios=usuarios)

@main.route('/receta/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_receta(id):
    receta = Receta.query.get_or_404(id)
    if not (session.get('is_admin') or session.get('user_id') == receta.usuario_id):
        abort(403)
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
                    try:
                        f.save(os.path.join(carpeta, nombre_seguro))
                    except OSError as err:
                        current_app.logger.error(f"Error al guardar {nombre_seguro}: {err}")
                        flash("Error al guardar imágenes")
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
@login_required
def eliminar_receta(id):
    receta = Receta.query.get_or_404(id)
    if not (session.get('is_admin') or session.get('user_id') == receta.usuario_id):
        abort(403)
    db.session.delete(receta)
    db.session.commit()
    carpeta = os.path.join(current_app.config['IMAGE_UPLOADS'], str(id))
    if os.path.isdir(carpeta):
        import shutil
        shutil.rmtree(carpeta)
    flash('Receta eliminada correctamente')
    return redirect(url_for('main.ver_recetas'))


@main.route('/receta/<int:id>/configurar', methods=['POST'])
@login_required
@admin_required
def configurar_receta(id):
    receta = Receta.query.get_or_404(id)
    usuario_id = request.form.get('usuario_id', type=int)
    user = Usuario.query.get(usuario_id)
    if user:
        receta.usuario_id = user.id
        db.session.commit()
        flash('Propietario actualizado')
    return redirect(url_for('main.ver_recetas'))


@main.route('/admin/usuarios')
@login_required
@admin_required
def admin_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin_users.html', usuarios=usuarios)


@main.route('/admin/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    user = Usuario.query.get_or_404(id)
    if user.is_admin:
        abort(403)
    Receta.query.filter_by(usuario_id=user.id).update({'usuario_id': None})
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado')
    return redirect(url_for('main.admin_usuarios'))


@main.route('/admin/usuarios/<int:id>/password', methods=['POST'])
@login_required
@admin_required
def cambiar_password(id):
    user = Usuario.query.get_or_404(id)
    clave = request.form.get('clave', '')
    if clave:
        user.password_hash = generate_password_hash(clave)
        db.session.commit()
        flash('Contraseña actualizada')
    return redirect(url_for('main.admin_usuarios'))


@main.route('/backup/export', methods=['POST'])
@backup_token_required
def backup_export():
    db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    cmd = ['pg_dump', db_url]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as err:
        current_app.logger.error(f"Error al ejecutar pg_dump: {err}")
        return jsonify({'error': 'Error al ejecutar pg_dump'}), 500

    sha256 = hashlib.sha256()
    total = 0
    chunks = []
    for chunk in iter(lambda: proc.stdout.read(8192), b''):
        sha256.update(chunk)
        total += len(chunk)
        chunks.append(chunk)

    stderr = proc.stderr.read().decode()
    ret = proc.wait()
    if ret != 0:
        current_app.logger.error(f"pg_dump error: {stderr}")
        return jsonify({'error': 'pg_dump falló', 'details': stderr.strip()}), 500

    def generate():
        for c in chunks:
            yield c

    response = Response(stream_with_context(generate()), mimetype='application/octet-stream')
    response.headers['X-Checksum-SHA256'] = sha256.hexdigest()
    response.headers['X-Size'] = str(total)
    response.headers['X-Format'] = 'sql'
    return response
