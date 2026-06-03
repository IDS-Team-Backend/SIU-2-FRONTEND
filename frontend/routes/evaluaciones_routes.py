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

evaluaciones_bp = Blueprint("evaluaciones", __name__)
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

MOCKS_DIR = Path(__file__).parent.parent / "mocks"

def _load_tipos_evaluacion():
    try:
        with open(MOCKS_DIR / "tipos_evaluacion.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


@evaluaciones_bp.route("/evaluaciones", methods=["GET"])
@requiere_staff
def listar_evaluaciones():
    ok, evaluaciones = obtener_evaluaciones_del_curso(CURSO_ACTIVO_ID)

    if not ok:
        flash(evaluaciones, "danger")
        evaluaciones = []

    tipos_evaluacion = _load_tipos_evaluacion()
    hoy = date.today().isoformat()

    return render_template(
        "evaluaciones.html",
        title="Evaluaciones",
        active_page="evaluaciones",
        evaluaciones=evaluaciones,
        tipos_evaluacion=tipos_evaluacion,
        hoy=hoy,
    )


@evaluaciones_bp.route("/evaluaciones", methods=["POST"])
@requiere_staff
def crear_nueva_evaluacion():
    titulo = request.form.get("titulo", "").strip()
    tipo_evaluacion_id = request.form.get("tipo_evaluacion_id")
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    ok, resultado = crear_evaluacion(
        titulo,
        tipo_evaluacion_id,
        fecha,
        descripcion,
        CURSO_ACTIVO_ID
    )

    if ok:
        flash("Evaluación creada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones"))


@evaluaciones_bp.route("/evaluaciones/<int:evaluacion_id>/actualizar", methods=["POST"])
@requiere_staff
def actualizar(evaluacion_id):
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
        CURSO_ACTIVO_ID,
        activo
    )

    if ok:
        flash("Evaluación actualizada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones"))


@evaluaciones_bp.route("/evaluaciones/<int:evaluacion_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(evaluacion_id):
    ok, resultado = eliminar_evaluacion(evaluacion_id)

    if ok:
        flash("Evaluación eliminada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones"))
