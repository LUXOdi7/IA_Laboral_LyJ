from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)

# Cargar los casos y sus palabras clave desde el CSV
casos_df = pd.read_csv('casos_laborales.csv')

def preprocesar_texto(texto):
    """
    Preprocesa el texto de entrada para mejorar la coincidencia de palabras clave.
    Convierte a minúsculas y elimina caracteres no alfanuméricos (excepto espacios).

    Args:
        texto (str): El texto a preprocesar.

    Returns:
        str: El texto preprocesado.
    """
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóú\s]', '', texto)
    return texto

def buscar_soluciones(texto_usuario):
    """
    Busca en la base de conocimientos (casos_laborales.csv) las soluciones que coinciden
    con las palabras clave en el texto del usuario.

    Args:
        texto_usuario (str): El texto ingresado por el usuario.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario contiene
              la descripción del caso y su resolución.  Retorna una lista vacía
              si no se encuentran coincidencias.
    """
    texto_usuario = preprocesar_texto(texto_usuario)
    soluciones_encontradas = []

    for index, row in casos_df.iterrows():
        palabras_clave = [preprocesar_texto(p) for p in row['palabras_clave'].split(', ')] # Preprocesar palabras clave del CSV
        for palabra in palabras_clave:
            if palabra in texto_usuario:
                soluciones_encontradas.append({
                    "caso": row['descripcion'],
                    "resolucion": row['resolucion'],
                    "index": index # Agregar el índice del caso
                })
                break  # Importante: Evita agregar la misma solución varias veces
    return soluciones_encontradas

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Maneja la página principal del sistema.
    Si se recibe un POST, procesa la consulta del usuario y muestra los resultados en la misma página.
    Si es un GET, muestra el formulario de entrada.
    """
    respuestas = [] # Inicializar la variable respuestas
    texto_usuario = ""
    if request.method == "POST":
        texto_usuario = request.form["descripcion"]
        if not texto_usuario.strip():  # Verifica si el texto está vacío o solo contiene espacios
            error_message = "Por favor, ingrese una descripción del conflicto."
            return render_template("index.html", error=error_message, respuestas=respuestas, texto_usuario=texto_usuario)
        respuestas = buscar_soluciones(texto_usuario)

    return render_template("index.html", respuestas=respuestas, texto_usuario=texto_usuario)

@app.route("/caso/<int:index>")  # Nueva ruta para ver un caso detallado
def ver_caso(index):
    """
    Muestra la descripción y resolución de un caso específico.

    Args:
        index (int): El índice del caso en el DataFrame.

    Returns:
        str: El template renderizado con los detalles del caso,
             o un mensaje de error si el índice no es válido.
    """
    if 0 <= index < len(casos_df):
        caso = casos_df.iloc[index]
        return render_template("caso_detalle.html", caso=caso.to_dict(), index=index)
    else:
        return "Caso no encontrado", 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    Manejador de error para errores internos del servidor (código 500).
    """
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
