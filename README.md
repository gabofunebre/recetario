
# Recetario App

Una aplicación de recetas donde los usuarios pueden consultar, agregar, editar y eliminar recetas.

## Estructura de directorios

/srv/dev-disk-by-uuid-1735d6ab-2a75-4dc4-91a9-b81bb3fda73d/Servicios/Recetario/recetario/
├── /app/                 # Lógica de la aplicación Flask (incluye `run.py` y `seed.py`)
├── /instance/            # Configuraciones locales
├── /__pycache__/          # Archivos compilados de Python
├── Dockerfile             # Instrucciones para crear la imagen Docker
├── docker-compose.yml     # Composición de los contenedores Docker
├── requirements.txt       # Dependencias del proyecto
└── Makefile               # Script para facilitar la gestión del contenedor

## Requisitos

- Python 3.7 o superior
- Docker y Docker Compose instalados
- Git

## Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/gabofunebre/recetario.git
cd recetario
```

2. **Instalar las dependencias**
```bash
pip install -r requirements.txt
```

## Uso

### 1. Levantar la aplicación
Construye y levanta los contenedores Docker con el siguiente comando:

```bash
make up
```

### 2. Acceder a la aplicación
Abre tu navegador y ve a `http://localhost:1881` para acceder a la aplicación en tu contenedor Docker.

### 3. Realizar migraciones de base de datos (si es necesario)
```bash
make migrate
```

### 4. Persistencia y respaldo de la base de datos
La base de datos se guarda de forma persistente fuera del contenedor. El archivo
`recetario.db` se monta desde la carpeta `data` del proyecto mediante el
`docker-compose.yml`:

```
./data/recetario.db:/app/recetario.db
```

Antes de levantar los contenedores asegúrate de crear la carpeta `data/` (el
archivo será generado automáticamente). Para realizar un *backup* simplemente
copia `data/recetario.db` a la ubicación de tu preferencia. La carpeta de
configuración local se mantiene en `instance/`.

## Comandos útiles en el Makefile

- **make up**: Construye y levanta los contenedores en segundo plano.
- **make down**: Detiene los contenedores.
- **make restart**: Reinicia la aplicación (detiene y vuelve a levantar los contenedores).
- **make logs**: Muestra los logs del contenedor.
- **make shell**: Abre una terminal dentro del contenedor.
- **make migrate**: Aplica las migraciones de base de datos (Flask).
- **make seed**: Carga datos iniciales en la base de datos.
- **make pull**: Actualiza el repositorio con los cambios más recientes de GitHub.

## Contribuciones

Si deseas contribuir al proyecto, por favor realiza un fork del repositorio, haz tus cambios y envía un pull request.
