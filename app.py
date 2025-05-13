from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)

# Cargar los casos y sus palabras clave desde el CSV
casos_df = pd.read_csv('casos_laborales.csv')

# Función para procesar el texto del usuario y devolver las soluciones
def procesar_texto_usuario(texto_usuario):
    texto_usuario = texto_usuario.lower()  # Convertir el texto a minúsculas
    palabras_clave_encontradas = {}

    # Reemplazamos caracteres no alfabéticos para mejorar la detección de palabras clave
    texto_usuario = re.sub(r'[^a-záéíóú\s]', '', texto_usuario)
    
    for index, row in casos_df.iterrows():
        palabras_clave = row['palabras_clave'].split(', ')  # Separar las palabras clave por coma
        for palabra in palabras_clave:
            if palabra in texto_usuario:
                if row['descripcion'] not in palabras_clave_encontradas:
                    palabras_clave_encontradas[row['descripcion']] = row['resolucion']
    
    # Convertimos el diccionario a una lista de respuestas
    respuestas = [{"caso": k, "resolucion": v} for k, v in palabras_clave_encontradas.items()]
    return respuestas

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        texto_usuario = request.form["descripcion"]
        respuestas = procesar_texto_usuario(texto_usuario)
        return render_template("resultado.html", respuestas=respuestas)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
