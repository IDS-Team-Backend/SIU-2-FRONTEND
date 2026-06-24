from flask import Blueprint, render_template, request, redirect, flash, url_for

from services.decorators import requiere_staff
from services.profesores_service import (
    obtener_profesores,
    obtener_participaciones,
    registrar_profesor,
    obtener_profesor,
    editar_profesor,
    eliminar_profesor,
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
    page_size = request.args.get("page_size", 20, type=int) or 20
    ok, profesores, paginacion = obtener_profesores(page=page, page_size=page_size)
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


@profesores_bp.route("/profesores/<int:profesor_id>")
@requiere_staff
def ver_profesor(profesor_id):
    ok, profesor = obtener_profesor(profesor_id)
    if not ok:
        flash(profesor, "danger")
        return redirect(url_for("profesores.listar_profesores"))

    participaciones = obtener_participaciones([profesor_id]).get(profesor_id, [])

    return render_template(
        "admin/profesores/detalle.html",
        title="Ficha de profesor",
        active_page="profesores",
        profesor=profesor,
        participaciones=participaciones,
        mostrar_modal_editar=request.args.get("editar") == "1",
    )


@profesores_bp.route("/profesores/<int:profesor_id>/editar", methods=["POST"])
@requiere_staff
def editar(profesor_id):
    datos = _leer_form(request.form)
    usuario_id = request.form.get("usuario_id", type=int)
    ok, error = editar_profesor(profesor_id, usuario_id, datos)

    if ok:
        flash("Datos del profesor actualizados.", "success")
        return redirect(url_for("profesores.ver_profesor", profesor_id=profesor_id))

    flash(f"Error al editar profesor: {error}", "danger")
    return redirect(url_for("profesores.ver_profesor", profesor_id=profesor_id, editar="1"))


@profesores_bp.route("/profesores/<int:profesor_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(profesor_id):
    ok, error = eliminar_profesor(profesor_id)
    flash("Profesor eliminado." if ok else f"Error al eliminar: {error}",
          "success" if ok else "danger")
    return redirect(url_for("profesores.listar_profesores"))


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
