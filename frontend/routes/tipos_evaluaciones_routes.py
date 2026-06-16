import os
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash

from services.decorators import requiere_staff
from services.tipos_evaluaciones_service import (
    obtener_tipos_evaluacion,
    crear_tipo_evaluacion,
    actualizar_tipo_evaluacion,
    eliminar_tipo_evaluacion,
)

tipo_evaluaciones_bp = Blueprint("tipo_evaluaciones", __name__)


def _redirect_tipos(curso_id):
    """Para llamadas AJAX (input de tipo inline) responde 204; si no, redirige a la
    pantalla de tipos."""
    if request.headers.get("X-Requested-With"):
        return ("", 204)
    return redirect(url_for("tipo_evaluaciones.listar_tipo_evaluaciones", curso_id=curso_id))


@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones/filas", methods=["GET"])
@requiere_staff
def filas_tipos(curso_id):
    """Devuelve sólo las filas del input de tipo (para refrescar tras agregar/cambiar)."""
    ok, tipos = obtener_tipos_evaluacion(curso_id)
    if not ok:
        tipos = []
    return render_template(
        "admin/evaluaciones/components/tipos_input_rows.html",
        curso_id=curso_id,
        tipos_evaluacion=tipos,
        seleccion=request.args.get("seleccion", type=int),
    )

@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones", methods=["GET"])
@requiere_staff
def listar_tipo_evaluaciones(curso_id):
    ok, tipo_evaluaciones = obtener_tipos_evaluacion(curso_id)

    if not ok:
        flash(tipo_evaluaciones, "danger")
        tipo_evaluaciones = []

    tipo_actual = None
    if request.args.get("accion") == "editar" and request.args.get("id"):
        tipo_id = request.args.get("id")
        tipo_actual = next(
            (t for t in tipo_evaluaciones if str(t["id"]) == str(tipo_id)), None
        )

    return render_template(
        "admin/tipo_evaluaciones/index.html",
        title="Tipos de Evaluaciones",
        curso_id=curso_id,
        active_page="tipo_evaluaciones",
        tipo_evaluaciones=tipo_evaluaciones,
        tipo_actual=tipo_actual,
    )


@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones", methods=["POST"])
def crear_nueva_evaluacion(curso_id):
    nombre = request.form.get("nombre", "").strip()
    es_grupal = "es_grupal" in request.form 

    ok, resultado = crear_tipo_evaluacion(
        nombre,
        es_grupal,
        curso_id
    )

    if ok:
        flash("Tipo de evaluación creada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return _redirect_tipos(curso_id)


@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones/<int:tipo_evaluacion_id>/actualizar",methods=["POST"])
def actualizar(curso_id, tipo_evaluacion_id):
    nombre = request.form.get("nombre", "").strip()
    es_grupal = "es_grupal" in request.form

    ok, resultado = actualizar_tipo_evaluacion(
        tipo_evaluacion_id,
        nombre,
        es_grupal,
        curso_id
    )

    if ok:
        flash("Tipo de evaluación actualizado correctamente.", "success")
    else:
        flash(resultado, "danger")

    return _redirect_tipos(curso_id)


@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones/<int:tipo_evaluacion_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(curso_id, tipo_evaluacion_id):
    ok, resultado = eliminar_tipo_evaluacion(tipo_evaluacion_id)

    if ok:
        flash("Tipo de evaluación eliminada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return _redirect_tipos(curso_id)
