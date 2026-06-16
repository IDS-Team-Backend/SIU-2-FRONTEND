from flask import request, flash

from services.decorators import requiere_staff
from services.notas_service import (
    crear_nota,
    actualizar_nota,
    eliminar_nota,
)
from services.entregas_service import (
    obtener_entregas_por_equipo,
    obtener_entregas_por_alumno,
)

from routes.evaluaciones import evaluaciones_bp, _volver_a_evaluacion


# ── Notas (corrección: cargar / editar / quitar; cargar exige entrega) ────────

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/nota", methods=["POST"])
@requiere_staff
def cargar_nota_equipo(curso_id, evaluacion_id, equipo_id):
    ok_ent, entregas = obtener_entregas_por_equipo(evaluacion_id)
    if not ok_ent or equipo_id not in entregas:
        flash("Registrá la entrega del equipo antes de cargar la nota.", "danger")
        return _volver_a_evaluacion(curso_id, evaluacion_id)

    ok, resultado = crear_nota(
        evaluacion_id,
        request.form.get("nota", "").strip(),
        request.form.get("observaciones", "").strip(),
        equipo_id=equipo_id,
    )
    flash("Nota cargada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/alumnos/<int:alumno_id>/nota", methods=["POST"])
@requiere_staff
def cargar_nota_alumno(curso_id, evaluacion_id, alumno_id):
    ok_ent, entregas = obtener_entregas_por_alumno(evaluacion_id)
    if not ok_ent or alumno_id not in entregas:
        flash("Registrá la entrega del alumno antes de cargar la nota.", "danger")
        return _volver_a_evaluacion(curso_id, evaluacion_id)

    ok, resultado = crear_nota(
        evaluacion_id,
        request.form.get("nota", "").strip(),
        request.form.get("observaciones", "").strip(),
        alumno_id=alumno_id,
    )
    flash("Nota cargada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/notas/<int:nota_id>/actualizar", methods=["POST"])
@requiere_staff
def editar_nota(curso_id, evaluacion_id, nota_id):
    ok, resultado = actualizar_nota(
        nota_id,
        request.form.get("nota", "").strip(),
        request.form.get("observaciones", ""),
    )
    flash("Nota actualizada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/notas/<int:nota_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_nota(curso_id, evaluacion_id, nota_id):
    ok, resultado = eliminar_nota(nota_id)
    flash("Nota eliminada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)
