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
from services.equipo_integrantes_service import (
    obtener_integrantes, agregar_integrante, eliminar_integrante
)
from services.alumnos_service import (
    buscar_alumno_por_padron,
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

@equipos_bp.route("/equipos/<int:equipo_id>/integrantes", methods=["GET"])
@requiere_staff
def administrar_integrantes(equipo_id):
    ok, integrantes = obtener_integrantes(equipo_id)

    if not ok:
        flash(integrantes, "danger")
        integrantes = []

    return render_template(
        "equipo_integrantes.html",
        title="Integrantes del Equipo",
        active_page="equipos",
        equipo_id=equipo_id,
        integrantes=integrantes,
    )


@equipos_bp.route(
    "/equipos/<int:equipo_id>/buscar-integrante",
    methods=["POST"]
)
@requiere_staff
def buscar_integrante(equipo_id):
    padron = request.form.get("padron", "").strip()
    ok, alumno = buscar_alumno_por_padron(padron)
    if not ok:
        flash(alumno, "danger")

        return redirect(
            url_for(
                "equipos.administrar_integrantes",
                equipo_id=equipo_id
            )
        )

    ok, resultado = agregar_integrante(
        equipo_id,
        alumno["id"]
    )

    if ok:
        flash(
            f"{alumno['nombre']} {alumno['apellido']} agregado correctamente.",
            "success"
        )
    else:
        flash(resultado, "danger")

    return redirect(
        url_for(
            "equipos.administrar_integrantes",
            equipo_id=equipo_id
        )
    )


@equipos_bp.route(
    "/equipos/<int:equipo_id>/integrantes/<int:alumno_id>/eliminar",
    methods=["POST"]
)
@requiere_staff
def eliminar_integrante_equipo(equipo_id, alumno_id):
    ok, resultado = eliminar_integrante(
        equipo_id,
        alumno_id
    )
    if ok:
        flash(
            "Integrante eliminado correctamente.",
            "success"
        )
    else:
        flash(resultado, "danger")

    return redirect(
        url_for(
            "equipos.administrar_integrantes",
            equipo_id=equipo_id
        )
    )