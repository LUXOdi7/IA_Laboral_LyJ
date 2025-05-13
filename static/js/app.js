document.querySelector("form").onsubmit = function(event) {
    let descripcion = document.querySelector("#descripcion").value;
    if (descripcion.trim() === "") {
        alert("Por favor, ingresa una descripción del conflicto.");
        event.preventDefault(); // Evita el envío del formulario si está vacío
    }
};
