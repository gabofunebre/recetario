const buscador = document.getElementById("buscador");
const resultados = document.getElementById("resultados");

let fuse;
let datosOriginales = null;

// Función para inicializar Fuse.js con los datos de búsqueda
function inicializarFuse(data) {
    datosOriginales = data;

    const opciones = {
        includeScore: true,
        threshold: 0.4,
        keys: [
            "nombre",
            "descripcion",
            "plato_nombre",
            "ingredientes_texto"
        ]
    };

    const fuseData = [];

    if (data.recetas) {
        data.recetas.forEach(r => {
            const receta = {
                ...r,
                tipo: "receta",
                plato_nombre: r.plato?.nombre || "",
                ingredientes_texto: r.ingredientes?.map(i => i.nombre).join(" ") || "",
            };
            fuseData.push(receta);
        });
    }

    if (data.platos) {
        data.platos.forEach(p => fuseData.push({ ...p, tipo: "plato" }));
    }

    if (data.ingredientes) {
        data.ingredientes.forEach(i => fuseData.push({ ...i, tipo: "ingrediente" }));
    }

    console.log("🔍 fuseData:", fuseData);
    fuse = new Fuse(fuseData, opciones);
}

// Función para mostrar resultados
function mostrarResultados(resultadosFuse) {
    resultados.innerHTML = "";

    if (resultadosFuse.length === 0) {
        resultados.innerHTML = "<p>No se encontraron resultados.</p>";
        return;
    }

    const categorias = {
        receta: [],
        plato: [],
        ingrediente: []
    };

    resultadosFuse.forEach(r => {
        categorias[r.item.tipo].push(r.item);
    });

    if (categorias.receta.length > 0) {
        const titulo = document.createElement("h3");
        titulo.textContent = "Recetas";
        resultados.appendChild(titulo);

        categorias.receta.forEach(receta => {
            const div = document.createElement("div");
            div.className = "resultado";
            div.textContent = receta.nombre;
            div.onclick = () => window.location.href = `/receta/${receta.id}`;
            resultados.appendChild(div);
        });
    }

    if (categorias.plato.length > 0) {
        const titulo = document.createElement("h3");
        titulo.textContent = "Platos";
        resultados.appendChild(titulo);

        categorias.plato.forEach(plato => {
            const div = document.createElement("div");
            div.className = "resultado";
            div.textContent = plato.nombre;
            resultados.appendChild(div);
        });
    }

    if (categorias.ingrediente.length > 0) {
        const titulo = document.createElement("h3");
        titulo.textContent = "Ingredientes";
        resultados.appendChild(titulo);

        categorias.ingrediente.forEach(ingrediente => {
            const div = document.createElement("div");
            div.className = "resultado";
            div.textContent = ingrediente.nombre;
            resultados.appendChild(div);
        });
    }
}

// Obtener todos los datos una vez y preparar Fuse.js
fetch("/buscar_recetas?q=")
    .then(response => response.json())
    .then(data => {
        console.log("✅ Datos recibidos del servidor:", data);
        inicializarFuse(data);
    })
    .catch(error => console.error("❌ Error inicializando Fuse.js:", error));

// Buscar mientras se escribe
buscador.addEventListener("input", function () {
    const query = this.value.trim();

    if (query.length > 0 && fuse) {
        const resultadosFiltrados = fuse.search(query);
        console.log("🔍 Resultados filtrados para:", query, resultadosFiltrados);
        mostrarResultados(resultadosFiltrados);
    } else {
        console.log("🕵️ Sin resultados o Fuse no inicializado.");
        resultados.innerHTML = "";
    }
});

// También buscar al presionar Enter
buscador.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
        const query = this.value.trim();

        if (query.length === 0) {
            console.log("⏎ Enter con input vacío, redirigiendo a /recetas");
            window.location.href = "/recetas";
        } else if (fuse) {
            const resultadosFiltrados = fuse.search(query);
            console.log("⏎ Enter presionado. Resultados filtrados para:", query, resultadosFiltrados);

            if (resultadosFiltrados.length === 0) {
                console.log("🚫 Sin resultados. Redirigiendo a /recetas con query.");
                window.location.href = `/recetas?q=${encodeURIComponent(query)}`;
            } else {
                mostrarResultados(resultadosFiltrados);
            }
        } else {
            console.log("⚠️ Fuse no está inicializado.");
        }
    }
});

// Agregar nuevos campos de ingredientes
function agregarIngrediente() {
    const container = document.getElementById("ingredientes-container");
    const nuevoIngrediente = document.createElement("div");
    nuevoIngrediente.classList.add("ingrediente");

    nuevoIngrediente.innerHTML = `
        <label for="ingrediente">Ingrediente:</label>
        <input type="text" name="ingredientes[]" required>
        <label for="cantidad">Cantidad:</label>
        <input type="number" name="cantidades[]" required>
        <label for="unidad">Unidad:</label>
        <select name="unidades[]">
            <option value="gramos">Gramos</option>
            <option value="kilogramos">Kilogramos</option>
            <option value="ml">Mililitros</option>
            <option value="litros">Litros</option>
            <option value="taza">Taza</option>
            <option value="cucharada">Cucharada</option>
            <option value="cucharadita">Cucharadita</option>
        </select>
        <br><br>
    `;
    container.appendChild(nuevoIngrediente);
}
