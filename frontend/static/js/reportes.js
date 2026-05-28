document.addEventListener("DOMContentLoaded", function () {
    // Buscamos el elemento que guarda el JSON en crudo enviado desde Jinja2
    const dataContainer = document.getElementById('datos-stats-raw');
    
    // Si no estamos en la pestaña de estadísticas, el elemento no existirá, salimos elegantemente
    if (!dataContainer) return;

    try {
        const rawData = JSON.parse(dataContainer.getAttribute('data-json'));
        
        // Mapeamos las colecciones para los ejes del gráfico
        const etiquetas = rawData.map(item => item.evaluacion_titulo);
        const datosAprobados = rawData.map(item => item.aprobados);
        const datosDesaprobados = rawData.map(item => item.desaprobados);

        const ctx = document.getElementById('chartMetricas').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: etiquetas,
                datasets: [
                    {
                        label: 'Aprobados',
                        data: datosAprobados,
                        backgroundColor: '#10b981', // Machea con tu var --text-success
                        borderColor: '#059669',
                        borderWidth: 1
                    },
                    {
                        label: 'Desaprobados',
                        data: datosDesaprobados,
                        backgroundColor: '#ef4444', // Machea con tu var --text-danger
                        borderColor: '#dc2626',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            font: { family: "'Plus Jakarta Sans', sans-serif", weight: '500' }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Cantidad de alumnos', font: { weight: '600' } }
                    },
                    x: {
                        labels: etiquetas
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error al procesar las métricas de Chart.js:", error);
    }
});