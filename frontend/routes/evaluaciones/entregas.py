from flask import request, flash

from services.decorators import requiere_staff
from services.notas_service import (
    obtener_notas_por_equipo,
    obtener_notas_por_alumno,
)
from services.entregas_service import (
    crear_entrega,
    eliminar_entrega,
)

from routes.evaluaciones import evaluaciones_bp, _volver_a_evaluacion


# ── Entregas (solo registrar / quitar; NO se editan) ──────────────────────────

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/entrega", methods=["POST"])
@requiere_staff
def registrar_entrega_equipo(curso_id, evaluacion_id, equipo_id):
    ok, resultado = crear_entrega(
        evaluacion_id,
        request.form.get("fecha_entrega", "").strip(),
        request.form.get("estado", "entregado"),
        request.form.get("archivo_url", "").strip(),
        request.form.get("observaciones", "").strip(),
        equipo_id=equipo_id,
    )
    flash("Entrega registrada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/alumnos/<int:alumno_id>/entrega", methods=["POST"])
@requiere_staff
def registrar_entrega_alumno(curso_id, evaluacion_id, alumno_id):
    ok, resultado = crear_entrega(
        evaluacion_id,
        request.form.get("fecha_entrega", "").strip(),
        request.form.get("estado", "entregado"),
        request.form.get("archivo_url", "").strip(),
        request.form.get("observaciones", "").strip(),
        alumno_id=alumno_id,
    )
    flash("Entrega registrada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/entregas/<int:entrega_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_entrega(curso_id, evaluacion_id, entrega_id):
    # Guarda: no se puede quitar la entrega si el sujeto ya tiene nota (dejaría la nota huérfana).
    equipo_id = request.form.get("equipo_id", type=int)
    alumno_id = request.form.get("alumno_id", type=int)
    if equipo_id:
        ok_n, notas = obtener_notas_por_equipo(evaluacion_id)
        tiene_nota = ok_n and equipo_id in notas
    elif alumno_id:
        ok_n, notas = obtener_notas_por_alumno(evaluacion_id)
        tiene_nota = ok_n and alumno_id in notas
    else:
        tiene_nota = False

    if tiene_nota:
        flash("Quitá la nota antes de quitar la entrega.", "danger")
        return _volver_a_evaluacion(curso_id, evaluacion_id)

    ok, resultado = eliminar_entrega(entrega_id)
    flash("Entrega eliminada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)
