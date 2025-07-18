
# Recetario App

Una aplicación de recetas donde los usuarios pueden consultar, agregar, editar y eliminar recetas.

La versión actual de la aplicación utiliza **PostgreSQL** como base de datos en lugar de SQLite. Todo se ejecuta dentro de contenedores Docker para facilitar la configuración y la persistencia de los datos.

## Estructura de directorios
```
recetario/
├── app/                # Lógica de la aplicación Flask (run.py, models y routes)
├── instance/           # Configuraciones locales
├── data/
│   ├── db/             # Datos persistentes de PostgreSQL
│   └── images/         # Carpeta para imágenes
├── __pycache__/        # Archivos compilados de Python
├── Dockerfile          # Instrucciones para crear la imagen Docker
├── docker-compose.yml  # Composición de los contenedores Docker
├── requirements.txt    # Dependencias del proyecto
└── Makefile            # Script para facilitar la gestión del contenedor

```
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

Los archivos `.py` y las plantillas HTML se montan en el contenedor y Flask se ejecuta en modo desarrollo (`FLASK_ENV=development`). Cualquier cambio en esos archivos se refleja de inmediato sin reiniciar el contenedor.

### 3. Realizar migraciones de base de datos (si es necesario)
```bash
make migrate
```

### 4. Persistencia y respaldo de la base de datos

La aplicación utiliza PostgreSQL como base de datos, ejecutada en un contenedor
separado. Los datos se almacenan en la carpeta `data/db/` de este proyecto.
Dentro del contenedor se usa la variable `PGDATA` para guardar la información en
`/var/lib/postgresql/data/pgdata`, de modo que `data/db/` puede contener archivos
de mantenimiento (como `.gitkeep`) sin interferir con la base de datos.


Para realizar un *backup* basta con copiar el contenido de `data/db/` o emplear
las herramientas de respaldo de PostgreSQL según tus necesidades. La carpeta de
configuración local sigue estando en `instance/`.

Adicionalmente, las imágenes que suba la aplicación se almacenarán en
`data/images/`, por lo que también puedes respaldar esa carpeta si la utilizas.
Esta carpeta del host se monta en el contenedor como `/app/data/images`,
asegurando que las imágenes persistan aunque se reinicie el servicio.
Asegúrate de que la aplicación tenga permisos de escritura en `data/images/`.

## Comandos útiles en el Makefile

- **make up**: Construye y levanta los contenedores en segundo plano.
- **make down**: Detiene los contenedores.
- **make restart**: Reinicia la aplicación (detiene y vuelve a levantar los contenedores).
- **make logs**: Muestra los logs del contenedor.
- **make shell**: Abre una terminal dentro del contenedor.
- **make migrate**: Aplica las migraciones de base de datos (Flask).
- **make pull**: Actualiza el repositorio con los cambios más recientes de GitHub.

## Contribuciones

Si deseas contribuir al proyecto, por favor realiza un fork del repositorio, haz tus cambios y envía un pull request.
