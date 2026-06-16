from flask import request, redirect, url_for, flash

from services.decorators import requiere_staff
from services.equipo_integrantes_service import (
    agregar_integrante,
    eliminar_integrante,
)
from services.alumnos_service import (
    buscar_alumno_por_padron,
)

from routes.evaluaciones import evaluaciones_bp


# ── Integrantes del equipo (modal dentro de la record page) ───────────────────

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/integrantes", methods=["POST"])
@requiere_staff
def agregar_integrante_equipo(curso_id, evaluacion_id, equipo_id):
    padron = request.form.get("padron", "").strip()

    ok, alumno = buscar_alumno_por_padron(padron)
    if not ok:
        flash(alumno, "danger")
        return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id,
                                evaluacion_id=evaluacion_id, accion="editar_equipo", equipo_id=equipo_id))

    ok, resultado = agregar_integrante(equipo_id, alumno["id"])
    if ok:
        flash(f"{alumno['nombre']} {alumno['apellido']} agregado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id,
                            evaluacion_id=evaluacion_id, accion="editar_equipo", equipo_id=equipo_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/integrantes/<int:alumno_id>/eliminar", methods=["POST"])
@requiere_staff
def quitar_integrante_equipo(curso_id, evaluacion_id, equipo_id, alumno_id):
    ok, resultado = eliminar_integrante(equipo_id, alumno_id)
    if ok:
        flash("Integrante eliminado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id,
                            evaluacion_id=evaluacion_id, accion="editar_equipo", equipo_id=equipo_id))
