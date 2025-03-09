from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import csv
from datetime import datetime
import json
from collections import defaultdict
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_la_aplicacion'

# Definir la ruta del archivo CSV
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos_sueno.csv')

# Definir los encabezados del CSV
CSV_HEADERS = [
    'fecha', 'calidad_sueno', 'nivel_estres', 'energia', 'dolor_muscular', 
    'nutricion', 'hidratacion', 'entrenamiento_hoy', 'grupo_muscular', 
    'intensidad_entrenamiento', 'duracion_entrenamiento', 'comentarios'
]

def asegurar_archivo_csv():
    """Asegura que el archivo CSV existe y tiene los encabezados correctos."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(CSV_HEADERS)

@app.route('/')
def index():
    """Página principal con el formulario para registrar datos."""
    asegurar_archivo_csv()
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    """Procesa el formulario y guarda los datos en el CSV."""
    asegurar_archivo_csv()
    
    # Obtener los datos del formulario
    datos = {
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'calidad_sueno': int(request.form.get('calidad_sueno', 5)),
        'nivel_estres': int(request.form.get('nivel_estres', 5)),
        'energia': int(request.form.get('energia', 5)),
        'dolor_muscular': int(request.form.get('dolor_muscular', 1)),
        'nutricion': int(request.form.get('nutricion', 5)),
        'hidratacion': int(request.form.get('hidratacion', 5)),
        'entrenamiento_hoy': request.form.get('entrenamiento_hoy', 'No'),
        'grupo_muscular': request.form.get('grupo_muscular', '') if request.form.get('entrenamiento_hoy') == 'Si' else '',
        'intensidad_entrenamiento': int(request.form.get('intensidad_entrenamiento', 0)) if request.form.get('entrenamiento_hoy') == 'Si' else 0,
        'duracion_entrenamiento': int(request.form.get('duracion_entrenamiento', 0)) if request.form.get('entrenamiento_hoy') == 'Si' else 0,
        'comentarios': request.form.get('comentarios', '')
    }
    
    # Guardar los datos en el CSV
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CSV_HEADERS)
        escritor.writerow(datos)
    
    flash('Datos registrados correctamente', 'success')
    return redirect(url_for('index'))

@app.route('/historico')
def historico():
    """Muestra el historial de registros."""
    asegurar_archivo_csv()
    registros = obtener_datos_historicos()
    return render_template('historico.html', registros=registros)

@app.route('/graficos')
def graficos():
    """Muestra gráficos de los datos registrados."""
    asegurar_archivo_csv()
    datos = obtener_datos_para_graficos()
    return render_template('graficos.html', datos=datos)

@app.route('/eliminar/<timestamp>', methods=['POST'])
def eliminar_registro(timestamp):
    """Elimina un registro específico basado en la fecha y hora."""
    asegurar_archivo_csv()
    
    # Obtener todos los registros
    registros = obtener_datos_historicos()
    
    # Filtrar para excluir el registro que se quiere eliminar
    registros_filtrados = [r for r in registros if r['fecha'] != timestamp]
    
    # Si no se encontró ningún registro para eliminar
    if len(registros_filtrados) == len(registros):
        flash('No se encontró el registro especificado', 'danger')
        return redirect(url_for('historico'))
    
    # Sobrescribir el archivo CSV con los registros filtrados
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CSV_HEADERS)
        escritor.writeheader()
        for registro in registros_filtrados:
            escritor.writerow(registro)
    
    flash('Registro eliminado correctamente', 'success')
    return redirect(url_for('historico'))

@app.route('/exportar-datos')
def exportar_datos():
    """Exporta todos los datos a un archivo CSV descargable."""
    asegurar_archivo_csv()
    
    # Crear un DataFrame con los datos
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        
        # Crear un buffer en memoria para el archivo
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        # Nombre del archivo con la fecha actual
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f'datos_sueno_{fecha_actual}.csv'
        
        return send_file(
            output,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f'Error al exportar datos: {str(e)}', 'danger')
        return redirect(url_for('historico'))

@app.route('/api/dashboard-data')
def dashboard_data():
    """API que devuelve datos para el dashboard."""
    asegurar_archivo_csv()
    
    # Obtener todos los registros
    registros = obtener_datos_historicos()
    
    # Si no hay registros, devolver datos vacíos
    if not registros:
        return jsonify({
            'avg_sleep_quality': 0,
            'avg_energy': 0,
            'avg_hydration': 0,
            'training_count': 0,
            'streak_count': 0,
            'best_sleep_day': '-',
            'best_energy_day': '-'
        })
    
    # Calcular promedios de los últimos 7 días (o menos si no hay suficientes registros)
    ultimos_registros = registros[:min(7, len(registros))]
    
    # Calcular promedios
    avg_sleep_quality = sum(r['calidad_sueno'] for r in ultimos_registros) / len(ultimos_registros)
    avg_energy = sum(r['energia'] for r in ultimos_registros) / len(ultimos_registros)
    avg_hydration = sum(r['hidratacion'] for r in ultimos_registros) / len(ultimos_registros)
    
    # Contar entrenamientos en los últimos 7 días
    training_count = sum(1 for r in ultimos_registros if r['entrenamiento_hoy'] == 'Si')
    
    # Calcular racha de días consecutivos con registros
    streak_count = calcular_racha_dias(registros)
    
    # Encontrar el mejor día de sueño y energía
    mejor_sueno = max(registros, key=lambda x: x['calidad_sueno'])
    mejor_energia = max(registros, key=lambda x: x['energia'])
    
    # Formatear fechas para mejor visualización
    mejor_sueno_fecha = datetime.strptime(mejor_sueno['fecha'].split()[0], '%Y-%m-%d').strftime('%d/%m')
    mejor_energia_fecha = datetime.strptime(mejor_energia['fecha'].split()[0], '%Y-%m-%d').strftime('%d/%m')
    
    return jsonify({
        'avg_sleep_quality': avg_sleep_quality,
        'avg_energy': avg_energy,
        'avg_hydration': avg_hydration,
        'training_count': training_count,
        'streak_count': streak_count,
        'best_sleep_day': mejor_sueno_fecha,
        'best_energy_day': mejor_energia_fecha
    })

def calcular_racha_dias(registros):
    """Calcula la racha actual de días consecutivos con registros."""
    if not registros:
        return 0
    
    # Obtener fechas únicas de los registros (solo la parte de la fecha, no la hora)
    fechas = [r['fecha'].split()[0] for r in registros]
    fechas_unicas = sorted(set(fechas), reverse=True)  # Ordenar de más reciente a más antigua
    
    # Si solo hay un día, la racha es 1
    if len(fechas_unicas) == 1:
        return 1
    
    # Convertir fechas a objetos datetime
    fechas_dt = [datetime.strptime(fecha, '%Y-%m-%d') for fecha in fechas_unicas]
    
    # Calcular racha
    racha = 1
    for i in range(len(fechas_dt) - 1):
        # Calcular diferencia en días entre fechas consecutivas
        diff = (fechas_dt[i] - fechas_dt[i+1]).days
        
        # Si la diferencia es 1 día, incrementar la racha
        if diff == 1:
            racha += 1
        else:
            # Si hay un hueco, terminar el cálculo
            break
    
    return racha

def obtener_datos_historicos():
    """Obtiene todos los datos históricos del CSV."""
    if not os.path.exists(CSV_FILE):
        return []
    
    registros = []
    with open(CSV_FILE, 'r', newline='', encoding='utf-8-sig') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            # Convertir valores numéricos a enteros
            for campo in ['calidad_sueno', 'nivel_estres', 'energia', 'dolor_muscular', 
                         'nutricion', 'hidratacion', 'intensidad_entrenamiento', 'duracion_entrenamiento']:
                if fila[campo] and fila[campo].isdigit():
                    fila[campo] = int(fila[campo])
                else:
                    fila[campo] = 0
            
            registros.append(fila)
    
    # Ordenar registros por fecha (más reciente primero)
    registros.sort(key=lambda x: x['fecha'], reverse=True)
    return registros

def obtener_datos_para_graficos():
    """Prepara los datos para los gráficos."""
    registros = obtener_datos_historicos()
    
    # Invertir el orden para que los gráficos muestren evolución cronológica
    registros.reverse()
    
    # Preparar datos para gráficos
    fechas = [r['fecha'].split()[0] for r in registros]  # Solo la parte de la fecha
    calidad_sueno = [r['calidad_sueno'] for r in registros]
    nivel_estres = [r['nivel_estres'] for r in registros]
    energia = [r['energia'] for r in registros]
    dolor_muscular = [r['dolor_muscular'] for r in registros]
    nutricion = [r['nutricion'] for r in registros]
    hidratacion = [r['hidratacion'] for r in registros]
    
    # Datos de entrenamiento
    entrenamientos = []
    for r in registros:
        if r['entrenamiento_hoy'] == 'Si':
            entrenamientos.append({
                'fecha': r['fecha'].split()[0],
                'grupo_muscular': r['grupo_muscular'],
                'intensidad': r['intensidad_entrenamiento'],
                'duracion': r['duracion_entrenamiento']
            })
    
    # Agrupar entrenamientos por grupo muscular
    grupos_musculares = defaultdict(int)
    for e in entrenamientos:
        if e['grupo_muscular']:
            grupos_musculares[e['grupo_muscular']] += 1
    
    # Convertir a formato para gráficos
    grupos_labels = list(grupos_musculares.keys())
    grupos_values = list(grupos_musculares.values())
    
    return {
        'fechas': fechas,
        'calidad_sueno': calidad_sueno,
        'nivel_estres': nivel_estres,
        'energia': energia,
        'dolor_muscular': dolor_muscular,
        'nutricion': nutricion,
        'hidratacion': hidratacion,
        'entrenamientos': entrenamientos,
        'grupos_musculares': {
            'labels': grupos_labels,
            'values': grupos_values
        }
    }

if __name__ == '__main__':
    app.run(debug=True)
