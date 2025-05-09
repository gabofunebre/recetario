document.addEventListener('DOMContentLoaded', () => {
  // ------------------- BUSCADOR DE RECETAS -------------------
  const buscador = document.getElementById('buscador');
  const resultados = document.getElementById('resultados');
  let fuseRecetas;

  if (buscador && resultados) {
    fetch('/buscar_recetas?q=')
      .then(res => res.json())
      .then(data => {
        const datos = data.recetas.map(r => ({
          id: r.id,
          nombre: r.nombre,
          descripcion: r.descripcion,
          plato_nombre: r.plato?.nombre || '',
          ingredientes_texto: r.ingredientes.map(i => i.nombre).join(' ')
        }));
        fuseRecetas = new Fuse(datos, {
          threshold: 0.4,
          keys: ['nombre', 'descripcion', 'plato_nombre', 'ingredientes_texto']
        });
      })
      .catch(err => console.error('Error al cargar recetas:', err));

    buscador.addEventListener('input', () => {
      resultados.innerHTML = '';
      const q = buscador.value.trim().toLowerCase();
      if (!q || !fuseRecetas) return;
      const matches = fuseRecetas.search(q);
      if (!matches.length) {
        // puedes mostrar un item diciendo "No hay resultados"
        return;
      }
      matches.forEach(item => {
        const rec = item.item;
        const li = document.createElement('button');
        li.type = 'button';
        li.className = 'list-group-item list-group-item-action';
        li.textContent = rec.nombre;
        li.addEventListener('click', () => {
          window.location.href = `/receta/${rec.id}`;
        });
        resultados.appendChild(li);
      });
    });
  }

  // ... resto de tu JS (autores, ingredientes, carta) ...
});
