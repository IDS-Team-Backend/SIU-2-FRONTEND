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

@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones", methods=["GET"])
@requiere_staff
def listar_tipo_evaluaciones(curso_id):
    ok, tipo_evaluaciones = obtener_tipos_evaluacion(curso_id)

    if not ok:
        flash(tipo_evaluaciones, "danger")
        tipo_evaluaciones = []
    return render_template(
        "tipo_evaluaciones.html",
        title="Tipos de Evaluaciones",
        curso_id=curso_id,
        active_page="tipo_evaluaciones",
        tipo_evaluaciones=tipo_evaluaciones,
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

    return redirect(
        url_for(
            "tipo_evaluaciones.listar_tipo_evaluaciones",
            curso_id=curso_id
        )
    )


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
        flash("Evaluación actualizada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(
        url_for(
            "tipo_evaluaciones.listar_tipo_evaluaciones",
            curso_id=curso_id
        )
    )


@tipo_evaluaciones_bp.route("/curso/<int:curso_id>/tipo_evaluaciones/<int:tipo_evaluacion_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(curso_id, tipo_evaluacion_id):
    ok, resultado = eliminar_tipo_evaluacion(tipo_evaluacion_id)

    if ok:
        flash("Tipo de evaluación eliminada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("tipo_evaluaciones.listar_tipo_evaluaciones", curso_id=curso_id))
