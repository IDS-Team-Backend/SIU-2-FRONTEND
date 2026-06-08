import os

from flask import Blueprint, abort, redirect, render_template, url_for

from services.mocks_service import cursos_mock, listar_materiales
from utils.api_client import api_request

# Router público: páginas accesibles sin sesión iniciada, sin sidebar.
# Todas resuelven contra el curso activo (no llevan curso_id en la URL).
# (Recordá sumar sus endpoints a RUTAS_PUBLICAS en services/decorators.py.)
public_bp = Blueprint("public", __name__)

CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))


@public_bp.route("/")
def index():
    return redirect(url_for("public.curso"))


@public_bp.route("/curso")
def curso():
    curso_data = cursos_mock.get(CURSO_ACTIVO_ID)
    if curso_data is None:
        abort(404)
    return render_template(
        "publico/curso.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )


@public_bp.route("/cronograma")
def cronograma():
    ok, data = api_request("GET", f"/cursos/{CURSO_ACTIVO_ID}/cronograma", auth=False)
    semanas = data.get("semanas", []) if ok and data else []
    return render_template(
        "publico/cronograma.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=semanas,
    )


@public_bp.route("/material")
def material():
    return render_template(
        "publico/material.html",
        title="Material",
        active_page="material",
        materiales=listar_materiales,
    )
