# Seguimiento de Sueño y Bienestar

Aplicación web para el seguimiento diario de métricas relacionadas con el sueño, bienestar y entrenamiento.

## Características

- Registro diario de:
  - Calidad del sueño
  - Nivel de estrés
  - Nivel de energía
  - Dolor muscular
  - Nutrición
  - Hidratación
  - Detalles de entrenamiento (opcional)
    - Grupo muscular
    - Intensidad
    - Duración

- Visualización de datos:
  - Histórico detallado con barras de progreso
  - Gráficos de evolución temporal
  - Vista detallada de cada registro

## Tecnologías

- Python 3.x
- Flask
- Bootstrap 5
- Chart.js
- CSV para almacenamiento de datos

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/reval1212121212/seguimiento_sueno.git
cd seguimiento_sueno
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
seguimiento_sueno/
├── app.py              # Aplicación principal Flask
├── registro_sueno.csv  # Almacenamiento de datos
├── requirements.txt    # Dependencias del proyecto
└── templates/         # Plantillas HTML
    ├── base.html     # Plantilla base
    ├── index.html    # Formulario de registro
    ├── historico.html # Vista de registros
    └── graficos.html  # Gráficos de evolución
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios que te gustaría hacer.

## Licencia

Este proyecto está bajo la Licencia MIT.
