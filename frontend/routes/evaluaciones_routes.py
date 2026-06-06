import os
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from pathlib import Path
import json

from services.decorators import requiere_staff
from services.evaluaciones_service import (
    obtener_evaluaciones_del_curso,
    crear_evaluacion,
    actualizar_evaluacion,
    eliminar_evaluacion,
)

from services.tipos_evaluaciones_service import (
    obtener_tipos_evaluacion,
)

evaluaciones_bp = Blueprint("evaluaciones", __name__)

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones", methods=["GET"])
@requiere_staff
def listar_evaluaciones(curso_id):
    ok, evaluaciones = obtener_evaluaciones_del_curso(curso_id)

    if not ok:
        flash(evaluaciones, "danger")
        evaluaciones = []

    ok_tipos, tipos_evaluacion = obtener_tipos_evaluacion(curso_id)

    if not ok_tipos:
        flash(tipos_evaluacion, "danger")
        tipos_evaluacion = []
        
    hoy = date.today().isoformat()

    evaluacion_actual = None
    if request.args.get("accion") == "editar" and request.args.get("id"):
        eval_id = request.args.get("id")
        evaluacion_actual = next(
            (e for e in evaluaciones if str(e["id"]) == str(eval_id)), None
        )

    return render_template(
        "admin/evaluaciones/index.html",
        title="Evaluaciones",
        curso_id=curso_id,
        active_page="evaluaciones",
        evaluaciones=evaluaciones,
        tipos_evaluacion=tipos_evaluacion,
        hoy=hoy,
        evaluacion_actual=evaluacion_actual,
    )


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones", methods=["POST"])
@requiere_staff
def crear_nueva_evaluacion(curso_id):
    titulo = request.form.get("titulo", "").strip()
    tipo_evaluacion_id = request.form.get("tipo_evaluacion_id")
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    ok, resultado = crear_evaluacion(
        titulo,
        tipo_evaluacion_id,
        fecha,
        descripcion,
        curso_id
    )

    if ok:
        flash("Evaluación creada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones", curso_id=curso_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/actualizar", methods=["POST"])
@requiere_staff
def actualizar(curso_id, evaluacion_id):
    titulo = request.form.get("titulo", "").strip()
    tipo_evaluacion_id = request.form.get("tipo_evaluacion_id")
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    activo = request.form.get("activo") == "on"

    ok, resultado = actualizar_evaluacion(
        evaluacion_id,
        titulo,
        tipo_evaluacion_id,
        fecha,
        descripcion,
        curso_id,
        activo
    )

    if ok:
        flash("Evaluación actualizada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones", curso_id=curso_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(curso_id, evaluacion_id):
    ok, resultado = eliminar_evaluacion(evaluacion_id)

    if ok:
        flash("Evaluación eliminada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones", curso_id=curso_id))
