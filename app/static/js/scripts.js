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
    let autoresData = [];

    if (apiAutoresUrl) {
      fetch(apiAutoresUrl)
        .then(res => res.json())
        .then(data => {
          autoresData = data;
          fuseAutores = new Fuse(autoresData, { keys: ['nombre'], threshold: 0.3 });
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
});
