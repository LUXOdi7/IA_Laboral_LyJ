document.querySelector("form").onsubmit = function(event) {
    let descripcion = document.querySelector("#descripcion").value;
    let mensajeError = document.querySelector("#mensaje-error");

    if (descripcion.trim() === "") {
        mensajeError.textContent = "Por favor, ingresa una descripción del conflicto.";
        mensajeError.style.color = "red";
        event.preventDefault();
    } else {
        mensajeError.textContent = ""; // Limpia el mensaje si todo está bien
    }
};
