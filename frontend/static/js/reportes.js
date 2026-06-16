// Gráficos del dashboard de reportes (módulo ES).
// Antes eran 6 funciones crearGrafico* casi idénticas; ahora comparten una
// factoría (crearChart) y un helper de color por umbral (colorPorPromedio).

const COLORS = {
  azul: "#2563eb",
  azulClaro: "#60a5fa",
  verde: "#10b981",
  verdeClaro: "#6ee7b7",
  rojo: "#ef4444",
  rojoClaro: "#fca5a5",
  amarillo: "#f59e0b",
  gris: "#6b7280",
};

// Color según umbral de aprobación (>=7 bien, >=4 justo, resto mal).
function colorPorPromedio(valor) {
  const p = Number(valor);
  if (p >= 7) return COLORS.verde;
  if (p >= 4) return COLORS.amarillo;
  return COLORS.rojo;
}

// Factoría común: resuelve el canvas, aplica el guard (sin canvas o sin datos
// no dibuja) y crea el Chart con options responsive + título.
function crearChart(canvasId, datos, { type, titulo, data, options = {} }) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !datos?.length) return;

  new Chart(canvas, {
    type,
    data,
    options: {
      responsive: true,
      ...options,
      plugins: {
        title: { display: true, text: titulo },
        ...(options.plugins || {}),
      },
    },
  });
}

function crearGraficoRendimiento(stats) {
  const datos = stats.promedio_por_evaluacion;
  crearChart("rendimientoChart", datos, {
    type: "line",
    titulo: "Evolución del rendimiento del curso",
    data: {
      labels: datos?.map((x) => x.evaluacion_titulo),
      datasets: [
        {
          label: "Promedio del curso",
          data: datos?.map((x) => Number(x.nota_promedio)),
          borderColor: COLORS.azul,
          backgroundColor: COLORS.azulClaro,
          tension: 0.3,
        },
        {
          label: "Nota mínima para aprobar",
          data: datos?.map(() => 4),
          borderColor: COLORS.rojo,
          borderDash: [8, 4],
          pointRadius: 0,
        },
      ],
    },
    options: { scales: { y: { min: 0, max: 10 } } },
  });
}

function crearGraficoTipos(stats) {
  const datos = stats.promedio_por_tipo;
  crearChart("tipoChart", datos, {
    type: "bar",
    titulo: "Promedio por tipo de evaluación",
    data: {
      labels: datos?.map((x) => x.nombre),
      datasets: [
        {
          label: "Promedio",
          data: datos?.map((x) => Number(x.promedio)),
          backgroundColor: datos?.map((x) => colorPorPromedio(x.promedio)),
        },
      ],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: { y: { min: 0, max: 10 } },
    },
  });
}

function crearGraficoEstado(stats) {
  const datos = stats.estado_cursada;
  crearChart("estadoChart", datos, {
    type: "pie",
    titulo: "Estado de cursada",
    data: {
      labels: datos?.map((x) => x.estado),
      datasets: [{ data: datos?.map((x) => x.cantidad), backgroundColor: [COLORS.verde, COLORS.rojo] }],
    },
  });
}

function crearGraficoDistribucion(stats) {
  const datos = stats.distribucion_notas;
  crearChart("notasChart", datos, {
    type: "bar",
    titulo: "Distribución de notas",
    data: {
      labels: datos?.map((x) => `Nota ${x.rango}`),
      datasets: [{ label: "Cantidad de alumnos", data: datos?.map((x) => x.cantidad), backgroundColor: COLORS.azul }],
    },
    options: { scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
  });
}

function crearGraficoAsistencia(stats) {
  const datos = stats.asistencia_por_clase;
  crearChart("asistenciaChart", datos, {
    type: "line",
    titulo: "Asistencia por clase",
    data: {
      labels: datos?.map((_, i) => `Clase ${i + 1}`),
      datasets: [
        {
          label: "% Asistencia",
          data: datos?.map((x) => (x.porcentaje === null ? 0 : Number(x.porcentaje))),
          borderColor: COLORS.verde,
          backgroundColor: COLORS.verdeClaro,
          tension: 0.3,
        },
      ],
    },
    options: {
      plugins: {
        tooltip: { callbacks: { title: (context) => datos[context[0].dataIndex].nombre } },
      },
      scales: { y: { min: 0, max: 100, title: { display: true, text: "% de asistencia" } } },
    },
  });
}

function crearGraficoPromedioPorAsistencia(stats) {
  const datos = stats.rendimiento;
  crearChart("promedioPorAsistenciaChart", datos, {
    type: "bar",
    titulo: "Relación entre asistencia y rendimiento",
    data: {
      labels: datos?.map((x) => x.rango),
      datasets: [
        {
          label: "Promedio >= 7",
          data: datos?.map((x) => Number(x.promedio)),
          backgroundColor: datos?.map((x) => colorPorPromedio(x.promedio)),
          borderColor: COLORS.azulClaro,
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: { tooltip: { callbacks: { label: (context) => `Promedio: ${context.parsed.y}` } } },
      scales: {
        x: { title: { display: true, text: "Porcentaje de asistencia" } },
        y: { beginAtZero: true, min: 0, max: 10, title: { display: true, text: "Promedio de notas" } },
      },
    },
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const dataContainer = document.getElementById("data-container-stats");
  if (!dataContainer) return;

  try {
    const stats = JSON.parse(dataContainer.getAttribute("data-json"));
    crearGraficoAsistencia(stats);
    crearGraficoDistribucion(stats);
    crearGraficoEstado(stats);
    crearGraficoRendimiento(stats);
    crearGraficoTipos(stats);
    crearGraficoPromedioPorAsistencia(stats);
  } catch (error) {
    console.error("Error al generar gráficos:", error);
  }
});
