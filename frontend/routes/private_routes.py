from flask import Blueprint, abort, render_template, url_for
from services.decorators import requiere_staff
from services.mocks_service import cursos_mock, listar_materias
from utils.api_client import api_request
from services.materiales_service import obtener_materiales_del_curso
import os
from flask import request, flash, redirect
from services.materiales_service import crear_material
from services.materiales_service import eliminar_material


CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

# Router privado: navegación autenticada del curso (curso, materias, material,
# cronograma). Se registra bajo ADMIN_PREFIX (/admin) junto al resto del
# backoffice; el gate global de proteger_rutas la cubre por no estar en RUTAS_PUBLICAS.
private_bp = Blueprint("private", __name__)


@private_bp.route("/materias")
def materias():
    return render_template(
        "admin/materias/index.html",
        title="Materias",
        active_page="materias",
        materias=listar_materias,
    )


@private_bp.route("/material")
def material():
    ok, materiales = obtener_materiales_del_curso(CURSO_ACTIVO_ID)
    if not ok:
        materiales = []
    return render_template(
        "admin/material/index.html",
        title="Material",
        active_page="material",
        materiales=materiales,
    )

@private_bp.route("/material/crear", methods=["POST"])
@requiere_staff
def subir_material():
    titulo      = request.form.get("titulo", "").strip()
    archivo_url = request.form.get("archivo_url", "").strip()
    ok, resultado = crear_material(CURSO_ACTIVO_ID, titulo, archivo_url)
    flash("Material subido correctamente." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("private.material"))


@private_bp.route("/material/<int:material_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_material(material_id):
    ok, resultado = eliminar_material(material_id)
    flash("Material eliminado." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("private.material"))


@private_bp.route("/curso/<int:curso_id>")
def curso(curso_id):
    curso_data = cursos_mock.get(curso_id)
    if curso_data is None:
        abort(404)
    return render_template(
        "admin/curso/index.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )


@private_bp.route("/curso/<int:curso_id>/cronograma")
def cronograma(curso_id):
    ok, data = api_request("GET", f"/cursos/{curso_id}/cronograma")
    semanas = data.get("semanas", []) if ok and data else []
    return render_template(
        "admin/cronograma/index.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=semanas,
    )
