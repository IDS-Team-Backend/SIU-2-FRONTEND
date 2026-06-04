import os
from flask import Blueprint, render_template, request, flash, make_response

from services.decorators import requiere_staff
from services.reportes_service import (
    obtener_alumnos_reporte,
    obtener_estadisticas_reporte,
    obtener_equipos_reporte,
)

reportes_bp = Blueprint("reportes", __name__)
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

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
                    CURSO_ACTIVO_ID, carrera=carrera_filtro, condicion=condicion_filtro,
                    anio_ingreso=anio_ingreso, nombre_completo=nombre_completo,
                    padron=padron, evaluacion_id=evaluacion_id, nota_mayor_a=nota_mayor_a,
                    export=export_format
                )
            elif tab_actual == "estadisticas":
                ok, res = obtener_estadisticas_reporte(CURSO_ACTIVO_ID, export=export_format)
            elif tab_actual == "equipos":
                ok, res = obtener_equipos_reporte(CURSO_ACTIVO_ID, export=export_format)

            if ok and (isinstance(res, bytes) or isinstance(res, bytearray)):
                # Nos aseguramos de pasarlo a bytes puros por si las moscas
                response = make_response(bytes(res)) 
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=reporte_{tab_actual}.pdf'
                return response
            else:
                error_msg = f"La API no pudo generar el archivo PDF para {tab_actual}."

        else:
            ok_alumnos, alumnos_data = obtener_alumnos_reporte(
                CURSO_ACTIVO_ID, carrera=carrera_filtro, condicion=condicion_filtro,
                anio_ingreso=anio_ingreso, nombre_completo=nombre_completo,
                padron=padron, evaluacion_id=evaluacion_id, nota_mayor_a=nota_mayor_a,
                export=False
            )
            if ok_alumnos:
                alumnos = alumnos_data
            else:
                error_msg = "No se pudieron cargar los alumnos del backend."
            ok_stats, estadisticas_data = obtener_estadisticas_reporte(CURSO_ACTIVO_ID, export=False)
            if ok_stats:
                estadisticas = estadisticas_data
            else:
                error_msg = error_msg or "No se pudieron cargar las estadísticas del backend."

            ok_equipos, equipos_data = obtener_equipos_reporte(CURSO_ACTIVO_ID, export=False)
            if ok_equipos:
                equipos = equipos_data
            else:
                error_msg = error_msg or "No se pudieron cargar los equipos del backend."
    
    except Exception as e:
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

        carrera_filtro=carrera_filtro,
        condicion_filtro=condicion_filtro,
        anio_ingreso_filtro=anio_ingreso,
        nombre_filtro=nombre_completo,
        padron_filtro=padron,
        evaluacion_filtro=evaluacion_id,
        nota_filtro=nota_mayor_a,

        curso_id=CURSO_ACTIVO_ID,
    )