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

  // ------------------- INGREDIENTES DINÁMICOS -------------------
  const contIngredientes = document.getElementById('ingredientes-container');
  const btnAgregar = document.getElementById('btn-agregar');
  if (contIngredientes && btnAgregar) {
    const addHandlers = (elem) => {
      const btnRemove = elem.querySelector('.btn-remove');
      if (btnRemove) {
        btnRemove.addEventListener('click', () => {
          elem.remove();
        });
      }
    };

    // inicializar handlers para la primera línea
    contIngredientes.querySelectorAll('.ingrediente').forEach(addHandlers);

    btnAgregar.addEventListener('click', () => {
      const base = contIngredientes.querySelector('.ingrediente');
      if (!base) return;
      const clone = base.cloneNode(true);
      clone.querySelectorAll('input').forEach(i => i.value = '');
      clone.querySelectorAll('select').forEach(s => s.selectedIndex = 0);
      addHandlers(clone);
      contIngredientes.appendChild(clone);
    });
  }

  // ------------------- GALERÍA DE IMÁGENES --------------------
  const thumbs = document.querySelectorAll('#galeria img');
  const modalElem = document.getElementById('imagenModal');
  const carouselElem = document.getElementById('galeriaCarousel');
  if (thumbs.length && modalElem && carouselElem) {
    const modal = new bootstrap.Modal(modalElem);
    const carousel = new bootstrap.Carousel(carouselElem);
    thumbs.forEach((img, idx) => {
      img.addEventListener('click', () => {
        carousel.to(idx);
        modal.show();
      });
    });
  }

  // ---------------------------------------------------------------
});
