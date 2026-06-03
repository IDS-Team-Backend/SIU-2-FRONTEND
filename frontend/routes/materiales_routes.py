import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.decorators import login_required, requiere_staff
from services.materiales_service import (
    obtener_materiales_del_curso,
    crear_material,
    eliminar_material,
)

materiales_bp = Blueprint("materiales", __name__)
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))


@materiales_bp.route("/material")
@login_required
def listar_materiales():
    ok, materiales = obtener_materiales_del_curso(CURSO_ACTIVO_ID)
    if not ok:
        flash(materiales, "danger")
        materiales = []

    return render_template(
        "material.html",
        title="Material",
        active_page="material",
        materiales=materiales,
    )


@materiales_bp.route("/material/crear", methods=["POST"])
@requiere_staff
def subir_material():
    titulo      = request.form.get("titulo", "").strip()
    archivo_url = request.form.get("archivo_url", "").strip()
    subido_por  = request.form.get("subido_por", type=int)

    ok, resultado = crear_material(CURSO_ACTIVO_ID, titulo, archivo_url, subido_por)
    flash("Material subido correctamente." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("materiales.listar_materiales"))


@materiales_bp.route("/material/<int:material_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_material(material_id):
    ok, resultado = eliminar_material(material_id)
    flash("Material eliminado." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("materiales.listar_materiales"))