from flask import Blueprint, render_template, request, redirect, flash
from services.decorators import requiere_staff
from services.alumnos_service import (
    obtener_estudiantes,
    crear_alumno,
    editar_alumno,
    eliminar_estudiante,
    eliminar_estudiantes_masivo,
    reactivar_estudiante,
    reactivar_estudiantes_masivo,
    importar_estudiantes_csv,
)
from utils.filtros import leer_filtros, url_con_filtros

estudiantes_bp = Blueprint("estudiantes", __name__)

COLUMNAS_ORDENABLES = {"padron", "nombre", "apellido", "email", "dni", "carrera", "anio_ingreso"}


@estudiantes_bp.route("/estudiantes")
@requiere_staff
def listar_estudiantes():
    f = leer_filtros()
    page       = f["page"]
    q          = f["q"]
    eliminados = f["eliminados"] == "1"
    sort_col   = f["sort"] if f["sort"] in COLUMNAS_ORDENABLES else "apellido"
    sort_dir   = f["dir"] if f["dir"] in ("asc", "desc") else "asc"
    page_size  = request.args.get("page_size", 8, type=int) or 8
    page_size  = max(1, min(page_size, 100))

    ok, estudiantes, paginacion = obtener_estudiantes(
        page=page, page_size=page_size, q=q or None, eliminados=eliminados,
    )
    if not ok:
        flash(estudiantes, "danger")
        estudiantes, paginacion = [], {}

    form_activo       = request.args.get("form", "")   # "alta" | "editar" | ""
    estudiante_editar = None

    if form_activo == "editar":
        eid = request.args.get("estudiante_id", type=int)
        estudiante_editar = next((e for e in estudiantes if e["id"] == eid), None)
        if not estudiante_editar:
            flash("No se encontró el estudiante para editar.", "warning")
            form_activo = ""

    estudiantes = sorted(
        estudiantes,
        key=lambda e: str(e.get(sort_col) or "").lower(),
        reverse=(sort_dir == "desc"),
    )

    return render_template(
        "admin/estudiantes/index.html",
        title="Estudiantes",
        active_page="estudiantes",
        estudiantes=estudiantes,
        paginacion=paginacion,
        page_size=page_size,
        url_con_filtros=url_con_filtros,
        form_activo=form_activo,
        estudiante_editar=estudiante_editar,
        q=q,
        eliminados=eliminados,
        sort_col=sort_col,
        sort_dir=sort_dir,
    )


# ── Alta ─────────────────────────────────────────────────────────────────────

@estudiantes_bp.route("/estudiantes/crear", methods=["POST"])
@requiere_staff
def crear():
    nombre       = request.form.get("nombre",       "").strip()
    apellido     = request.form.get("apellido",     "").strip()
    email        = request.form.get("email",        "").strip()
    dni          = request.form.get("dni",          "").strip()
    padron       = request.form.get("padron",       "").strip()
    carrera      = request.form.get("carrera",      "").strip()
    anio_ingreso = request.form.get("anio_ingreso", "").strip()

    ok, error = crear_alumno(nombre, apellido, email, dni, padron, carrera, anio_ingreso)

    if ok:
        flash(f"Estudiante {nombre} {apellido} creado correctamente.", "success")
    else:
        flash(f"Error al crear estudiante: {error}", "danger")

    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))


# ── Editar ───────────────────────────────────────────────────────────────────

@estudiantes_bp.route("/estudiantes/<int:estudiante_id>/editar", methods=["POST"])
@requiere_staff
def editar(estudiante_id):
    usuario_id   = request.form.get("usuario_id",   type=int)
    nombre       = request.form.get("nombre",       "").strip()
    apellido     = request.form.get("apellido",     "").strip()
    email        = request.form.get("email",        "").strip()
    dni          = request.form.get("dni",          "").strip()
    padron       = request.form.get("padron",       "").strip()
    carrera      = request.form.get("carrera",      "").strip()
    anio_ingreso = request.form.get("anio_ingreso", "").strip()

    ok, error = editar_alumno(
        estudiante_id, usuario_id,
        nombre, apellido, email, dni,
        padron, carrera, anio_ingreso,
    )

    if ok:
        flash(f"Datos de {nombre} {apellido} actualizados.", "success")
    else:
        flash(f"Error al editar estudiante: {error}", "danger")

    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))


# ── Baja ─────────────────────────────────────────────────────────────────────

@estudiantes_bp.route("/estudiantes/<int:estudiante_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(estudiante_id):
    ok, error = eliminar_estudiante(estudiante_id)
    flash("Estudiante eliminado correctamente." if ok else error,
          "success" if ok else "danger")
    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))


@estudiantes_bp.route("/estudiantes/<int:estudiante_id>/reactivar", methods=["POST"])
@requiere_staff
def reactivar(estudiante_id):
    ok, error = reactivar_estudiante(estudiante_id)
    flash("Estudiante reactivado correctamente." if ok else error,
          "success" if ok else "danger")
    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))


@estudiantes_bp.route("/estudiantes/eliminar-masivo", methods=["POST"])
@requiere_staff
def eliminar_masivo():
    ids_raw = request.form.getlist("seleccionados")
    estudiante_ids = [int(v) for v in ids_raw if v.isdigit()]

    if not estudiante_ids:
        flash("No seleccionaste ningún estudiante.", "warning")
        return redirect(url_con_filtros("estudiantes.listar_estudiantes"))

    ok, resumen = eliminar_estudiantes_masivo(estudiante_ids)
    if ok:
        flash(f"{resumen['eliminados']} eliminados, {resumen['errores']} con error.",
              "success" if resumen["errores"] == 0 else "warning")
    else:
        flash(f"Error: {resumen}", "danger")
    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))


@estudiantes_bp.route("/estudiantes/reactivar-masivo", methods=["POST"])
@requiere_staff
def reactivar_masivo():
    ids_raw = request.form.getlist("seleccionados")
    estudiante_ids = [int(v) for v in ids_raw if v.isdigit()]

    if not estudiante_ids:
        flash("No seleccionaste ningún estudiante.", "warning")
        return redirect(url_con_filtros("estudiantes.listar_estudiantes"))

    ok, resumen = reactivar_estudiantes_masivo(estudiante_ids)
    if ok:
        flash(f"{resumen['reactivados']} reactivados, {resumen['errores']} con error.",
              "success" if resumen["errores"] == 0 else "warning")
    else:
        flash(f"Error: {resumen}", "danger")
    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))


# ── Importación masiva (alta de estudiantes nuevos) ─────────────────────────

@estudiantes_bp.route("/estudiantes/importar", methods=["POST"])
@requiere_staff
def importar():
    archivo = request.files.get("csv_file")
    if not archivo or not archivo.filename:
        flash("Seleccioná un archivo CSV.", "warning")
        return redirect(url_con_filtros("estudiantes.listar_estudiantes"))
    if not archivo.filename.lower().endswith(".csv"):
        flash("El archivo debe tener extensión .csv", "danger")
        return redirect(url_con_filtros("estudiantes.listar_estudiantes"))

    ok, resultado = importar_estudiantes_csv(archivo)
    if ok:
        flash(
            f"Importación completada: {resultado['exitosos']} creados, "
            f"{resultado['duplicados']} duplicados ignorados, "
            f"{resultado['errores']} errores.",
            "success" if resultado["errores"] == 0 else "warning",
        )
    else:
        flash(f"Error en la importación: {resultado}", "danger")
    return redirect(url_con_filtros("estudiantes.listar_estudiantes"))
