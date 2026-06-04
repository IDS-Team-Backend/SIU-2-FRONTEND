import os

from flask import Blueprint, render_template, request, redirect, url_for, flash

from services.decorators import requiere_staff
from services.equipos_service import (
    obtener_equipos,
    crear_equipo,
    actualizar_equipo,
    eliminar_equipo,
)
from services.evaluaciones_service import (
    obtener_evaluaciones_del_curso,
)

equipos_bp = Blueprint("equipos", __name__)

CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))


@equipos_bp.route("/equipos", methods=["GET"])
@requiere_staff
def listar_equipos():
    ok_equipos, equipos = obtener_equipos()

    if not ok_equipos:
        flash(equipos, "danger")
        equipos = []

    ok_evals, evaluaciones = obtener_evaluaciones_del_curso(
        CURSO_ACTIVO_ID
    )

    if not ok_evals:
        flash(evaluaciones, "danger")
        evaluaciones = []

    return render_template(
        "equipos.html",
        title="Equipos",
        active_page="equipos",
        equipos=equipos,
        evaluaciones=evaluaciones,
    )


@equipos_bp.route("/equipos", methods=["POST"])
@requiere_staff
def crear_nuevo_equipo():
    nombre = request.form.get("nombre", "").strip()
    evaluacion_id = request.form.get("evaluacion_id")

    ok, resultado = crear_equipo(
        CURSO_ACTIVO_ID,
        evaluacion_id,
        nombre
    )

    if ok:
        flash("Equipo creado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(
        url_for("equipos.listar_equipos")
    )


@equipos_bp.route("/equipos/<int:equipo_id>/actualizar", methods=["POST"])
@requiere_staff
def actualizar(equipo_id):
    nombre = request.form.get("nombre", "").strip()
    activo = request.form.get("activo") == "on"
    evaluacion_id = request.form.get('evaluacion_id')

    ok, resultado = actualizar_equipo(
        CURSO_ACTIVO_ID,
        equipo_id,
        evaluacion_id,
        nombre,
        activo,
    )

    if ok:
        flash("Equipo actualizado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(
        url_for("equipos.listar_equipos")
    )


@equipos_bp.route("/equipos/<int:equipo_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(equipo_id):
    ok, resultado = eliminar_equipo(equipo_id)

    if ok:
        flash("Equipo eliminado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(
        url_for("equipos.listar_equipos")
    )