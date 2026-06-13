from flask import Blueprint, render_template, request, redirect, flash, url_for

from services.decorators import requiere_staff
from services.profesores_service import (
    obtener_profesores,
    obtener_participaciones,
    registrar_profesor,
)

profesores_bp = Blueprint("profesores", __name__)


def _adjuntar_participaciones(profesores):
    """Enriquece cada profesor con sus cursadas (una sola llamada al backend)."""
    if not profesores:
        return
    participaciones = obtener_participaciones([p["id"] for p in profesores])
    for p in profesores:
        p["participaciones"] = participaciones.get(p["id"], [])


def _leer_form(form):
    return {
        "nombre":        (form.get("nombre") or "").strip(),
        "apellido":      (form.get("apellido") or "").strip(),
        "email":         (form.get("email") or "").strip(),
        "dni":           form.get("dni", type=int),
        "legajo":        form.get("legajo", type=int),
        "titulo":        (form.get("titulo") or "").strip(),
        "departamento":  (form.get("departamento") or "").strip(),
        "fecha_ingreso": (form.get("fecha_ingreso") or "").strip(),
    }


@profesores_bp.route("/profesores")
@requiere_staff
def listar_profesores():
    page = request.args.get("page", 1, type=int) or 1
    ok, profesores, paginacion = obtener_profesores(page=page, page_size=20)
    if not ok:
        flash(profesores, "danger")
        profesores, paginacion = [], {}
    else:
        _adjuntar_participaciones(profesores)

    return render_template(
        "admin/profesores/index.html",
        title="Profesores",
        active_page="profesores",
        profesores=profesores,
        paginacion=paginacion,
        mostrar_modal=request.args.get("accion") == "nueva",
        form_data={},
    )


@profesores_bp.route("/profesores/crear", methods=["POST"])
@requiere_staff
def crear_profesor():
    datos = _leer_form(request.form)
    ok, resultado = registrar_profesor(datos)

    if ok:
        flash("Profesor creado. Se le envió un email para finalizar su registración.", "success")
        return redirect(url_for("profesores.listar_profesores"))

    # Error: reabrir el modal conservando lo cargado.
    flash(resultado, "danger")
    ok_list, profesores, paginacion = obtener_profesores(page=1, page_size=20)
    if not ok_list:
        profesores, paginacion = [], {}
    else:
        _adjuntar_participaciones(profesores)

    return render_template(
        "admin/profesores/index.html",
        title="Profesores",
        active_page="profesores",
        profesores=profesores,
        paginacion=paginacion,
        mostrar_modal=True,
        form_data=datos,
    )
