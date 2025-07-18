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

    // inicializar handlers para la(s) línea(s) existente(s)
    contIngredientes.querySelectorAll('.ingrediente').forEach(addHandlers);

    // guardar una plantilla limpia para futuros ingredientes
    const template = contIngredientes.querySelector('.ingrediente').cloneNode(true);
    template.querySelectorAll('input').forEach(i => i.value = '');
    template.querySelectorAll('select').forEach(s => s.selectedIndex = 0);

    btnAgregar.addEventListener('click', () => {
      const clone = template.cloneNode(true);
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

  // ------------------- PREVIA DE SUBIDA DE IMÁGENES -------------
  const inputImagenes = document.getElementById('imagenes');
  const preview = document.getElementById('preview');
  const btnCapturar = document.getElementById('btn-capturar');
  const capturaInput = document.getElementById('capture-input');
  const formReceta = document.getElementById('form-receta');
  let archivosSeleccionados = [];
  const renderPreviews = () => {
    if (!preview) return;
    preview.innerHTML = '';
    archivosSeleccionados.forEach((file, idx) => {
      const wrapper = document.createElement('div');
      wrapper.className = 'preview-container';
      const img = document.createElement('img');
      img.className = 'img-thumbnail preview-thumb';
      const url = URL.createObjectURL(file);
      img.src = url;
      img.onload = () => URL.revokeObjectURL(url);
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'preview-remove';
      btn.innerHTML = '&times;';
      btn.addEventListener('click', () => {
        archivosSeleccionados.splice(idx, 1);
        renderPreviews();
      });
      wrapper.appendChild(img);
      wrapper.appendChild(btn);
      preview.appendChild(wrapper);
    });
  };

  const agregarArchivos = (files) => {
    Array.from(files).forEach(file => {
      if (!file.type.startsWith('image/')) return;
      archivosSeleccionados.push(file);
    });
    renderPreviews();
  };

  if (inputImagenes) {
    inputImagenes.addEventListener('change', (e) => {
      agregarArchivos(e.target.files);
      inputImagenes.value = '';
    });
  }

  if (btnCapturar && capturaInput) {
    btnCapturar.addEventListener('click', () => capturaInput.click());
    capturaInput.addEventListener('change', (e) => {
      agregarArchivos(e.target.files);
      capturaInput.value = '';
    });
  }

  // ------------------- ELIMINAR IMÁGENES EXISTENTES -------------
  const contActuales = document.getElementById('imagenes-actuales');
  if (contActuales && formReceta) {
    contActuales.querySelectorAll('.eliminar-imagen').forEach(btn => {
      btn.addEventListener('click', () => {
        const cont = btn.parentElement;
        if (cont) cont.remove();
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'eliminar_imagenes';
        input.value = btn.dataset.img;
        formReceta.appendChild(input);
      });
    });
  }

  if (formReceta) {
    formReceta.addEventListener('submit', (e) => {
      e.preventDefault();

      console.log('🧾 Enviando manualmente...');
      console.log('Archivos seleccionados:', archivosSeleccionados);

      const formData = new FormData(formReceta);

      archivosSeleccionados.forEach((file) => {
        formData.append('imagenes[]', file);
      });

      fetch(formReceta.action, {
        method: 'POST',
        body: formData,
      })
      .then(res => {
        if (res.redirected) {
          window.location.href = res.url;
        } else {
          return res.text();
        }
      })
      .then(data => {
        if (data) console.log('Respuesta del servidor:', data);
      })
      .catch(err => console.error('Error al enviar:', err));
    });
  }

});
