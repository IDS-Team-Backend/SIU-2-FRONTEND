from flask import request, redirect, url_for, flash

from services.decorators import requiere_staff
from services.equipos_service import (
    crear_equipo,
    actualizar_equipo,
    eliminar_equipo,
    importar_equipos_csv,
)

from routes.evaluaciones import evaluaciones_bp


# ── ABM de equipos (evaluación fija desde el path) ────────────────────────────

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos", methods=["POST"])
@requiere_staff
def crear_equipo_evaluacion(curso_id, evaluacion_id):
    nombre = request.form.get("nombre", "").strip()

    ok, resultado = crear_equipo(curso_id, evaluacion_id, nombre)

    if ok:
        flash("Equipo creado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/importar", methods=["POST"])
@requiere_staff
def importar_equipos_evaluacion(curso_id, evaluacion_id):
    archivo = request.files.get("csv_file")
    if not archivo or not archivo.filename:
        flash("Seleccioná un archivo CSV.", "warning")
        return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))
    if not archivo.filename.lower().endswith(".csv"):
        flash("El archivo debe tener extensión .csv", "danger")
        return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))

    ok, resultado = importar_equipos_csv(archivo, curso_id, evaluacion_id)
    if ok:
        flash(
            f"Importación completada: {resultado['exitosos']} equipos creados, "
            f"{resultado['duplicados']} duplicados ignorados, "
            f"{resultado['errores']} errores.",
            "success" if resultado["errores"] == 0 else "warning",
        )
    else:
        flash(f"Error en la importación: {resultado}", "danger")
    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/actualizar", methods=["POST"])
@requiere_staff
def editar_equipo_evaluacion(curso_id, evaluacion_id, equipo_id):
    nombre = request.form.get("nombre", "").strip()

    ok, resultado = actualizar_equipo(curso_id, equipo_id, evaluacion_id, nombre)

    if ok:
        flash("Equipo actualizado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_equipo_evaluacion(curso_id, evaluacion_id, equipo_id):
    ok, resultado = eliminar_equipo(equipo_id)

    if ok:
        flash("Equipo eliminado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))
