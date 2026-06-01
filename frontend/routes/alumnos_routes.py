import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

COLUMNAS_ORDENABLES = {"padron", "nombre", "apellido", "email", "estado"}


@alumnos_bp.route("/alumnos")
@requiere_staff
def listar_alumnos():
    ok, alumnos = obtener_alumnos_del_curso(CURSO_ACTIVO_ID)
    if not ok:
        flash(alumnos, "danger")
        alumnos = []

    # modal del vincular
    mostrar_modal   = request.args.get("modal") == "vincular"
    padron_buscado  = request.args.get("padron", "").strip()
    alumno_encontrado = None
    buscar_error    = None

    if mostrar_modal and padron_buscado:
        ok_b, resultado = buscar_alumno_por_padron(padron_buscado)
        if ok_b:
            alumno_encontrado = resultado
        else:
            buscar_error = resultado

    #Buqueda y filtro 
    q             = request.args.get("q", "").strip()
    estado_filtro = request.args.get("estado_filtro", "")

    if q:
        q_lower = q.lower()
        alumnos = [
            a for a in alumnos
            if q_lower in str(a.get("padron", "")).lower()
            or q_lower in str(a.get("nombre",   "")).lower()
            or q_lower in str(a.get("apellido", "")).lower()
            or q_lower in str(a.get("email",    "")).lower()
            or q_lower in str(a.get("dni", "")).lower()
        ]

    if estado_filtro:
        alumnos = [a for a in alumnos if a.get("estado") == estado_filtro]

    # Ordenamiento 
    sort_col = request.args.get("sort", "padron")
    sort_dir = request.args.get("dir",  "asc")

    if sort_col not in COLUMNAS_ORDENABLES:
        sort_col = "padron"
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
        alumnos=alumnos,
        # modal
        mostrar_modal=mostrar_modal,
        padron_buscado=padron_buscado,
        alumno_encontrado=alumno_encontrado,
        buscar_error=buscar_error,
        # filtros activos (para mantenerlos en la URL)
        q=q,
        estado_filtro=estado_filtro,
        sort_col=sort_col,
        sort_dir=sort_dir,
    )


@alumnos_bp.route("/alumnos/vincular", methods=["POST"])
@requiere_staff
def vincular_alumno():
    usuario_id = request.form.get("usuario_id", type=int)
    ok, resultado = vincular_alumno_a_curso(usuario_id, CURSO_ACTIVO_ID)
    flash("Alumno vinculado al curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("alumnos.listar_alumnos"))


@alumnos_bp.route("/alumnos/<int:inscripcion_id>/desvincular", methods=["POST"])
@requiere_staff
def desvincular_alumno(inscripcion_id):
    ok, resultado = desvincular_alumno_del_curso(inscripcion_id)
    flash("Alumno desvinculado del curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("alumnos.listar_alumnos"))


@alumnos_bp.route("/alumnos/<int:inscripcion_id>/estado", methods=["POST"])
@requiere_staff
def cambiar_estado(inscripcion_id):
    nuevo_estado = request.form.get("estado", "").strip()
    usuario_id   = request.form.get("usuario_id", type=int)
    curso_id     = request.form.get("curso_id",   type=int)
    ok, resultado = cambiar_estado_inscripcion(
        inscripcion_id, usuario_id, curso_id, nuevo_estado
    )
    flash(f"Estado actualizado a '{nuevo_estado}'." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("alumnos.listar_alumnos"))


@alumnos_bp.route("/alumnos/importar", methods=["POST"])
@requiere_staff
def importar():
    archivo = request.files.get("csv_file")
    if not archivo or not archivo.filename:
        flash("Seleccioná un archivo CSV.", "warning")
        return redirect(url_for("alumnos.listar_alumnos"))
    if not archivo.filename.lower().endswith(".csv"):
        flash("El archivo debe tener extensión .csv", "danger")
        return redirect(url_for("alumnos.listar_alumnos"))

    ok, resultado = importar_csv(archivo, CURSO_ACTIVO_ID)
    if ok:
        flash(
            f"Importación completada: {resultado['exitosos']} inscriptos, "
            f"{resultado['duplicados']} duplicados ignorados, "
            f"{resultado['errores']} errores.",
            "success" if resultado["errores"] == 0 else "warning",
        )
    else:
        flash(f"Error en la importación: {resultado}", "danger")
    return redirect(url_for("alumnos.listar_alumnos"))