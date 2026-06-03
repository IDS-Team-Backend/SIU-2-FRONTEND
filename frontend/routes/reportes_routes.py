import os
from flask import Blueprint, render_template, request, flash, make_response
from pathlib import Path
import json

from services.decorators import requiere_staff
from services.reportes_service import (
    obtener_alumnos_reporte,
    obtener_estadisticas_reporte,
    obtener_equipos_reporte,
)

reportes_bp = Blueprint("reportes", __name__)
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

MOCKS_DIR = Path(__file__).parent.parent / "mocks"

def _load_mock(filename):
    try:
        with open(MOCKS_DIR / filename, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


@reportes_bp.route("/reportes", methods=["GET"])
@requiere_staff
def listar_reportes():
    tab_actual = request.args.get("tab", "alumnos").lower()
    tabs_validos = ["alumnos", "estadisticas", "equipos"]
    if tab_actual not in tabs_validos:
        tab_actual = "alumnos"

    alumnos, estadisticas, equipos = [], [], []
    error_msg = None
    
    carrera_filtro = request.args.get("carrera", "")
    condicion_filtro = request.args.get("condicion", "")
    anio_ingreso = request.args.get("anio_ingreso", "")
    nombre_completo = request.args.get("nombre_completo", "")
    padron = request.args.get("padron", "")
    evaluacion_id = request.args.get("evaluacion_id", "")
    nota_mayor_a = request.args.get("nota_mayor_a", "")
    
    export = request.args.get("export", "").lower() == "pdf"
    
    try:
        if export:
            export_format = "pdf"
            if tab_actual == "alumnos":
                ok, res = obtener_alumnos_reporte(
                    CURSO_ACTIVO_ID, 
                    carrera=carrera_filtro, 
                    condicion=condicion_filtro,
                    anio_ingreso=anio_ingreso,
                    nombre_completo=nombre_completo,
                    padron=padron,
                    evaluacion_id=evaluacion_id, 
                    nota_mayor_a=nota_mayor_a,
                    export=export_format
                )
            elif tab_actual == "estadisticas":
                ok, res = obtener_estadisticas_reporte(CURSO_ACTIVO_ID, export=export_format)
            elif tab_actual == "equipos":
                ok, res = obtener_equipos_reporte(CURSO_ACTIVO_ID, export=export_format)

            if ok and isinstance(res, bytes):
                response = make_response(res)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=reporte_{tab_actual}.pdf'
                return response
            else:
                error_msg = "La API no devolvió un archivo PDF válido."

        else:
            ok, alumnos_data = obtener_alumnos_reporte(
                CURSO_ACTIVO_ID, 
                carrera=carrera_filtro, 
                condicion=condicion_filtro,
                anio_ingreso=anio_ingreso,
                nombre_completo=nombre_completo,
                padron=padron,
                evaluacion_id=evaluacion_id, 
                nota_mayor_a=nota_mayor_a,
                export=False
            )
            alumnos = alumnos_data if ok else _load_mock("alumnos.json")
            
            ok, estadisticas_data = obtener_estadisticas_reporte(CURSO_ACTIVO_ID, export=False)
            estadisticas = estadisticas_data if ok else _load_mock("reporte_estadisticas.json")

            ok, equipos_data = obtener_equipos_reporte(CURSO_ACTIVO_ID, export=False)
            equipos = equipos_data if ok else _load_mock("equipos.json")
    
    except Exception as e:
        error_msg = f"Error cargando reportes: {str(e)}"
        if not export:
            alumnos = _load_mock("alumnos.json")
            estadisticas = _load_mock("reporte_estadisticas.json")
            equipos = _load_mock("equipos.json")
    
    if error_msg:
        flash(error_msg, "warning")
    
    return render_template(
        "reportes.html",
        title="Reportes de Cátedra",
        active_page="reportes",
        tab_actual=tab_actual,
        alumnos=alumnos,
        estadisticas=estadisticas,
        equipos=equipos,
        carrera_filtro=carrera_filtro,
        condicion_filtro=condicion_filtro,
        curso_id=CURSO_ACTIVO_ID,
    )