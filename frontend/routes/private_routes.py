from flask import Blueprint, abort, render_template, url_for
from services.decorators import requiere_staff
from services.mocks_service import listar_materias
from services.cursos_service import obtener_curso_para_vista
from services.materiales_service import obtener_materiales_del_curso
from flask import request, flash, redirect
from services.materiales_service import crear_material
from services.materiales_service import eliminar_material
from utils.config import CURSO_ACTIVO_ID

# Router privado: navegación autenticada del curso (curso, materias, material).
# Se registra bajo ADMIN_PREFIX (/admin) junto al resto del backoffice; el gate
# global de proteger_rutas la cubre por no estar en RUTAS_PUBLICAS.
private_bp = Blueprint("private", __name__)


@private_bp.route("/materias")
def materias():
    return render_template(
        "admin/materias/index.html",
        title="Materias",
        active_page="materias",
        materias=listar_materias,
    )


@private_bp.route("/curso/<int:curso_id>/material")
def material(curso_id):
    ok, materiales = obtener_materiales_del_curso(curso_id)
    if not ok:
        materiales = []
    return render_template(
        "admin/material/index.html",
        title="Material",
        active_page="material",
        curso_id=curso_id,
        materiales=materiales,
    )

@private_bp.route("/curso/<int:curso_id>/material/crear", methods=["POST"])
@requiere_staff
def subir_material(curso_id):
    titulo      = request.form.get("titulo", "").strip()
    archivo_url = request.form.get("archivo_url", "").strip()
    ok, resultado = crear_material(curso_id, titulo, archivo_url)
    flash("Material subido correctamente." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("private.material", curso_id=curso_id))


@private_bp.route("/curso/<int:curso_id>/material/<int:material_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_material(curso_id, material_id):
    ok, resultado = eliminar_material(material_id)
    flash("Material eliminado." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("private.material", curso_id=curso_id))




@private_bp.route("/curso/<int:curso_id>")
def curso(curso_id):
    ok, curso_data = obtener_curso_para_vista(curso_id)
    if not ok:
        abort(404)
    return render_template(
        "admin/curso/index.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )
