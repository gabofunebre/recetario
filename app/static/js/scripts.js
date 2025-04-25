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
    const userInput = document.getElementById('autor_busqueda');
    const userResults = document.getElementById('resultados_usuarios');
    const autorIdField = document.getElementById('usuario_id');
    let fuseAutores;
  
    if (userInput && userResults && autorIdField) {
      function inicializarFuseAutores(data) {
        fuseAutores = new Fuse(data, {
          keys: ['nombre'],
          threshold: 0.3
        });
      }
  
      fetch('/api/autores')
        .then(res => res.json())
        .then(data => inicializarFuseAutores(data))
        .catch(err => console.error('Error al cargar autores:', err));
  
      userInput.addEventListener('input', () => {
        const q = userInput.value.trim();
        userResults.innerHTML = '';
        autorIdField.value = '';
        if (!q || !fuseAutores) return;
        fuseAutores.search(q).slice(0, 5).forEach(obj => {
          const u = obj.item;
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'list-group-item list-group-item-action';
          btn.textContent = u.nombre;
          btn.addEventListener('click', () => {
            userInput.value = u.nombre;
            autorIdField.value = u.id;
            userResults.innerHTML = '';
          });
          userResults.appendChild(btn);
        });
      });
  
      document.addEventListener('click', e => {
        if (!e.target.closest('#autor_busqueda') && !e.target.closest('#resultados_usuarios')) {
          userResults.innerHTML = '';
        }
      });
    }
  
    // ------------------- INGREDIENTES DINÁMICOS -------------------
    const btnAgregar = document.getElementById('btn-agregar');
    if (btnAgregar) btnAgregar.addEventListener('click', () => {
      const container = document.getElementById('ingredientes-container');
      const nuevo = document.createElement('div');
      nuevo.classList.add('row', 'g-2', 'align-items-end', 'mb-2', 'ingrediente');
      nuevo.innerHTML = `
        <div class="col-md-5">
          <label class="form-label">Ingrediente</label>
          <input type="text" name="ingredientes[]" class="form-control" placeholder="Ej. Harina" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">Cantidad</label>
          <input type="number" name="cantidades[]" class="form-control" placeholder="Ej. 100" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">Unidad</label>
          <select name="unidades[]" class="form-select">
            <option value="gramos">Gramos</option>
            <option value="kilogramos">Kilogramos</option>
            <option value="ml">Mililitros</option>
            <option value="litros">Litros</option>
            <option value="unidad">Unidad</option>
            <option value="puñado">Puñado</option>
            <option value="taza">Taza</option>
            <option value="cucharada">Cucharada</option>
            <option value="cucharadita">Cucharadita</option>
          </select>
        </div>
        <div class="col-md-1 text-end">
          <button type="button" class="btn btn-outline-danger btn-remove" title="Eliminar ingrediente">&times;</button>
        </div>
      `;
      container.appendChild(nuevo);
    });
  
    document.addEventListener('click', e => {
      if (e.target.matches('.btn-remove')) {
        e.target.closest('.ingrediente').remove();
      }
    });
  });
  