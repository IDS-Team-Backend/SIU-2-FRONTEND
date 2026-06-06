import os

from flask import Blueprint, redirect, url_for

# Router público (sin sesión). Por ahora sólo el punto de entrada.
public_bp = Blueprint("public", __name__)

CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))


@public_bp.route("/")
def index():
    return redirect(url_for("private.curso", curso_id=CURSO_ACTIVO_ID))
