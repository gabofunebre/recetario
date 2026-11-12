# Propuesta visual moderna

Una actualización discreta: tonos crema y verde oliva, títulos de estilo
recetario, más aire y controles con bordes suaves. Se mantienen los recorridos
habituales de la aplicación.

- Portada con el buscador como protagonista y acceso a todas las recetas.
- Navegación con la pantalla actual destacada y menú adaptable al celular.
- Login con etiquetas visibles y autocompletado de usuario y contraseña.
- Estilos comunes para tarjetas, formularios, tablas y detalle de receta.

## Alcance

Solo cambia CSS y las plantillas base, inicio y login. El JavaScript del
buscador, Fuse.js, los endpoints, los modelos y las dependencias se mantienen.
No hay migraciones, cambios de esquema ni operaciones sobre los datos de uso.
Tampoco se agregan servicios, fuentes externas ni bibliotecas.

La propuesta se revisa en la rama `propuesta_moderna`. No requiere importar,
restaurar ni reinicializar la base de datos. Para probarla con datos de ejemplo,
usá una base temporal independiente mediante `DATABASE_URL`; no ejecutes
pruebas que creen o eliminen registros sobre tu base en uso.
