from datetime import datetime
from flask import Blueprint, request, redirect, url_for

from utils.filtros_fecha import FORMATO_BACKEND

# Estados posibles de una entrega (espeja ESTADOS_ENTREGA del backend).
ESTADOS_ENTREGA = ["entregado", "tarde", "rehacer"]

MESES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _parsear_fecha_eval(valor):
    """RFC 1123 -> date (o None si no parsea)."""
    try:
        return datetime.strptime(valor, FORMATO_BACKEND).date()
    except (ValueError, TypeError):
        return None


# Filas por página por defecto y valores permitidos del selector (backend limita a 100).
ALUMNOS_POR_PAGINA = 10
PAGE_SIZES_PERMITIDOS = [10, 20, 50, 100]


def _volver_a_evaluacion(curso_id, evaluacion_id):
    """Redirige a la record page preservando página y filas por página (tabla paginada)."""
    return redirect(url_for(
        "evaluaciones.ver_evaluacion",
        curso_id=curso_id,
        evaluacion_id=evaluacion_id,
        page=request.form.get("page", type=int),
        page_size=request.form.get("page_size", type=int),
    ))


evaluaciones_bp = Blueprint("evaluaciones", __name__)

# Importar los submódulos al final para que registren sus rutas sobre evaluaciones_bp.
from routes.evaluaciones import evaluaciones, equipos, entregas, notas, integrantes  # noqa: E402,F401

__all__ = ["evaluaciones_bp"]
