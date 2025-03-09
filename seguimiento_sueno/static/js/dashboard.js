/**
 * Dashboard.js - Script para mejorar la funcionalidad del dashboard de seguimiento de sueño
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Actualizar métricas del dashboard
    fetchDashboardData();

    // Añadir animación a las tarjetas métricas
    animateMetricCards();

    // Inicializar eventos para los filtros de fecha
    initDateFilters();

    // Inicializar gráficos si existe el contenedor
    if (document.getElementById('sleepQualityChart')) {
        initCharts();
    }
});

/**
 * Obtiene los datos del dashboard desde la API
 */
function fetchDashboardData() {
    fetch('/api/dashboard-data')
        .then(response => response.json())
        .then(data => {
            updateDashboardMetrics(data);
            updateTips(data);
            highlightBestMetrics(data);
        })
        .catch(error => {
            console.error('Error al obtener datos del dashboard:', error);
        });
}

/**
 * Actualiza las métricas del dashboard con los datos recibidos
 */
function updateDashboardMetrics(data) {
    // Actualizar valores de métricas
    updateMetric('sleepQualityValue', data.avg_sleep_quality);
    updateMetric('energyValue', data.avg_energy);
    updateMetric('hydrationValue', data.avg_hydration);
    updateMetric('workoutValue', data.training_count);
    
    // Actualizar barras de tendencia
    updateTrendBar('sleepQualityTrend', data.avg_sleep_quality * 10);
    updateTrendBar('energyTrend', data.avg_energy * 10);
    updateTrendBar('hydrationTrend', data.avg_hydration * 10);
    
    // Actualizar racha actual
    if (document.getElementById('currentStreak')) {
        document.getElementById('currentStreak').textContent = data.current_streak;
    }
    
    // Actualizar mejor racha
    if (document.getElementById('bestStreak')) {
        document.getElementById('bestStreak').textContent = data.best_streak;
    }
}

/**
 * Actualiza el valor de una métrica específica
 */
function updateMetric(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Si el valor es un número, formatearlo con un decimal
        if (!isNaN(value)) {
            element.textContent = Number(value).toFixed(1);
        } else {
            element.textContent = value;
        }
    }
}

/**
 * Actualiza la barra de tendencia de una métrica
 */
function updateTrendBar(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.width = `${percentage}%`;
    }
}

/**
 * Resalta las mejores métricas en el dashboard
 */
function highlightBestMetrics(data) {
    // Resaltar mejor día para dormir
    if (data.best_sleep_day && document.getElementById('bestSleepDay')) {
        document.getElementById('bestSleepDay').textContent = data.best_sleep_day;
    }
    
    // Resaltar mejor día para energía
    if (data.best_energy_day && document.getElementById('bestEnergyDay')) {
        document.getElementById('bestEnergyDay').textContent = data.best_energy_day;
    }
    
    // Añadir clases para métricas buenas/malas
    applyMetricStatus('sleepQualityMetric', data.avg_sleep_quality, 7);
    applyMetricStatus('energyMetric', data.avg_energy, 7);
    applyMetricStatus('hydrationMetric', data.avg_hydration, 7);
}

/**
 * Aplica clases de estado a las métricas según su valor
 */
function applyMetricStatus(elementId, value, threshold) {
    const element = document.getElementById(elementId);
    if (element) {
        if (value >= threshold) {
            element.classList.add('good-metric');
            element.classList.remove('bad-metric');
        } else if (value < threshold - 2) {
            element.classList.add('bad-metric');
            element.classList.remove('good-metric');
        } else {
            element.classList.remove('good-metric', 'bad-metric');
        }
    }
}

/**
 * Actualiza los consejos mostrados en el dashboard
 */
function updateTips(data) {
    // Ejemplo de consejos basados en los datos
    const tipsContainer = document.getElementById('tipsContainer');
    if (!tipsContainer) return;
    
    let tipsHTML = '';
    
    // Consejo para calidad de sueño
    if (data.avg_sleep_quality < 6) {
        tipsHTML += createTipHTML(
            'sleep-tip',
            'bi-moon-stars',
            'Mejora tu sueño',
            'Intenta acostarte a la misma hora todos los días y evita pantallas 1 hora antes de dormir.'
        );
    }
    
    // Consejo para hidratación
    if (data.avg_hydration < 6) {
        tipsHTML += createTipHTML(
            'hydration-tip',
            'bi-droplet-fill',
            'Aumenta tu hidratación',
            'Lleva una botella de agua contigo y establece recordatorios para beber agua regularmente.'
        );
    }
    
    // Consejo para recuperación
    if (data.avg_energy < 6) {
        tipsHTML += createTipHTML(
            'recovery-tip',
            'bi-battery-charging',
            'Mejora tu recuperación',
            'Considera añadir días de descanso activo y asegúrate de dormir al menos 7-8 horas.'
        );
    }
    
    // Si no hay consejos específicos, mostrar uno general
    if (tipsHTML === '') {
        tipsHTML = createTipHTML(
            'sleep-tip',
            'bi-check-circle',
            '¡Buen trabajo!',
            'Continúa con tus buenos hábitos. Considera registrar más detalles en tus comentarios.'
        );
    }
    
    tipsContainer.innerHTML = tipsHTML;
}

/**
 * Crea el HTML para un consejo
 */
function createTipHTML(iconClass, iconName, title, content) {
    return `
        <div class="tip-item">
            <div class="tip-icon ${iconClass}">
                <i class="bi ${iconName}"></i>
            </div>
            <div class="tip-content">
                <h5>${title}</h5>
                <p>${content}</p>
            </div>
        </div>
    `;
}

/**
 * Añade animaciones a las tarjetas de métricas
 */
function animateMetricCards() {
    const metricCards = document.querySelectorAll('.metric-card');
    
    metricCards.forEach((card, index) => {
        // Añadir un retraso escalonado para cada tarjeta
        setTimeout(() => {
            card.classList.add('animated');
        }, 100 * index);
    });
}

/**
 * Inicializa los filtros de fecha
 */
function initDateFilters() {
    const dateFilterButtons = document.querySelectorAll('.date-filter-btn');
    if (dateFilterButtons.length === 0) return;
    
    dateFilterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover clase activa de todos los botones
            dateFilterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Añadir clase activa al botón clickeado
            this.classList.add('active');
            
            // Aquí se implementaría la lógica para filtrar por fecha
            const filterType = this.dataset.filter;
            console.log(`Filtrar por: ${filterType}`);
            
            // Simular actualización de datos
            // En una implementación real, se haría una llamada a la API con el filtro
            fetchDashboardData();
        });
    });
}

/**
 * Inicializa los gráficos si Chart.js está disponible
 */
function initCharts() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js no está disponible');
        return;
    }
    
    // Configurar gráfico de calidad de sueño
    const sleepCtx = document.getElementById('sleepQualityChart').getContext('2d');
    const sleepChart = new Chart(sleepCtx, {
        type: 'line',
        data: {
            labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            datasets: [{
                label: 'Calidad de Sueño',
                data: [6, 7, 5, 8, 6, 9, 7],
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2
                    }
                }
            }
        }
    });
    
    // Configurar gráfico de energía
    const energyCtx = document.getElementById('energyChart').getContext('2d');
    const energyChart = new Chart(energyCtx, {
        type: 'line',
        data: {
            labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            datasets: [{
                label: 'Nivel de Energía',
                data: [7, 6, 8, 5, 7, 8, 9],
                borderColor: '#f6c23e',
                backgroundColor: 'rgba(246, 194, 62, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2
                    }
                }
            }
        }
    });
}
