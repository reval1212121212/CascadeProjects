from flask import Flask, render_template, request, redirect, url_for, flash
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash_messages'  # Necesario para los mensajes flash

# Ruta al archivo CSV
CSV_FILE = 'registro_sueno.csv'

def asegurar_archivo_csv():
    """Asegura que el archivo CSV existe con los encabezados correctos"""
    if not os.path.isfile(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([
                'fecha', 
                'hora', 
                'calidad_sueno', 
                'nivel_estres',
                'energia',
                'dolor_muscular',
                'nutricion',
                'hidratacion',
                'entrenamiento_hoy',
                'grupo_muscular',
                'intensidad_entrenamiento',
                'duracion_entrenamiento',
                'comentarios'
            ])

def guardar_datos(datos):
    """Guarda los datos en un archivo CSV."""
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M")
    
    asegurar_archivo_csv()
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            fecha_actual,
            hora_actual,
            datos.get('calidad_sueno', ''),
            datos.get('nivel_estres', ''),
            datos.get('energia', ''),
            datos.get('dolor_muscular', ''),
            datos.get('nutricion', ''),
            datos.get('hidratacion', ''),
            datos.get('entrenamiento_hoy', 'No'),
            datos.get('grupo_muscular', ''),
            datos.get('intensidad_entrenamiento', ''),
            datos.get('duracion_entrenamiento', ''),
            datos.get('comentarios', '')
        ])
    
    return fecha_actual, hora_actual

def obtener_datos_historicos():
    """Obtiene los datos históricos del archivo CSV"""
    asegurar_archivo_csv()
    try:
        registros = []
        with open(CSV_FILE, 'r', newline='', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                registros.append(fila)
        return registros
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return []

@app.route('/')
def index():
    """Página principal con el formulario de registro"""
    return render_template('index.html', now=datetime.now())

@app.route('/registrar', methods=['POST'])
def registrar():
    """Procesa el formulario de registro"""
    datos = {
        'calidad_sueno': int(request.form.get('calidad_sueno', 5)),
        'nivel_estres': int(request.form.get('nivel_estres', 5)),
        'energia': int(request.form.get('energia', 5)),
        'dolor_muscular': int(request.form.get('dolor_muscular', 1)),
        'nutricion': int(request.form.get('nutricion', 5)),
        'hidratacion': int(request.form.get('hidratacion', 5)),
        'entrenamiento_hoy': request.form.get('entrenamiento_hoy', 'No'),
        'comentarios': request.form.get('comentarios', '')
    }
    
    # Si entrenó hoy, obtener detalles adicionales
    if datos['entrenamiento_hoy'] == 'Si':
        datos['grupo_muscular'] = request.form.get('grupo_muscular', '')
        datos['intensidad_entrenamiento'] = int(request.form.get('intensidad_entrenamiento', 5))
        datos['duracion_entrenamiento'] = int(request.form.get('duracion_entrenamiento', 60))
    
    fecha, hora = guardar_datos(datos)
    
    flash(f'Datos guardados correctamente para el {fecha} a las {hora}.')
    return redirect(url_for('historico'))

@app.route('/historico')
def historico():
    """Muestra el historial de registros"""
    registros = obtener_datos_historicos()
    return render_template('historico.html', registros=registros, now=datetime.now())

@app.route('/graficos')
def graficos():
    """Muestra los gráficos de evolución"""
    registros = obtener_datos_historicos()
    # Invertimos el orden para mostrar la evolución de izquierda a derecha
    registros.reverse()
    return render_template('graficos.html', datos=registros, now=datetime.now())

@app.route('/exportar')
def exportar():
    """Página para exportar datos"""
    return render_template('exportar.html', now=datetime.now())

if __name__ == '__main__':
    asegurar_archivo_csv()
    app.run(debug=True)
