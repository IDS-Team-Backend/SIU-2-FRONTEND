import math

from flask import Blueprint, render_template, request, redirect, flash, url_for
from services.decorators import requiere_staff
from services.alumnos_service import (
    obtener_alumnos_del_curso,
    buscar_alumno_por_padron,
    vincular_alumno_a_curso,
    desvincular_alumno_del_curso,
    cambiar_estado_inscripcion,
    importar_csv,
    crear_alumno,
    editar_alumno,
    vincular_alumnos_masivo,
    importar_estudiantes_csv,
    desvincular_alumnos_masivo
)
from services.ficha_estudiante_service import obtener_ficha_estudiante
from services.estudiantes_service import obtener_estudiantes, obtener_detalle_estudiante
from utils.filtros import leer_filtros, url_con_filtros

alumnos_bp = Blueprint("alumnos", __name__)

COLUMNAS_ORDENABLES = {"padron", "nombre", "apellido", "email", "estado"}


# ── Listado general de alumnos (catálogo del sistema) ────────────────────────────

@alumnos_bp.route("/alumnos")
@requiere_staff
def listar_general():
    page = request.args.get("page", 1, type=int) or 1
    page_size = request.args.get("page_size", 8, type=int) or 8
    page_size = max(1, min(page_size, 100))

    carrera = (request.args.get("carrera") or "").strip()
    anio = request.args.get("anio_ingreso", type=int)
    q = (request.args.get("q") or "").strip()

    ok, alumnos, paginacion = obtener_estudiantes(
        page=page,
        page_size=page_size,
        carrera=carrera or None,
        anio_ingreso=anio,
        q=q or None,
    )

    if not ok:
        flash(alumnos, "danger")
        alumnos, paginacion = [], {}

    return render_template(
        "admin/alumnos/listado.html",
        title="Alumnos",
        active_page="alumnos_general",
        alumnos=alumnos,
        paginacion=paginacion,
        page_size=page_size,
        carrera=carrera,
        anio_ingreso=anio,
        q=q,
        mostrar_modal=request.args.get("nuevo") == "1",
        form_data={},
    )


# ── Alta de estudiante (sistema): crear cuenta + perfil, sin inscribir a un curso ──

@alumnos_bp.route("/alumnos/crear", methods=["POST"])
@requiere_staff
def crear_general():
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
        return redirect(url_for("alumnos.listar_general"))

    flash(f"Error al crear estudiante: {error}", "danger")
    return redirect(url_for("alumnos.listar_general", nuevo="1"))


@alumnos_bp.route("/alumnos/importar-altas", methods=["POST"])
@requiere_staff
def importar_altas_general():
    archivo = request.files.get("csv_altas")
    if not archivo or not archivo.filename:
        flash("Seleccioná un archivo CSV.", "warning")
        return redirect(url_for("alumnos.listar_general"))
    if not archivo.filename.lower().endswith(".csv"):
        flash("El archivo debe tener extensión .csv", "danger")
        return redirect(url_for("alumnos.listar_general"))

    ok, resultado = importar_estudiantes_csv(archivo)
    if ok:
        flash(
            f"Altas completadas: {resultado['exitosos']} creados, "
            f"{resultado['duplicados']} duplicados ignorados, "
            f"{resultado['errores']} errores.",
            "success" if resultado["errores"] == 0 else "warning",
        )
    else:
        flash(f"Error en la importación: {resultado}", "danger")
    return redirect(url_for("alumnos.listar_general"))


# ── Ficha general del alumno (multi-curso) ───────────────────────────────────────

@alumnos_bp.route("/alumnos/<int:estudiante_id>")
@requiere_staff
def ver_alumno(estudiante_id):
    ok, detalle = obtener_detalle_estudiante(estudiante_id)
    if not ok:
        flash(detalle, "danger")
        return redirect(url_for("alumnos.listar_general"))

    return render_template(
        "admin/alumnos/detalle.html",
        title="Ficha de alumno",
        active_page="alumnos_general",
        detalle=detalle,
    )


@alumnos_bp.route("/curso/<int:curso_id>/alumnos")
@requiere_staff
def listar_alumnos(curso_id):
    f = leer_filtros()
    page          = f["page"]
    estado_filtro = f["estado_filtro"]
    q             = f["q"]
    sort_col      = f["sort"] if f["sort"] in COLUMNAS_ORDENABLES else "apellido"
    sort_dir      = f["dir"] if f["dir"] in ("asc", "desc") else "asc"
    page_size     = request.args.get("page_size", 8, type=int) or 8
    page_size     = max(1, min(page_size, 100))

    ok, alumnos, paginacion = obtener_alumnos_del_curso(
        curso_id, page=page, page_size=page_size, estado=estado_filtro or None, q=q or None,
    )
    if not ok:
        flash(alumnos, "danger")
        alumnos, paginacion = [], {}

    # ── Formulario activo (editar / vincular) ──────────────────────────────
    form_activo  = request.args.get("form", "")   # "editar" | "vincular" | ""
    alumno_editar = None

    if form_activo == "editar":
        eid = request.args.get("estudiante_id", type=int)
        alumno_editar = next((a for a in alumnos if a["estudiante_id"] == eid), None)
        if not alumno_editar:
            flash("No se encontró el alumno para editar.", "warning")
            form_activo = ""

    # ── Modal vincular (flujo existente) ──────────────────────────────────
    mostrar_modal     = form_activo == "vincular"
    padron_buscado    = request.args.get("padron", "").strip()
    alumno_encontrado = None
    buscar_error      = None

    if mostrar_modal and padron_buscado:
        ok_b, resultado = buscar_alumno_por_padron(padron_buscado)
        if ok_b:
            alumno_encontrado = resultado
        else:
            buscar_error = resultado


    alumnos = sorted(
        alumnos,
        key=lambda a: str(a.get(sort_col) or "").lower(),
        reverse=(sort_dir == "desc"),
    )

    return render_template(
        "admin/alumnos/index.html",
        title="Alumnos",
        active_page="alumnos",
        curso_id=curso_id,
        alumnos=alumnos,
        paginacion=paginacion,
        page_size=page_size,
        url_con_filtros=url_con_filtros,
        form_activo=form_activo,
        alumno_editar=alumno_editar,
        mostrar_modal=mostrar_modal,
        padron_buscado=padron_buscado,
        alumno_encontrado=alumno_encontrado,
        buscar_error=buscar_error,
        q=q,
        estado_filtro=estado_filtro,
        sort_col=sort_col,
        sort_dir=sort_dir,
    )


# ── Ficha del alumno en el curso (Page A) ───────────────────────────────────────

FICHA_POR_PAGINA = 8


def _paginar_lista(items, page):
    """Pagina una lista en memoria (misma lógica que alumnos: 8 por página).
    Retorna (pagina, paginacion) con paginacion={page, total_paginas, total}."""
    total = len(items)
    total_paginas = max(1, math.ceil(total / FICHA_POR_PAGINA))
    page = max(1, min(page, total_paginas))
    inicio = (page - 1) * FICHA_POR_PAGINA
    return items[inicio:inicio + FICHA_POR_PAGINA], {
        "page": page,
        "total_paginas": total_paginas,
        "total": total,
    }


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/<int:estudiante_id>")
@requiere_staff
def ver_ficha(curso_id, estudiante_id):
    ok, ficha = obtener_ficha_estudiante(curso_id, estudiante_id)
    if not ok:
        flash(ficha, "danger")
        return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))

    eval_page = request.args.get("eval_page", 1, type=int) or 1
    asis_page = request.args.get("asis_page", 1, type=int) or 1
    evaluaciones_pagina, eval_paginacion = _paginar_lista(ficha["evaluaciones"], eval_page)
    asistencia_pagina, asis_paginacion = _paginar_lista(ficha["asistencia_detalle"], asis_page)

    return render_template(
        "admin/alumnos/ficha.html",
        title="Ficha del alumno",
        active_page="alumnos",
        curso_id=curso_id,
        ficha=ficha,
        evaluaciones_pagina=evaluaciones_pagina,
        eval_paginacion=eval_paginacion,
        asistencia_pagina=asistencia_pagina,
        asis_paginacion=asis_paginacion,
    )


# ── Editar ─────────────────────────────────────────────────────────────────────

@alumnos_bp.route("/curso/<int:curso_id>/alumnos/<int:estudiante_id>/editar", methods=["POST"])
@requiere_staff
def editar(curso_id, estudiante_id):
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
        flash(f"Error al editar alumno: {error}", "danger")

    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))


# ── Vincular ───────────────────────────────────────────────────────────────────

@alumnos_bp.route("/curso/<int:curso_id>/alumnos/vincular", methods=["POST"])
@requiere_staff
def vincular_alumno(curso_id):
    estudiante_id = request.form.get("estudiante_id", type=int)
    ok, resultado = vincular_alumno_a_curso(estudiante_id, curso_id)
    flash("Alumno vinculado al curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/<int:inscripcion_id>/desvincular", methods=["POST"])
@requiere_staff
def desvincular_alumno(curso_id, inscripcion_id):
    ok, resultado = desvincular_alumno_del_curso(inscripcion_id)
    flash("Alumno desvinculado del curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))


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
    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/importar", methods=["POST"])
@requiere_staff
def importar(curso_id):
    archivo = request.files.get("csv_file")
    if not archivo or not archivo.filename:
        flash("Seleccioná un archivo CSV.", "warning")
        return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))
    if not archivo.filename.lower().endswith(".csv"):
        flash("El archivo debe tener extensión .csv", "danger")
        return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))

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
    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))


@alumnos_bp.route("/curso/<int:curso_id>/alumnos/vincular-masivo", methods=["POST"])
@requiere_staff
def vincular_masivo(curso_id):
    # checkboxes name="seleccionados" lista de estudiante_id
    ids_raw = request.form.getlist("seleccionados")
    estudiante_ids = []
    for v in ids_raw:
        try:
            estudiante_ids.append(int(v))
        except (ValueError, TypeError):
            pass
 
    if not estudiante_ids:
        flash("No seleccionaste ningún alumno.", "warning")
        return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))
 
    ok, resumen = vincular_alumnos_masivo(estudiante_ids, curso_id)
 
    if not ok:
        flash(f"Error: {resumen}", "danger")
    else:
        msg = (f"{resumen['vinculados']} vinculados, "
               f"{resumen['duplicados']} ya estaban inscriptos, "
               f"{resumen['errores']} con error.")
        categoria = "success" if resumen["errores"] == 0 else "warning"
        flash(msg, categoria)
 
    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))

@alumnos_bp.route("/curso/<int:curso_id>/alumnos/desvincular-masivo", methods=["POST"])
@requiere_staff
def desvincular_masivo(curso_id):
    ids_raw = request.form.getlist("seleccionados")
    estudiante_ids = [int(v) for v in ids_raw if v.isdigit()]

    if not estudiante_ids:
        flash("No seleccionaste ningún alumno.", "warning")
        return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))

    ok, resumen = desvincular_alumnos_masivo(estudiante_ids, curso_id)
    if ok:
        flash(f"{resumen['desvinculados']} desvinculados, {resumen['errores']} con error.",
              "success" if resumen["errores"] == 0 else "warning")
    else:
        flash(f"Error: {resumen}", "danger")
    return redirect(url_con_filtros("alumnos.listar_alumnos", curso_id=curso_id))