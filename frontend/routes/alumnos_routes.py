from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.decorators import login_required, requiere_staff
from services.alumnos_service import (
    obtener_alumnos_del_curso,
    buscar_alumno_por_padron,
    vincular_alumno_a_curso,
    desvincular_alumno_del_curso,
    cambiar_estado_inscripcion,
    importar_csv,
)

alumnos_bp = Blueprint("alumnos", __name__)

COLUMNAS_ORDENABLES = {"padron", "nombre", "apellido", "email", "estado"}


def redirect_preservando_params(curso_id):
    """Vuelve a la lista preservando los filtros actuales (viajan en el query string del form)."""
    filtros = {
        "page":          request.args.get("page", type=int),
        "estado_filtro": request.args.get("estado_filtro") or None,
        "sort":          request.args.get("sort") or None,
        "dir":           request.args.get("dir") or None,
        "q":             request.args.get("q") or None,
    }
    # url_for omite los kwargs con valor None
    return redirect(url_for("alumnos.listar_alumnos", curso_id=curso_id, **filtros))


@alumnos_bp.route("/curso/<int:curso_id>/alumnos")
@requiere_staff
def listar_alumnos(curso_id):
    page         = request.args.get("page",         1,  type=int)
    estado_filtro = request.args.get("estado_filtro", "").strip()

    ok, alumnos, paginacion = obtener_alumnos_del_curso(
        curso_id,
        page=page,
        estado=estado_filtro or None,
    )
    if not ok:
        flash(alumnos, "danger")
        alumnos, paginacion = [], {}

    mostrar_modal     = request.args.get("modal") == "vincular"
    padron_buscado    = request.args.get("padron", "").strip()
    alumno_encontrado = None
    buscar_error      = None

    if mostrar_modal and padron_buscado:
        ok_b, resultado = buscar_alumno_por_padron(padron_buscado)
        if ok_b:
            alumno_encontrado = resultado
        else:
            buscar_error = resultado

    # búsqueda de texto sobre la página actual
    q = request.args.get("q", "").strip()
    if q:
        q_lower = q.lower()
        alumnos = [
            a for a in alumnos
            if q_lower in str(a.get("padron",   "")).lower()
            or q_lower in str(a.get("nombre",   "")).lower()
            or q_lower in str(a.get("apellido", "")).lower()
            or q_lower in str(a.get("email",    "")).lower()
            or q_lower in str(a.get("dni",      "")).lower()
        ]

    sort_col = request.args.get("sort", "apellido")
    sort_dir = request.args.get("dir",  "asc")

    if sort_col not in COLUMNAS_ORDENABLES:
        sort_col = "apellido"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "asc"

    alumnos = sorted(
        alumnos,
        key=lambda a: str(a.get(sort_col) or "").lower(),
        reverse=(sort_dir == "desc"),
    )

    return render_template(
        "alumnos.html",
        title="Alumnos",
        active_page="alumnos",
        curso_id=curso_id,
        alumnos=alumnos,
        paginacion=paginacion,
        page=page,
        mostrar_modal=mostrar_modal,
        padron_buscado=padron_buscado,
        alumno_encontrado=alumno_encontrado,
        buscar_error=buscar_error,
        q=q,
        estado_filtro=estado_filtro,
        sort_col=sort_col,
        sort_dir=sort_dir,
    )


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/vincular", methods=["POST"])
@requiere_staff
def vincular_alumno(curso_id):
    estudiante_id = request.form.get("estudiante_id", type=int)
    ok, resultado = vincular_alumno_a_curso(estudiante_id, curso_id)
    flash("Alumno vinculado al curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect_preservando_params(curso_id)


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/<int:inscripcion_id>/desvincular", methods=["POST"])
@requiere_staff
def desvincular_alumno(curso_id, inscripcion_id):
    ok, resultado = desvincular_alumno_del_curso(inscripcion_id)
    flash("Alumno desvinculado del curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect_preservando_params(curso_id)


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/<int:inscripcion_id>/estado", methods=["POST"])
@requiere_staff
def cambiar_estado(curso_id, inscripcion_id):
    nuevo_estado  = request.form.get("estado", "").strip()
    estudiante_id = request.form.get("estudiante_id", type=int)
    ok, resultado = cambiar_estado_inscripcion(
        inscripcion_id, estudiante_id, curso_id, nuevo_estado
    )
    flash(f"Estado actualizado a '{nuevo_estado}'." if ok else resultado,
          "success" if ok else "danger")
    return redirect_preservando_params(curso_id)


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/importar", methods=["POST"])
@requiere_staff
def importar(curso_id):
    archivo = request.files.get("csv_file")
    if not archivo or not archivo.filename:
        flash("Seleccioná un archivo CSV.", "warning")
        return redirect_preservando_params(curso_id)
    if not archivo.filename.lower().endswith(".csv"):
        flash("El archivo debe tener extensión .csv", "danger")
        return redirect_preservando_params(curso_id)

    ok, resultado = importar_csv(archivo, curso_id)
    if ok:
        flash(
            f"Importación completada: {resultado['exitosos']} inscriptos, "
            f"{resultado['duplicados']} duplicados ignorados, "
            f"{resultado['errores']} errores.",
            "success" if resultado["errores"] == 0 else "warning",
        )
    else:
        flash(f"Error en la importación: {resultado}", "danger")
    return redirect_preservando_params(curso_id)
