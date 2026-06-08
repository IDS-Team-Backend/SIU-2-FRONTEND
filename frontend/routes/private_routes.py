from flask import Blueprint, abort, render_template

from services.mocks_service import cursos_mock, listar_materiales, listar_materias
from utils.api_client import api_request

# Router privado: navegación autenticada del curso (curso, materias, material,
# cronograma). Se registra bajo ADMIN_PREFIX (/admin) junto al resto del
# backoffice; el gate global de proteger_rutas la cubre por no estar en RUTAS_PUBLICAS.
private_bp = Blueprint("private", __name__)


@private_bp.route("/materias")
def materias():
    return render_template(
        "materias.html",
        title="Materias",
        active_page="materias",
        materias=listar_materias,
    )


@private_bp.route("/material")
def material():
    return render_template(
        "material.html",
        title="Material",
        active_page="material",
        materiales=listar_materiales,
    )


@private_bp.route("/curso/<int:curso_id>")
def curso(curso_id):
    curso_data = cursos_mock.get(curso_id)
    if curso_data is None:
        abort(404)
    return render_template(
        "curso.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )


@private_bp.route("/curso/<int:curso_id>/cronograma")
def cronograma(curso_id):
    ok, data = api_request("GET", f"/cursos/{curso_id}/cronograma")
    semanas = data.get("semanas", []) if ok and data else []
    return render_template(
        "cronograma.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=semanas,
    )
