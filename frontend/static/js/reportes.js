document.addEventListener("DOMContentLoaded", function () {

    const dataContainer = document.getElementById("data-container-stats");

    if (!dataContainer) return;

    try {
        const stats = JSON.parse(
            dataContainer.getAttribute("data-json")
        );
        crearGraficoAsistencia(stats);
        crearGraficoDistribucion(stats);
        crearGraficoEstado(stats);
        crearGraficoRendimiento(stats);
        crearGraficoTipos(stats);
    } catch (error) {
        console.error("Error al generar gráficos:", error);
    }
});


const COLORS = {
    azul: "#2563eb",
    azulClaro: "#60a5fa",
    verde: "#10b981",
    verdeClaro: "#6ee7b7",
    rojo: "#ef4444",
    rojoClaro: "#fca5a5",
    amarillo: "#f59e0b",
    gris: "#6b7280"
};


function crearGraficoRendimiento(stats) {
    const datos = stats.promedio_por_evaluacion;
    const canvas = document.getElementById("rendimientoChart");
    if (!canvas || !datos?.length) return;

    new Chart(canvas, {
        type: "line",
        data: {
            labels: datos.map(x => x.evaluacion_titulo),
            datasets: [
                {
                    label: "Promedio del curso",
                    data: datos.map(x => Number(x.nota_promedio)),
                    borderColor: COLORS.azul,
                    backgroundColor: COLORS.azulClaro,
                    tension: 0.3
                },
                {
                    label: "Nota mínima para aprobar",
                    data: datos.map(() => 4),
                    borderColor: COLORS.rojo,
                    borderDash: [8, 4],
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Evolución del rendimiento del curso"
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 10
                }
            }
        }
    });
}


function crearGraficoTipos(stats) {

    const datos = stats.promedio_por_tipo;

    const canvas = document.getElementById("tipoChart");

    if (!canvas || !datos?.length) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: datos.map(x => x.nombre),
            datasets: [{
                label: "Promedio",
                data: datos.map(x => Number(x.promedio)),
                backgroundColor: [
                    COLORS.azul,
                    COLORS.verde,
                    COLORS.amarillo,
                    COLORS.rojo
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Promedio por tipo de evaluación"
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 10
                }
            }
        }
    });
}


function crearGraficoEstado(stats) {

    const datos = stats.estado_cursada;

    const canvas = document.getElementById("estadoChart");

    if (!canvas || !datos?.length) return;

    new Chart(canvas, {
        type: "pie",
        data: {
            labels: datos.map(x => x.estado),
            datasets: [{
                data: datos.map(x => x.cantidad),
                backgroundColor: [
                    COLORS.verde,
                    COLORS.rojo
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Estado de cursada"
                }
            }
        }
    });
}


function crearGraficoDistribucion(stats) {

    const datos = stats.distribucion_notas;

    const canvas = document.getElementById("notasChart");

    if (!canvas || !datos?.length) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: datos.map(x => `Nota ${x.rango}`),
            datasets: [{
                label: "Cantidad de alumnos",
                data: datos.map(x => x.cantidad),
                backgroundColor: COLORS.azul
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Distribución de notas"
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}


function crearGraficoAsistencia(stats) {

    const datos = stats.asistencia_por_clase;

    const canvas = document.getElementById("asistenciaChart");

    if (!canvas || !datos?.length) return;

    new Chart(canvas, {
        type: "line",
        data: {
            labels: datos.map((_, i) => `Clase ${i + 1}`),
            datasets: [{
                label: "% Asistencia",
                data: datos.map(x =>
                    x.porcentaje === null
                        ? 0
                        : Number(x.porcentaje)
                ),
                borderColor: COLORS.verde,
                backgroundColor: COLORS.verdeClaro,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: "Asistencia por clase"
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return datos[context[0].dataIndex].nombre;
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: "% de asistencia"
                    }
                }
            }
        }
    });
}