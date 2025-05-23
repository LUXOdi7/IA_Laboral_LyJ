from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
import re
from urllib.parse import urlencode
import unicodedata

app = Flask(__name__)

# Cargar los casos y sus palabras clave desde el CSV
casos_df = pd.read_csv('casos_laborales.csv')

# Definir un diccionario de sinónimos
sinonimos = {
    "horas extras": ["sobretiempo", "horas extra", "tiempo extra", "extrajornada"],
    "no pagadas": ["impagas", "sin pagar", "adeudadas", "pendientes de pago"],
    "salario": ["sueldo", "remuneración", "paga", "haberes", "retribución"],
    "compensación": ["indemnización", "resarcimiento", "pago", "abono", "reparación"],
    "despido": ["cese", "terminación de contrato", "desvinculación", "rescisión laboral", "cesantía"],
    "sin justificación": ["injustificado", "arbitrario", "ilegal", "improcedente", "sin causa"],
    "acoso laboral": ["mobbing", "hostigamiento laboral", "abuso laboral", "maltrato laboral", "intimidación laboral"],
    "acoso": ["hostigamiento", "persecución", "intimidación", "molestia", "vejación"],
    "violencia": ["agresión", "maltrato", "abuso", "agresión física", "agresión verbal"],
    "hostigamiento": ["persecución", "acoso", "intimidación", "molestia", "vejación"],
    "condiciones de trabajo": ["ambiente laboral", "entorno de trabajo", "medio ambiente de trabajo", "condiciones laborales"],
    "inseguro": ["peligroso", "riesgoso", "precario", "vulnerable"],
    "seguridad": ["protección", "prevención", "cuidado", "resguardo", "bienestar"],
    "vacaciones": ["descanso vacacional", "días de descanso", "período vacacional", "licencia anual"],
    "discriminación": ["trato desigual", "marginación", "exclusión", "segregación", "prejuicio"],
    "robo": ["hurto", "sustracción", "apropiación indebida", "latrocinio"],
    "retraso": ["demora", "tardanza", "aplazo"],
    "estrés": ["tensión", "agotamiento", "presión"],
    "bajo rendimiento": ["baja productividad", "rendimiento deficiente", "ineficiencia"],
    "salud": ["bienestar", "sanidad", "condición física"],
    "trabajo": ["empleo", "labor", "ocupación", "puesto"],
    "sobrecarga": ["exceso de trabajo", "carga excesiva", "saturación"],
    "género": ["sexo"],
    "igualdad": ["equidad", "paridad"],
    "favoritismo": ["parcialidad", "preferencia", "amiguismo"],
    "tareas": ["funciones", "actividades", "cometidos"],
    "desigualdad": ["inequidad", "disparidad", "asimetría"],
    "injusto": ["inequitativo", "arbitrario", "parcial"],
    "pelea": ["disputa", "altercado", "riña", "enfrentamiento"],
    "conflicto": ["disputa", "problema", "desacuerdo", "controversia"],
    "compañero": ["colega", "colaborador", "camarada"],
    "comportamiento": ["conducta", "actitud", "proceder"],
    "no permitido": ["prohibido", "vetado", "ilegal"],
    "ley": ["norma", "regulación", "legislación", "reglamento"],
    "teléfono": ["celular", "móvil"],
    "uso": ["utilización", "manejo"],
    "política": ["normativa", "regla", "directriz"],
    "material": ["suministros", "insumos", "equipamiento"],
    "oficina": ["puesto de trabajo", "escritorio"],
    "sanción": ["castigo", "multa", "penalización", "disciplina"],
    "investigación": ["indagación", "averiguación", "pesquisa"],
    "razones políticas": ["motivos políticos"],
    "derechos": ["garantías", "prerrogativas", "facultades"],
    "raza": ["etnia", "origen étnico"],
    "comisiones": ["porcentajes", "bonificaciones por venta"],
    "ventas": ["comercialización", "negocios"],
    "horario": ["jornada", "turnos", "cronograma"],
    "flexible": ["adaptable", "maleable"],
    "cambio": ["modificación", "alteración"],
    "enfermedad": ["afección", "dolencia", "padecimiento"],
    "adaptación": ["ajuste", "acomodación"],
    "pago": ["abono", "remuneración", "salario"],
    "aumento": ["incremento", "subida", "alza"],
    "incumplimiento": ["falta", "violación", "quebrantamiento"],
    "evaluación": ["valoración", "apreciación", "examen"],
    "desempeño": ["rendimiento", "actuación", "ejecución"],
    "retroalimentación": ["feedback", "comentarios", "observaciones"],
    "justicia": ["equidad", "imparcialidad"],
    "obligación": ["deber", "compromiso", "responsabilidad"],
    "equipo": ["maquinaria", "instrumental", "herramientas"],
    "justificación": ["razón", "motivo", "fundamento"],
    "trato": ["manejo", "relación", "conducta"],
    "jefe": ["superior", "supervisor", "gerente", "líder"],
    "empleado": ["trabajador", "colaborador", "subordinado"],
    "comunicación": ["interacción", "diálogo", "contacto"],
    "privacidad": ["intimidad", "reserva", "confidencialidad"],
    "confidencialidad": ["secreto", "discreción", "privacidad"],
    "transparencia": ["claridad", "honestidad", "franqueza"],
    "decisiones": ["resoluciones", "determinaciones"],
    "empresa": ["compañía", "organización", "negocio"],
    "asignación": ["distribución", "reparto", "designación"],
    "acoso sexual": ["hostigamiento sexual"],
    "ideas": ["conceptos", "pensamientos", "propuestas"],
    "participación": ["colaboración", "intervención"],
    "contrato temporal": ["contrato a plazo fijo"],
    "licencia": ["permiso", "autorización"],
    "maternidad": ["embarazo", "postparto"],
    "solicitud": ["petición", "requerimiento"],
    "faltas": ["ausencias", "infracciones"],
    "descanso": ["reposo", "pausa", "receso"],
    "ajuste": ["adaptación", "modificación"],
    "teletrabajo": ["trabajo remoto", "home office"],
    "recursos": ["medios", "suministros", "materiales"],
    "insuficiente": ["escaso", "deficiente", "limitado"],
    "acoso verbal": ["maltrato verbal", "abuso verbal"],
    "turno": ["jornada", "horario"],
    "tiempo": ["período", "lapso"],
    "mala conducta": ["mal comportamiento", "conducta inapropiada"],
    "acusación": ["denuncia", "imputación"],
    "pruebas": ["evidencias", "demostraciones"],
    "herramientas": ["instrumentos", "utensilios"],
    "equidad": ["justicia", "imparcialidad", "igualdad"],
    "experiencia": ["conocimiento", "práctica"],
    "distribución": ["reparto", "asignación"],
    "acusación falsa": ["falsa denuncia", "calumnia"],
    "transferencia": ["traslado", "cambio de puesto"],
    "cuidado familiar": ["atención familiar"],
    "copia": ["duplicado", "ejemplar"],
    "estacionamiento": ["parqueo", "aparcamiento"],
    "privilegios": ["beneficios", "ventajas"],
    "feriados": ["días festivos", "fiestas"],
    "pago diferencial": ["pago extra", "recargo"],
    "recargos": ["adicionales", "suplementos"],
    "documento en blanco": ["documento sin llenar"],
    "fraude": ["engaño", "estafa", "dolo"],
    "ética": ["moral", "principios"],
    "alimentos": ["comida", "víveres"],
    "prohibición": ["veto", "impedimento"],
    "bienestar laboral": ["salud ocupacional", "ambiente saludable"],
    "uniforme": ["vestimenta de trabajo"],
    "higiene": ["limpieza", "aseo"],
    "cambio de funciones": ["modificación de tareas"],
    "unilateral": ["arbitrario", "impuesto"],
    "acuerdo": ["consenso", "pacto"],
    "pertenencias": ["objetos personales", "bienes"],
    "seguridad personal": ["integridad física"],
    "agua potable": ["agua para beber"],
    "condiciones básicas": ["requisitos mínimos"],
    "título profesional": ["grado académico", "profesión"],
    "categoría": ["nivel", "rango"],
    "remuneración": ["salario", "sueldo"],
    "exámenes médicos": ["chequeos médicos", "revisiones de salud"],
    "permisos": ["licencias", "autorizaciones"],
    "temperaturas extremas": ["clima extremo"],
    "ambiente": ["entorno", "medio"],
    "asistencia": ["presencia", "concurrencia"],
    "registro": ["anotación", "control"],
    "manipulación": ["alteración", "modificación fraudulenta"],
    "certificado": ["constancia", "credencial"],
    "constancia": ["prueba", "evidencia"],
    "documentos": ["papeles", "expedientes"],
    "retención": ["incautación", "detención"],
    "extranjero": ["foráneo", "inmigrante"],
    "sillas": ["asientos"],
    "ergonomía": ["comodidad", "adaptación"],
    "computadora": ["ordenador", "PC"],
    "tecnología": ["informática", "sistemas"],
    "obsolescencia": ["antigüedad", "desuso"],
    "sindicato": ["gremio", "unión laboral"],
    "cobro ilegal": ["cargo indebido"],
    "reembolso": ["devolución", "reintegro"],
    "emergencias": ["urgencias", "contingencias"],
    "protocolo": ["procedimiento", "norma"],
    "primeros auxilios": ["asistencia inicial"],
    "humedad": ["moho", "condensación"],
    "infraestructura": ["instalaciones", "estructura"],
    "mantenimiento": ["reparación", "conservación"],
    "ventilación": ["aireación", "circulación de aire"],
    "cámaras": ["videocámaras", "cámaras de vigilancia"],
    "vigilancia": ["supervisión", "monitoreo"],
    "metas": ["objetivos", "logros", "cuotas"],
    "presión laboral": ["estrés laboral", "exigencia laboral"],
    "indicadores": ["métricas", "parámetros"],
    "discapacidad": ["minusvalía", "diversidad funcional"],
    "accesibilidad": ["facilidad de acceso"],
    "inclusión": ["integración"],
    "seguro médico": ["póliza de salud", "seguro de salud"],
    "cancelación": ["anulación", "rescisión"],
    "duelo": ["luto", "pena"],
    "apoyo emocional": ["soporte psicológico"],
    "vehículo": ["automóvil", "coche"],
    "rumores": ["chismes", "habladurías"],
    "acoso psicológico": ["maltrato psicológico", "hostigamiento psicológico"],
    "reputación": ["fama", "prestigio"],
    "capacitación": ["formación", "entrenamiento", "cualificación"],
    "desarrollo": ["crecimiento", "progreso"],
    "habilidades": ["destrezas", "capacidades"],
    "bono": ["gratificación", "prima", "incentivo"],
    "renuncia": ["dimisión", "abandono de puesto"],
    "liquidación": ["finiquito", "pago final"],
    "cláusulas": ["condiciones", "estipulaciones"],
    "exceso": ["abuso", "demasía"],
    "radiación": ["emisión", "exposición"],
    "cobro": ["cargo", "facturación"],
    "home office": ["teletrabajo", "trabajo desde casa"],
    "flexibilidad": ["adaptabilidad", "elasticidad"],
    "cliente": ["usuario", "consumidor"],
    "apoyo": ["ayuda", "soporte"],
    "software": ["programa informático", "aplicación"],
    "licencia": ["permiso de uso"],
    "legalidad": ["legitimidad", "conformidad con la ley"],
    "antigüedad": ["años de servicio", "experiencia"],
    "reconocimiento": ["valoración", "apreciación"],
    "beneficios": ["ventajas", "prestaciones"],
    "ascenso": ["promoción", "subida de puesto"],
    "meritocracia": ["mérito", "reconocimiento por mérito"],
    "nepotismo": ["amiguismo", "favoritismo familiar"],
    "contrataciones": ["reclutamiento", "selección de personal"],
    "altura": ["altitud"],
    "bonificación": ["extra", "incentivo"],
    "riesgo": ["peligro", "amenaza"],
    "trámites": ["gestiones", "diligencias"],
    "embarazo": ["gestación", "gravidez"],
    "contratación": ["empleo", "ingreso"],
    "zona peligrosa": ["área de riesgo"],
    "reubicación": ["traslado", "cambio de ubicación"],
    "reciclaje": ["reutilización", "gestión de residuos"],
    "medio ambiente": ["entorno natural"],
    "sostenibilidad": ["sustentabilidad", "ecología"],
    "turno nocturno": ["jornada nocturna"],
    "vestimenta": ["ropa", "atuendo"],
    "clima": ["ambiente", "temperatura"],
    "ruido": ["sonido", "estruendo"],
    "salud ocupacional": ["seguridad y salud en el trabajo"],
    "preparación": ["formación", "entrenamiento"],
    "lactancia": ["amamantamiento"],
    "festivos": ["días feriados", "fiestas"],
    "religión": ["credo", "culto"],
    "enfermedad profesional": ["enfermedad laboral"],
    "violencia doméstica": ["violencia intrafamiliar"],
    "descuento": ["deducción", "rebaja"],
    "planilla": ["nómina", "salarios"],
    "error": ["equivocación", "fallo"],
    "injusticia": ["inequidad", "arbitrariedad"],
    "abuso": ["maltrato", "exceso"],
    "jornada": ["horario de trabajo", "día laboral"],
    "enfermedad": ["padecimiento", "malestar"],
    "madre": ["progenitora"],
    "boletas": ["recibos", "comprobantes de pago"],
    "mensual": ["cada mes"],
    "ESSALUD": ["seguro social", "seguro de salud"],
    "omisión": ["falta", "negligencia"],
    "afiliación": ["inscripción", "registro"],
    "funciones": ["tareas", "responsabilidades"],
    "aviso": ["notificación", "comunicado"],
    "supervisor": ["jefe", "encargado"],
    "feriado": ["día festivo"],
    "pago": ["abono", "remuneración"],
    "exceso": ["abuso", "demasía"],
    "accidente": ["incidente", "percance"],
    "contrato": ["acuerdo", "convenio"],
    "informalidad": ["ilegalidad", "precariedad"],
    "reducción": ["disminución", "recorte"],
    "sin aviso": ["sin notificación"],
    "grabación": ["registro de audio/video"],
    "consentimiento": ["acuerdo", "aprobación"],
    "vigilancia": ["monitoreo", "supervisión"],
    "refrigerio": ["descanso para comer"],
    "degradación": ["humillación", "desprestigio"],
    "público": ["abierto", "conocido"],
    "seguro": ["póliza", "cobertura"],
    "exclusión": ["marginación", "apartamiento"],
    "constancia": ["certificado", "comprobante"],
    "cese": ["despido", "terminación"],
    "documento": ["papel", "escrito"],
    "limpieza": ["aseo", "higiene"],
    "coerción": ["presión", "amenaza"],
    "señas": ["lenguaje de señas", "gestos"],
    "asueto": ["día libre", "descanso"],
    "recados": ["encargos", "mensajes"],
    "personal": ["privado"],
    "expediente": ["archivo", "legajo"],
    "información": ["datos", "conocimiento"],
    "baños": ["servicios higiénicos"],
    "reposición": ["reemplazo", "sustitución"],
    "no registrado": ["no declarado", "en negro"],
    "cáncer": ["neoplasia", "tumor"],
    "paternidad": ["padre", "paternidad"],
    "defectuoso": ["fallido", "averiado"],
    "indemnización": ["compensación", "resarcimiento"],
    "protector solar": ["bloqueador solar"],
    "piel": ["cutis", "dermis"],
    "historial": ["antecedentes", "historia"],
    "viáticos": ["gastos de viaje", "dietas"],
    "viaje": ["traslado", "desplazamiento"],
    "gastos": ["costos", "desembolsos"],
    "reestructuración": ["reorganización", "reajuste"],
    "lluvia": ["precipitación"],
    "boleta electrónica": ["factura electrónica"],
    "SUNAT": ["administración tributaria"],
    "años de servicio": ["antigüedad laboral"],
    "no capacitado": ["sin formación", "inexperto"],
    "retención": ["detención", "descuento"],
    "ilegal": ["ilícito", "antijurídico"],
    "examen médico": ["chequeo médico"],
    "ocupacional": ["laboral", "profesional"],
    "gratificación": ["bono", "extra"],
    "cierre": ["finalización"],
    "beneficio": ["ventaja", "provecho"],
    "mascarilla": ["cubrebocas", "barbijo"],
    "químicos": ["sustancias químicas"],
    "título técnico": ["diploma técnico"],
    "dominical": ["domingo", "día festivo"],
    "fin de semana": ["sábado y domingo"],
    "comedor": ["cafetería", "refectorio"],
    "alimentación": ["nutrición", "comida"],
    "médula": ["médula ósea"],
    "donación": ["entrega", "aportación"],
    "huelga": ["paro", "cese de actividades"],
    "sindicato": ["gremio", "asociación de trabajadores"],
    "represalia": ["venganza", "revancha"],
    "prenatal": ["pre-parto"],
    "presión": ["tensión", "estrés"],
    "productividad": ["rendimiento", "eficiencia"],
    "inventario": ["recuento", "existencias"],
    "verificación": ["comprobación", "revisión"],
    "alergia": ["hipersensibilidad"],
    "medicamentos": ["fármacos", "medicinas"],
    "receta": ["prescripción médica"],
    "SOAT": ["seguro obligatorio de accidentes de tránsito"],
    "colecta": ["recolecta", "recaudación"],
    "regalo": ["obsequio", "presente"],
    "rampas": ["accesos", "pendientes"],
    "barreras": ["obstáculos", "impedimentos"],
    "perfume": ["fragancia", "aroma"],
    "convivencia": ["coexistencia", "armonía"],
    "certificados": ["documentos", "constancias"],
    "ideas": ["conceptos", "propuestas"],
    "plagio": ["copia", "robo de ideas"],
    "creatividad": ["ingenio", "originalidad"],
    "contraseñas": ["claves", "passwords"],
    "correo": ["email"],
    "TI": ["tecnologías de la información"],
    "sangre": ["plasma"],
    "responsabilidad social": ["compromiso social"],
    "pánico": ["miedo", "terror"],
    "emergencia": ["urgencia", "crisis"],
    "psicológico": ["mental", "emocional"],
    "apodos": ["sobrenombres", "motes"],
    "denigrante": ["humillante", "ofensivo"],
    "identidad": ["ser", "esencia"],
    "respeto": ["consideración", "estima"],
    "dieta": ["régimen alimenticio"],
    "lentes": ["gafas", "anteojos"],
    "luz": ["iluminación"],
    "ojos": ["vista"],
    "producción": ["fabricación", "elaboración"],
    "equipos": ["aparatos", "maquinaria"],
    "daños": ["deterioros", "perjuicios"],
    "desgaste": ["deterioro", "abrasión"],
    "memes": ["imágenes virales"],
    "ofensivo": ["insultante", "agresivo"],
    "redes": ["internet", "plataformas"],
    "terapia": ["tratamiento"],
    "rehabilitación": ["recuperación"],
    "luz natural": ["luz solar"],
    "reloj": ["marcador"],
    "control": ["supervisión"],
    "ropa": ["vestimenta"],
    "marca": ["firma", "emblema"],
    "traductor": ["intérprete"],
    "idioma": ["lengua"],
    "ocultamiento": ["encubrimiento"],
    "VIH": ["SIDA"],
    "mochilas": ["bolsos", "bultos"],
    "revisión": ["inspección"],
    "visitas": ["recepciones"],
    "mobiliario": ["muebles"],
    "atención": ["servicio"],
    "apps": ["aplicaciones"],
    "celular": ["móvil"],
    "datos": ["información"],
    "agua caliente": ["agua templada"],
    "invierno": ["estación fría"],
    "facturas": ["recibos", "comprobantes"],
    "ausencia": ["falta", "incomparecencia"],
    "voto": ["sufragio"],
    "elecciones": ["comicios"],
    "hijo": ["descendiente"],
    "cuidado": ["atención"],
    "acta": ["registro", "minuta"],
    "reunión": ["encuentro", "sesión"],
    "epilepsia": ["convulsiones"],
    "burlas": ["mofas", "escarnios"],
    "fertilidad": ["fecundidad"],
    "humedad": ["condensación", "moho"],
    "hongos": ["moho"],
    "lentes de sol": ["gafas de sol"],
    "rayos uv": ["radiación ultravioleta"],
    "montaña": ["sierra"],
    "maquinaria": ["equipo", "aparato"],
    "audiometría": ["prueba de audición"],
    "decibeles": ["unidades de sonido"],
    "edad": ["años"],
    "químicos": ["sustancias tóxicas"],
    "software pirata": ["software ilegal"],
    "cirugía": ["operación"],
    "familia": ["parientes"],
    "turno rotativo": ["horario rotativo"],
    "grave": ["serio", "severo"],
    "calor": ["alta temperatura"],
    "extranjero": ["forastero", "inmigrante"],
    "desierto": ["zona árida"],
    "obra": ["construcción"],
    "látex": ["goma"],
    "depresión": ["tristeza profunda"],
    "amianto": ["asbesto"],
    "adopción": ["acogimiento"],
    "petrolera": ["empresa de petróleo"],
    "blanco": ["vacío"],
    "próstata": ["glándula prostática"],
    "tercerizado": ["subcontratado", "externo"],
    "keylogger": ["registrador de teclado"],
    "espionaje": ["vigilancia secreta"],
    "dermatitis": ["inflamación de la piel"],
    "crema": ["ungüento"],
    "frontera": ["límite", "borde"],
    "liderazgo": ["dirección", "gestión"],
    "dosímetro": ["medidor de radiación"],
    "túnel carpiano": ["síndrome del túnel carpiano"],
    "cáncer de mama": ["cáncer de seno"]
}

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
    con las palabras clave (y sus sinónimos) en el texto del usuario.

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
            # Verificar sinónimos
            if palabra in sinonimos:
                for sinonimo in sinonimos[palabra]:
                    if preprocesar_texto(sinonimo) in texto_usuario:
                        soluciones_encontradas.append({
                            "descripcion": row['descripcion'],
                            "resolucion": row['resolucion'],
                            "procedimiento": row['procedimiento'],
                            "ley": row['ley'],
                            "index": index
                        })
                        break
                else:
                    continue
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

@app.errorhandler(500)
def internal_server_error(e):
    """
    Manejador de error para errores internos del servidor (código 500).
    """
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
