document.addEventListener('DOMContentLoaded', () => {
    const buscador = document.getElementById("buscador");
    const resultados = document.getElementById("resultados");
    let fuse;
    let datosRecetas = [];
    let lastQuery = "";
  
    // Inicializar Fuse.js con datos solo de recetas
    function inicializarFuse(data) {
      // Guardamos array de recetas con sus ingredientes originales
      datosRecetas = data.recetas.map(r => ({
        id: r.id,
        nombre: r.nombre,
        descripcion: r.descripcion,
        plato_nombre: r.plato?.nombre || "",
        ingredientes_array: r.ingredientes || []  // array de objetos {nombre}
      }));
      const opciones = {
        includeMatches: false,
        threshold: 0.4,
        keys: ["nombre", "descripcion", "plato_nombre", "ingredientes_array.nombre"]
      };
      fuse = new Fuse(datosRecetas, opciones);
    }
  
    // Mostrar solo recetas con nota del ingrediente coincidente
    function mostrarResultados(resultadosFuse) {
      resultados.innerHTML = "";
      if (!resultadosFuse.length) {
        resultados.innerHTML = "<p>No se encontraron recetas.</p>";
        return;
      }
      resultadosFuse.forEach(res => {
        const rec = res.item;
        let nota = "";
        const qLower = lastQuery.toLowerCase();
        // Buscar coincidencia en ingredientes
        const ingMatch = rec.ingredientes_array.find(i =>
          i.nombre.toLowerCase().includes(qLower)
        );
        if (ingMatch) {
          nota = ` (Contiene ${ingMatch.nombre})`;
        } else if (rec.plato_nombre.toLowerCase().includes(qLower)) {
          nota = ` (Relacionado: ${rec.plato_nombre})`;
        }
  
        const div = document.createElement("div");
        div.className = "resultado";
        div.textContent = rec.nombre + nota;
        div.onclick = () => window.location.href = `/receta/${rec.id}`;
        resultados.appendChild(div);
      });
    }
  
    // Cargar datos iniciales (solo recetas)
    fetch("/buscar_recetas?q=")
      .then(res => res.json())
      .then(data => inicializarFuse(data))
      .catch(err => console.error("Error inicializando Fuse.js:", err));
  
    // Búsqueda en tiempo real
    if (buscador) {
      buscador.addEventListener("input", function() {
        lastQuery = this.value.trim();
        if (lastQuery && fuse) mostrarResultados(fuse.search(lastQuery));
        else resultados.innerHTML = "";
      });
    }
  });
  