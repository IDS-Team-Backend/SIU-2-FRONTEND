import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.decorators import login_required, requiere_staff
from services.materiales_service import (
    obtener_materiales_del_curso,
    crear_material,
    eliminar_material,
)

materiales_bp = Blueprint("materiales", __name__)


@materiales_bp.route("/curso/<int:curso_id>/material") 
@login_required
def listar_materiales(curso_id):
    ok, materiales = obtener_materiales_del_curso(curso_id)
    if not ok:
        flash(materiales, "danger")
        materiales = []

    return render_template(
        "material.html",
        title="Material",
        active_page="material",
        materiales=materiales,
    )


@materiales_bp.route("/curso/<int:curso_id>/material/crear", methods=["POST"])
@requiere_staff
def subir_material(curso_id):
    titulo      = request.form.get("titulo", "").strip()
    archivo_url = request.form.get("archivo_url", "").strip()
    subido_por  = request.form.get("subido_por", type=int)

    ok, resultado = crear_material(curso_id, titulo, archivo_url, subido_por)
    flash("Material subido correctamente." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("materiales.listar_materiales", curso_id=curso_id))


@materiales_bp.route("/curso/<int:curso_id>/material/<int:material_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_material(curso_id, material_id):
    ok, resultado = eliminar_material(material_id)
    flash("Material eliminado." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("materiales.listar_materiales", curso_id=curso_id))