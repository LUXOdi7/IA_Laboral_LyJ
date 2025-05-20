document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector("form");
    if (form) {
        form.onsubmit = function(event) {
            let descripcion = document.querySelector("#descripcion").value;
            let mensajeError = document.querySelector("#mensaje-error");

            if (descripcion.trim() === "") {
                mensajeError.textContent = "Por favor, ingresa una descripción del conflicto.";
                mensajeError.style.color = "red";
                event.preventDefault();
            } else {
                mensajeError.textContent = "";
            }
        };
    }

    const textoUsuarioElement = document.getElementById('descripcion');
    const textoUsuario = textoUsuarioElement ? textoUsuarioElement.value : '';
    const palabrasClaveSpan = document.getElementById('palabras_clave_generales');
    if (palabrasClaveSpan) {
        let todasLasPalabrasClave = "";
        let respuestas = window.respuestasData;

        if (respuestas && respuestas.length > 0) {
            for (let i = 0; i < respuestas.length; i++) {
                const respuesta = respuestas[i];
                const palabrasClaveEncontradasHTML = mostrarPalabrasClave(respuesta, textoUsuario);
                if (todasLasPalabrasClave) {
                    todasLasPalabrasClave += ", ";
                }
                todasLasPalabrasClave += palabrasClaveEncontradasHTML;
            }
        } else {
            todasLasPalabrasClave = "Ninguna";
        }

        palabrasClaveSpan.innerHTML = todasLasPalabrasClave;
    }

    // Modo oscuro
    const checkbox = document.getElementById('checkbox');
    const body = document.body;
    const container = document.querySelector('.container');
    const mensajeError = document.getElementById('mensaje-error');
    const labels = document.querySelectorAll('label');
    const resultadosDiv = document.getElementById('resultados');
    const h1 = document.querySelector('h1');
    const em = document.querySelector('.theme-switch-wrapper em'); // Agregar para el texto del modo oscuro

    function toggleDarkMode() {
        body.classList.toggle('dark-mode');
        container.classList.toggle('dark-mode');
        mensajeError.classList.toggle('dark-mode');
        h1.classList.toggle('dark-mode');
        labels.forEach(label => label.classList.toggle('dark-mode'));
        if (resultadosDiv) {
            resultadosDiv.classList.toggle('dark-mode');
        }
        em.classList.toggle('dark-mode'); // Cambiar también el estilo del texto
    }

    if (checkbox) {
        checkbox.addEventListener('change', toggleDarkMode);
    }

    // Comprueba si el modo oscuro está habilitado en las preferencias del usuario
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        toggleDarkMode();
        if (checkbox) {
            checkbox.checked = true;
        }
    }
});

function mostrarPalabrasClave(respuesta, textoUsuario) {
    const palabrasClaveCaso = respuesta.palabras_clave.split(', ');
    const textoUsuarioLower = textoUsuario.toLowerCase();
    const palabrasClaveEncontradas = [];

    for (const palabraClaveCaso of palabrasClaveCaso) {
        if (textoUsuarioLower.includes(palabraClaveCaso.toLowerCase())) {
            palabrasClaveEncontradas.push(palabraClaveCaso);
        }
    }

    let palabrasClaveHTML = '';
    if (palabrasClaveEncontradas.length > 0) {
        palabrasClaveHTML =  `${palabrasClaveEncontradas.join(', ')}`;
    } else {
        palabrasClaveHTML = 'Ninguna';
    }

    return palabrasClaveHTML;
}
