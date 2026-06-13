from flask import Blueprint, abort, redirect, render_template, url_for

from services.mocks_service import listar_materiales
from services.cursos_service import obtener_curso_activo, obtener_curso_activo_id
from utils.api_client import api_request
from services.materiales_service import obtener_materiales_del_curso

# Router público: páginas accesibles sin sesión iniciada, sin sidebar.
# Todas resuelven contra la cursada activa del sistema (no llevan curso_id en la URL).
# (Recordá sumar sus endpoints a RUTAS_PUBLICAS en services/decorators.py.)
public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return redirect(url_for("public.curso"))


@public_bp.route("/curso")
def curso():
    ok, curso_data = obtener_curso_activo()
    if not ok:
        abort(404)
    return render_template(
        "public/curso/index.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )


@public_bp.route("/cronograma")
def cronograma():
    ok, data = api_request("GET", f"/cursos/{obtener_curso_activo_id()}/cronograma", auth=False)
    semanas = data.get("semanas", []) if ok and data else []
    return render_template(
        "public/cronograma/index.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=semanas,
    )


@public_bp.route("/material")
def material():
    ok, materiales = obtener_materiales_del_curso(CURSO_ACTIVO_ID)
    if not ok:
        materiales = []
    return render_template(
        "public/material/index.html",
        title="Material",
        active_page="material",
        materiales=materiales,
    )