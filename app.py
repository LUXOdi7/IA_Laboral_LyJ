from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
import re
from urllib.parse import urlencode
import unicodedata
import os
# Importa el diccionario de sinónimos desde el nuevo archivo
from data.sinonimos import sinonimos

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
    con las palabras clave (y sus sinónimos) en el texto del usuario y calcula un porcentaje de similitud.
    """
    texto_usuario_procesado = preprocesar_texto(texto_usuario)
    soluciones_encontradas = []

    for index, row in casos_df.iterrows():
        # Obtener todos los términos relevantes para el caso (palabras clave + sinónimos)
        # Asegurarse de manejar el caso donde 'palabras_clave' podría ser NaN
        palabras_clave_str = str(row['palabras_clave']) if pd.notna(row['palabras_clave']) else ''
        case_keywords_original = [p.strip() for p in palabras_clave_str.split(',') if p.strip()]
        
        case_relevant_terms_processed = set()
        for kw_orig in case_keywords_original:
            kw_processed = preprocesar_texto(kw_orig)
            case_relevant_terms_processed.add(kw_processed)
            if kw_processed in sinonimos:
                for syn_orig in sinonimos[kw_processed]:
                    case_relevant_terms_processed.add(preprocesar_texto(syn_orig))
        
        matched_terms_count = 0
        for term_processed in case_relevant_terms_processed:
            # Verifica si el término procesado del caso está contenido en el texto procesado del usuario
            if term_processed in texto_usuario_procesado:
                matched_terms_count += 1
        
        total_case_terms = len(case_relevant_terms_processed)
        
        similitud_porcentaje = 0
        if total_case_terms > 0:
            similitud_porcentaje = (matched_terms_count / total_case_terms) * 100
        
        # Solo agregar si hay al menos una coincidencia (para evitar mostrar casos sin relación)
        if matched_terms_count > 0:
            soluciones_encontradas.append({
                "descripcion": row['descripcion'],
                "resolucion": row['resolucion'],
                "procedimiento": row['procedimiento'],
                "ley": row['ley'],
                "palabras_clave": palabras_clave_str, # Incluir palabras clave originales para el JS
                "index": index,
                "similitud_porcentaje": round(similitud_porcentaje, 2) # Redondear a 2 decimales
            })
            
    # Ordenar por porcentaje de similitud (descendente)
    soluciones_encontradas.sort(key=lambda x: x['similitud_porcentaje'], reverse=True)
    
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

    respuestas = buscar_soluciones(request.form['descripcion_original']) # Obtener la lista completa de respuestas

    casos_seleccionados = [respuesta for respuesta in respuestas if respuesta['index'] in casos_seleccionados_indices] # Filtrar las respuestas seleccionadas

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

# ==============================================
# NUEVA FUNCIONALIDAD PARA REGISTRAR CASOS
# ==============================================

@app.route("/nuevo_caso", methods=["GET", "POST"])
def nuevo_caso():
    """
    Maneja el formulario para registrar un nuevo caso laboral.
    """
    if request.method == "POST":
        # Obtener datos del formulario
        descripcion = request.form["descripcion"]
        resolucion = request.form["resolucion"]
        procedimiento = request.form["procedimiento"]
        ley = request.form["ley"]
        palabras_clave = request.form["palabras_clave"]
        
        # Crear nuevo registro
        nuevo_caso = {
            "descripcion": descripcion,
            "resolucion": resolucion,
            "procedimiento": procedimiento,
            "ley": ley,
            "palabras_clave": palabras_clave
        }
        
        # Convertir a DataFrame y guardar
        global casos_df
        nuevo_df = pd.DataFrame([nuevo_caso])
        casos_df = pd.concat([casos_df, nuevo_df], ignore_index=True)
        casos_df.to_csv('casos_laborales.csv', index=False)
        
        return redirect(url_for('index'))

    
    return render_template("nuevo_caso.html")

@app.errorhandler(500)
def internal_server_error(e):
    """
    Manejador de error para errores internos del servidor (código 500).
    """
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)