import os
from flask import Blueprint, render_template, request, flash, make_response, redirect, url_for

from services.decorators import requiere_staff
from services.reportes_service import (
    obtener_alumnos_reporte,
    obtener_estadisticas_reporte,
    obtener_equipos_reporte,
)
from services.evaluaciones_service import (
    obtener_evaluaciones_del_curso,
)
import traceback


reportes_bp = Blueprint("reportes", __name__)
@reportes_bp.route("/curso/<int:curso_id>/reportes", methods=["GET"])
@requiere_staff
def listar_reportes(curso_id):
    tab_actual = request.args.get("tab", "alumnos").lower()
    tabs_validos = ["alumnos", "estadisticas", "equipos"]

    if tab_actual not in tabs_validos:
        tab_actual = "alumnos"

    carrera_filtro = request.args.get("carrera", "")
    condicion_filtro = request.args.get("condicion", "")
    anio_ingreso = request.args.get("anio_ingreso", "")
    nombre_completo = request.args.get("nombre_completo", "")
    padron = request.args.get("padron", "")
    evaluacion_id = request.args.get("evaluacion_id", "")
    nota_mayor_a = request.args.get("nota_mayor_a", "")

    page = request.args.get("page", 1, type=int)

    export = request.args.get("export", "").lower() == "pdf"
    ok_evals, evaluaciones = obtener_evaluaciones_del_curso(
        curso_id,
    )

    if not ok_evals:
        flash(evaluaciones, "danger")
        evaluaciones = []

    if export:
        try:
            if tab_actual == "alumnos":
                ok, res = obtener_alumnos_reporte(
                    curso_id,
                    carrera=carrera_filtro,
                    condicion=condicion_filtro,
                    anio_ingreso=anio_ingreso,
                    nombre_completo=nombre_completo,
                    padron=padron,
                    evaluacion_id=evaluacion_id,
                    nota_mayor_a=nota_mayor_a,
                    export="pdf"
                )
            elif tab_actual == "estadisticas":
                ok, res = obtener_estadisticas_reporte(curso_id, export="pdf")
            elif tab_actual == "equipos":
                ok, res = obtener_equipos_reporte(curso_id, export="pdf")

            
            if ok and isinstance(res, (bytes, bytearray)):
                response = make_response(res)
                response.headers["Content-Type"] = "application/pdf"
                response.headers["Content-Disposition"] = f"attachment; filename=reporte_{tab_actual}.pdf"
                return response

            error_msg = res.get("error") if isinstance(res, dict) else "Error al generar el PDF."
            flash(error_msg, "danger")

        except Exception as e:
            flash(f"Error crítico al exportar PDF: {str(e)}", "danger")

        return redirect(url_for("reportes.listar_reportes", curso_id=curso_id, tab=tab_actual))

    alumnos, estadisticas, equipos = [], [], []
    paginacion = {}
    error_msg = None

    try:
        ok_alumnos, alumnos_data, paginacion = obtener_alumnos_reporte(
            curso_id,
            carrera=carrera_filtro,
            condicion=condicion_filtro,
            anio_ingreso=anio_ingreso,
            nombre_completo=nombre_completo,
            padron=padron,
            evaluacion_id=evaluacion_id,
            nota_mayor_a=nota_mayor_a,
            page=page,
            export=False
        )

        alumnos = alumnos_data if ok_alumnos else []

        if not ok_alumnos:
            error_msg = "No se pudieron cargar los alumnos."

        ok_evals, evaluaciones = obtener_evaluaciones_del_curso(
            curso_id,
        )

        if not ok_evals:
            flash(evaluaciones, "danger")
            evaluaciones = []

        ok_stats, estadisticas_data = obtener_estadisticas_reporte(curso_id, export=False)
        
        if ok_stats:
            estadisticas = estadisticas_data
        else:
            estadisticas = []
            error_msg = error_msg or f"Estadísticas: {estadisticas_data}"

        ok_equipos, equipos_data = obtener_equipos_reporte(curso_id, export=False)
        
        if ok_equipos:
            equipos = equipos_data
        else:
            equipos = []
            error_msg = error_msg or f"Equipos: {equipos_data}"

    except Exception as e:
        print(traceback.format_exc())
        error_msg = f"Error crítico de conexión con el backend: {str(e)}"

    if error_msg:
        flash(error_msg, "danger")

    return render_template(
        "reportes.html",
        title="Reportes de Cátedra",
        active_page="reportes",
        tab_actual=tab_actual,
        alumnos=alumnos,
        estadisticas=estadisticas,
        equipos=equipos,
        paginacion=paginacion,
        carrera_filtro=carrera_filtro,
        condicion_filtro=condicion_filtro,
        anio_ingreso_filtro=anio_ingreso,
        nombre_filtro=nombre_completo,
        padron_filtro=padron,
        evaluaciones=evaluaciones,
        evaluacion_filtro=evaluacion_id,
        nota_filtro=nota_mayor_a,
        curso_id=curso_id
    )