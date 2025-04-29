document.addEventListener('DOMContentLoaded', () => {
  // ------------------- BUSCADOR DE RECETAS -------------------
  const buscador = document.getElementById('buscador');
  const resultados = document.getElementById('resultados');
  let fuseRecetas;

  if (buscador && resultados) {
    function inicializarFuseRecetas(data) {
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
    }

    function mostrarResultadosRecetas(res) {
      resultados.innerHTML = '';
      if (!res.length) {
        resultados.innerHTML = '<p>No se encontraron recetas.</p>';
        return;
      }
      const query = buscador.value.trim().toLowerCase();
      res.forEach(item => {
        const rec = item.item;
        let nota = '';
        const match = rec.ingredientes_texto.split(' ').find(w => w.toLowerCase().includes(query));
        if (match) nota = ` (Contiene ${match})`;
        const div = document.createElement('div');
        div.className = 'resultado';
        div.textContent = rec.nombre + nota;
        div.onclick = () => window.location.href = `/receta/${rec.id}`;
        resultados.appendChild(div);
      });
    }

    fetch('/buscar_recetas?q=')
      .then(res => res.json())
      .then(data => inicializarFuseRecetas(data))
      .catch(err => console.error('Error al cargar recetas:', err));

    buscador.addEventListener('input', () => {
      const q = buscador.value.trim();
      if (q && fuseRecetas) mostrarResultadosRecetas(fuseRecetas.search(q));
      else resultados.innerHTML = '';
    });
  }

  // ------------------- BUSCADOR DE AUTORES -------------------
  const formReceta = document.getElementById('form-receta');
  if (formReceta) {
    const apiAutoresUrl = formReceta.dataset.apiAutores;
    let fuseAutores;

    if (apiAutoresUrl) {
      fetch(apiAutoresUrl)
        .then(res => res.json())
        .then(data => {
          fuseAutores = new Fuse(data, { keys: ['nombre'], threshold: 0.3 });
        })
        .catch(err => console.error('Error al cargar autores:', err));
    }

    const inputAutor = document.getElementById('autor');
    const listaAutores = document.getElementById('resultados_autores');

    inputAutor.addEventListener('input', () => {
      const q = inputAutor.value.trim();
      listaAutores.innerHTML = '';
      if (!q || !fuseAutores) return;
      fuseAutores.search(q).slice(0, 5).forEach(res => {
        const u = res.item;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'list-group-item list-group-item-action';
        btn.textContent = u.nombre;
        btn.addEventListener('click', () => {
          inputAutor.value = u.nombre;
          listaAutores.innerHTML = '';
        });
        listaAutores.appendChild(btn);
      });
    });

    document.addEventListener('click', e => {
      if (!listaAutores.contains(e.target) && e.target !== inputAutor) {
        listaAutores.innerHTML = '';
      }
    });
  }

  // ------------------- INGREDIENTES DINÁMICOS -------------------
  const btnAgregar = document.getElementById('btn-agregar');
  const contenedor = document.getElementById('ingredientes-container');

  if (btnAgregar && contenedor) {
    btnAgregar.addEventListener('click', () => {
      const original = contenedor.querySelector('.ingrediente');
      const clon = original.cloneNode(true);
      clon.querySelectorAll('input, select').forEach(el => el.value = '');
      contenedor.appendChild(clon);
    });

    contenedor.addEventListener('click', e => {
      if (e.target.classList.contains('btn-remove')) {
        const rows = contenedor.querySelectorAll('.ingrediente');
        if (rows.length > 1) {
          e.target.closest('.ingrediente').remove();
        }
      }
    });
  }

  // ------------------- CREAR CARTA: SECCIONES & PLATOS -------------------
  const formCarta = document.getElementById('form-carta');
  if (formCarta) {
    const contSecciones = document.getElementById('secciones-container');
    const btnAddSeccion = document.getElementById('btn-agregar-seccion');
    const inputNombreCarta = document.getElementById('carta-nombre');
    const inputPayload = document.getElementById('payload');
    const modalPlatoEl = document.getElementById('modalPlato');
    const formPlato = document.getElementById('form-plato');
    let seccionActivaIdx = null;

    // Estructura en memoria
    const data = { nombreCarta: '', secciones: [] };

    const renderSecciones = () => {
      contSecciones.innerHTML = '';
      data.secciones.forEach((sec, idx) => {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        card.innerHTML = `
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <input type="text" class="form-control me-2 seccion-nombre"
                     placeholder="Nombre de la sección" value="${sec.nombre || ''}">
              <button class="btn btn-danger btn-eliminar-seccion">&times;</button>
            </div>
            <h6>Platos</h6>
            <ul class="list-group mb-2">
              ${sec.platos.map(p => `<li class="list-group-item">
                <strong>${p.nombre}</strong><br><small>${p.descripcion}</small>
              </li>`).join('')}
            </ul>
            <button class="btn btn-outline-primary btn-agregar-plato">
              + Agregar Plato
            </button>
          </div>`;
        contSecciones.appendChild(card);

        // Eventos
        const inputSecNombre = card.querySelector('.seccion-nombre');
        inputSecNombre.addEventListener('input', e => {
          data.secciones[idx].nombre = e.target.value;
        });
        card.querySelector('.btn-eliminar-seccion').addEventListener('click', () => {
          data.secciones.splice(idx,1);
          renderSecciones();
        });
        card.querySelector('.btn-agregar-plato').addEventListener('click', () => {
          seccionActivaIdx = idx;
          new bootstrap.Modal(modalPlatoEl).show();
        });
      });
    };

    btnAddSeccion.addEventListener('click', () => {
      data.secciones.push({ nombre: '', platos: [] });
      renderSecciones();
    });

    // Submit Plato desde modal
    formPlato.addEventListener('submit', e => {
      e.preventDefault();
      const nombre = document.getElementById('plato-nombre').value.trim();
      const desc = document.getElementById('plato-descripcion').value.trim();
      if (nombre && seccionActivaIdx !== null) {
        data.secciones[seccionActivaIdx].platos.push({ nombre, descripcion: desc });
        renderSecciones();
      }
      bootstrap.Modal.getInstance(modalPlatoEl).hide();
      formPlato.reset();
    });

    // Antes de enviar la carta
    formCarta.addEventListener('submit', e => {
      data.nombreCarta = inputNombreCarta.value.trim();
      if (!data.nombreCarta) {
        e.preventDefault();
        return alert('La carta necesita un nombre.');
      }
      inputPayload.value = JSON.stringify(data);
    });

    // Iniciar con una sección vacía
    btnAddSeccion.click();
  }
});
