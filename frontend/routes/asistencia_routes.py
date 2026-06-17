from flask import Blueprint, flash, render_template

from services.asistencia_service import obtener_mi_qr, obtener_mis_asistencias
from services.decorators import requiere_alumno


asistencia_bp = Blueprint("asistencia", __name__)

@asistencia_bp.route("/curso/<int:curso_id>/mi-asistencia", methods=["GET"])
@requiere_alumno
def mi_asistencia(curso_id):
    ok_asistencia, asistencia = obtener_mis_asistencias(curso_id)
    if not ok_asistencia:
        flash(asistencia, "danger")
        asistencia = {}

    ok_qr, token_qr = obtener_mi_qr()
    if not ok_qr:
        token_qr = None

    return render_template(
        "admin/asistencia/index.html",
        title="Mi asistencia",
        curso_id=curso_id,
        asistencia=asistencia,
        token_qr=token_qr,
        active_page="asistencia",
    )