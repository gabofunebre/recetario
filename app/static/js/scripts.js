const buscador = document.getElementById("buscador");
const resultados = document.getElementById("resultados");

// Función para obtener recetas desde la API de búsqueda
function obtenerRecetas(query) {
    return fetch(`/buscar_recetas?q=${query}`)
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
            div.innerText = receta.nombre;  // Mostrar solo el nombre de la receta
            div.onclick = () => window.location.href = `/receta/${receta.id}`;
            resultados.appendChild(div);
        });
    } else {
        resultados.innerHTML = "<p>No se encontraron recetas.</p>";
    }
}

// Escuchar el input del campo de búsqueda
buscador.addEventListener("input", function () {
    const query = this.value.trim();  // Obtener valor de búsqueda sin espacios innecesarios
    
    if (query.length > 0) {
        // Filtrar recetas
        obtenerRecetas(query).then(filtradas => mostrarResultados(filtradas));
    } else {
        // Si el campo está vacío, no mostrar resultados
        resultados.innerHTML = "";
    }
});

// Si presionas Enter, buscar también
buscador.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
        const query = this.value.trim();
        obtenerRecetas(query).then(filtradas => mostrarResultados(filtradas));
    }
});
