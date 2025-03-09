/**
 * historico.js - Script para mejorar la funcionalidad de la página de historial
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar las barras de progreso
    initProgressBars();
    
    // Añadir efectos visuales a las filas de registros
    enhanceRecordRows();
    
    // Inicializar tooltips de Bootstrap
    initTooltips();
});

/**
 * Inicializa las barras de progreso aplicando los anchos desde los atributos data
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width) {
            bar.style.width = width + '%';
        }
    });
}

/**
 * Añade efectos visuales a las filas de registros
 */
function enhanceRecordRows() {
    const rows = document.querySelectorAll('.record-row');
    
    rows.forEach((row, index) => {
        // Añadir un retraso escalonado para cada fila
        setTimeout(() => {
            row.classList.add('fade-in');
        }, 50 * index);
        
        // Añadir efecto hover
        row.addEventListener('mouseenter', function() {
            this.classList.add('row-highlight');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('row-highlight');
        });
    });
}

/**
 * Inicializa los tooltips de Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Función para filtrar registros por fecha
 */
function filterRecords(period) {
    console.log(`Filtrando registros por: ${period}`);
    // Aquí se implementaría la lógica para filtrar los registros
    // Esta es una función de ejemplo que podría expandirse en el futuro
}

/**
 * Función para exportar datos a CSV
 */
function exportToCSV() {
    console.log('Exportando datos a CSV...');
    // Aquí se implementaría la lógica para exportar los datos
    // Esta es una función de ejemplo que podría expandirse en el futuro
}
