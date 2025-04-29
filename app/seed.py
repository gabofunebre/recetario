#!/usr/bin/env python3
"""
Script de semillas (seed) para poblar la base de datos con datos de prueba.
Ejecutar desde la raíz del proyecto:

    python seed.py
"""
from app import create_app, db
from app.models import Usuario, Carta, Plato, Receta, Ingrediente
from datetime import datetime

# Inicializar la app y el contexto
app = create_app()
with app.app_context():
    # Opcional: limpiar la base de datos
    db.drop_all()
    db.create_all()

    # Crear usuarios de prueba
    usuarios = [
        Usuario(nombre='Alice', posicion='Chef Ejecutivo'),
        Usuario(nombre='Bob', posicion='Sous Chef'),
        Usuario(nombre='Carlos', posicion='Pastelero'),
    ]
    db.session.add_all(usuarios)

    # Crear cartas
    carta1 = Carta(nombre='Menú de Verano', autor='Alice', fecha=datetime(2025, 6, 1))
    carta2 = Carta(nombre='Menú de Invierno', autor='Bob', fecha=datetime(2025, 12, 1))
    db.session.add_all([carta1, carta2])
    db.session.flush()

    # Crear platos para las cartas
    plato1 = Plato(nombre='Ensalada Fresca', ingredientes='Lechuga, Tomate, Pepino', autor='Alice', carta_id=carta1.id)
    plato2 = Plato(nombre='Sopa Caliente', ingredientes='Calabaza, Zanahoria, Jengibre', autor='Bob', carta_id=carta2.id)
    db.session.add_all([plato1, plato2])
    db.session.flush()

    # Crear recetas genéricas
    receta1 = Receta(nombre='Hamburguesa Clásica', autor='Carlos', descripcion='Una hamburguesa jugosa con queso y verduras.', metodo='1. Formar carne. 2. Asar. 3. Montar burguer.')
    receta2 = Receta(nombre='Pasta al Pesto', autor='Alice', descripcion='Pasta fresca con salsa pesto casera.', metodo='1. Cocer pasta. 2. Mezclar pesto.')
    db.session.add_all([receta1, receta2])
    db.session.flush()

    # Asociar ingredientes detallados a las recetas
    ingredientes_seed = [
        Ingrediente(nombre='Carne molida', cantidad='200', unidad='gramos', receta_id=receta1.id),
        Ingrediente(nombre='Pan de hamburguesa', cantidad='2', unidad='unidad', receta_id=receta1.id),
        Ingrediente(nombre='Queso cheddar', cantidad='2', unidad='rebanadas', receta_id=receta1.id),
        Ingrediente(nombre='Pasta italiana', cantidad='150', unidad='gramos', receta_id=receta2.id),
        Ingrediente(nombre='Albahaca', cantidad='30', unidad='gramos', receta_id=receta2.id),
        Ingrediente(nombre='Aceite de oliva', cantidad='50', unidad='ml', receta_id=receta2.id),
    ]
    db.session.add_all(ingredientes_seed)

    # Confirmar cambios
    db.session.commit()
    print('✅ Base de datos poblada con datos de prueba.')
