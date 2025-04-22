# Recetario Flask

## Descripción
Este proyecto es una aplicación web para gestionar un recetario, construida con Flask. Permite crear, editar y listar recetas, ingredientes y métodos de preparación. También ofrece la posibilidad de gestionar cartas (por ejemplo, "Carta de Verano 2025").

El proyecto está configurado para ejecutarse en un contenedor Docker, lo que facilita su despliegue y testeo en cualquier entorno compatible con Docker.

## Tecnologías
- **Flask**: Framework web ligero para Python.
- **Docker**: Contenedores para la gestión y ejecución de la app.
- **SQLite**: Base de datos ligera para almacenamiento de recetas e ingredientes.

## Estructura de directorios

/WDPassportGabo/app_recetario/
├── /app/                 # Lógica de la aplicación Flask
├── /instance/            # Configuraciones locales
├── /__pycache__/          # Archivos compilados de Python
├── Dockerfile             # Instrucciones para crear la imagen Docker
├── docker-compose.yml     # Composición de los contenedores Docker
├── requirements.txt       # Dependencias del proyecto
├── run.py                 # Punto de entrada de la aplicación
├── seed.py                # Script para cargar datos iniciales
└── Makefile               # Script para facilitar la gestión del contenedor

## Requisitos

1. **Docker** y **Docker Compose** instalados.
2. **Python 3.7+** (si deseas correr la aplicación fuera de Docker).

### Instalación

### 1. Clonar el repositorio
git clone https://github.com/gabofunebre/recetario.git
cd recetario

### 2. Construir y levantar los contenedores
make up

### 3. Acceder a la aplicación
Abre tu navegador y ve a `http://localhost:1881` para acceder a la aplicación en tu contenedor Docker.

### 4. Realizar migraciones de base de datos (si es necesario)
make migrate


### Comandos útiles en el Makefile

- **make up**: Construye y levanta los contenedores en segundo plano.
- **make down**: Detiene y elimina los contenedores y volúmenes.
- **make restart**: Reinicia la aplicación (detiene y vuelve a levantar los contenedores).
- **make logs**: Muestra los logs del contenedor.
- **make shell**: Abre una terminal dentro del contenedor.
- **make migrate**: Aplica las migraciones de base de datos (Flask).
- **make seed**: Carga datos iniciales en la base de datos.
- **make pull**: Actualiza el repositorio con los cambios más recientes de GitHub.

## Contribuciones

Si deseas contribuir al proyecto, por favor realiza un fork del repositorio, haz tus cambios y envía un pull request.

