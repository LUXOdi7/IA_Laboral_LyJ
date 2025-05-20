from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
import re
from urllib.parse import urlencode
import unicodedata

app = Flask(__name__)

# Cargar los casos y sus palabras clave desde el CSV
casos_df = pd.read_csv('casos_laborales.csv')

def preprocesar_texto(texto):
    """
    Preprocesa el texto de entrada para mejorar la coincidencia de palabras clave.
    Convierte a minúsculas, elimina caracteres no alfanuméricos (excepto espacios)
    y elimina acentos.

    Args:
        texto (str): El texto a preprocesar.

    Returns:
        str: El texto preprocesado.
    """
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóú\s]', '', texto)
    # Eliminar acentos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    return texto

def buscar_soluciones(texto_usuario):
    """
    Busca en la base de conocimientos (casos_laborales.csv) las soluciones que coinciden
    con las palabras clave en el texto del usuario.

    Args:
        texto_usuario (str): El texto ingresado por el usuario.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario contiene
              la descripción del caso, su resolución y el índice del caso.
              Retorna una lista vacía si no se encuentran coincidencias.
    """
    texto_usuario = preprocesar_texto(texto_usuario)
    soluciones_encontradas = []

    for index, row in casos_df.iterrows():
        palabras_clave = [preprocesar_texto(p) for p in row['palabras_clave'].split(', ')]
        for palabra in palabras_clave:
            if palabra in texto_usuario:
                soluciones_encontradas.append({
                    "descripcion": row['descripcion'],
                    "resolucion": row['resolucion'],
                    "procedimiento": row['procedimiento'],
                    "ley": row['ley'],
                    "index": index
                })
                break
    return soluciones_encontradas

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Maneja la página principal del sistema.
    Si se recibe un POST, procesa la consulta del usuario y muestra los resultados en la misma página.
    Si es un GET, muestra el formulario de entrada.
    """
    respuestas = []
    texto_usuario = ""
    if request.method == "POST":
        texto_usuario = request.form["descripcion"]
        if not texto_usuario.strip():
            error_message = "Por favor, ingrese una descripción del conflicto."
            return render_template("index.html", error=error_message, respuestas=respuestas, texto_usuario=texto_usuario)
        respuestas = buscar_soluciones(texto_usuario)

    return render_template("index.html", respuestas=respuestas, texto_usuario=texto_usuario)

@app.route("/generar_reporte", methods=["POST"])
def generar_reporte():
    """
    Genera un reporte con los casos seleccionados por el usuario, sin usar sesiones.
    Los casos seleccionados se reciben como una lista de índices en el formulario y se pasan a la
    ruta /resultado a través de la URL.
    """
    casos_seleccionados_indices = request.form.getlist('casos_seleccionados')
    casos_seleccionados_indices = [int(i) for i in casos_seleccionados_indices]

    respuestas = buscar_soluciones(request.form['descripcion_original'])

    casos_seleccionados = [respuesta for respuesta in respuestas if respuesta['index'] in casos_seleccionados_indices]

    reporte_data = []
    for caso in casos_seleccionados:
        reporte_data.append({
            'descripcion': caso['descripcion'],
            'resolucion': caso['resolucion'],
            'procedimiento': caso['procedimiento'],
            'ley': caso['ley'],
            'index': caso['index']
        })
    reporte_url = url_for('resultado') + '?' + urlencode({'reporte_data': str(reporte_data)})

    return redirect(reporte_url)

@app.route("/resultado")
def resultado():
    """
    Muestra el reporte con los casos seleccionados. Los datos del reporte se reciben a través de la URL.
    """
    import ast
    reporte_data_str = request.args.get('reporte_data', '[]')
    reporte_data = ast.literal_eval(reporte_data_str)
    return render_template("resultado.html", casos_seleccionados=reporte_data)

@app.route("/caso/<int:index>")
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
