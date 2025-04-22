const buscador = document.getElementById("buscador");
const resultados = document.getElementById("resultados");

// Función para obtener recetas desde la API
function obtenerRecetas() {
    return fetch("/api/recetas")
        .then(response => response.json())
        .catch(error => console.error("Error al obtener las recetas:", error));
}

// Función para mostrar los resultados filtrados
function mostrarResultados(filtradas) {
    resultados.innerHTML = "";  // Limpiar resultados previos

    if (filtradas.length > 0) {
        filtradas.forEach(receta => {
            const div = document.createElement("div");
            div.className = "resultado";
            div.innerText = receta.nombre;  // Puedes mostrar más detalles si lo deseas
            div.onclick = () => window.location.href = `/receta/${receta.id}`;
            resultados.appendChild(div);
        });
    } else {
        resultados.innerHTML = "<p>No se encontraron recetas.</p>";
    }
}

// Función para buscar recetas
function buscarRecetas(query) {
    obtenerRecetas().then(recetas => {
        const filtradas = recetas.filter(r =>
            r.nombre.toLowerCase().includes(query) || r.descripcion.toLowerCase().includes(query)
        );
        mostrarResultados(filtradas);
    });
}

// Escuchar el input del campo de búsqueda
buscador.addEventListener("input", function () {
    const query = this.value.toLowerCase();
    
    if (query.length > 0) {
        // Filtrar recetas
        buscarRecetas(query);
    } else {
        // Si el campo está vacío, mostrar todas las recetas
        obtenerRecetas().then(recetas => mostrarResultados(recetas));
    }
});

// Si presionas Enter, buscar también
buscador.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
        const query = this.value.toLowerCase();
        buscarRecetas(query);
    }
});
