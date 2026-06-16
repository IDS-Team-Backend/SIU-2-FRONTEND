from flask import Blueprint, render_template, request, redirect, flash, url_for

from services.decorators import requiere_staff
from services.cursos_service import (
    obtener_curso_para_vista,
    actualizar_curso,
    obtener_materias,
    cambiar_estado_curso,
    listar_cursadas,
    activar_cursada,
    crear_siguiente_cursada,
    transiciones_disponibles,
    ESTADO_LABELS,
)
from services.docentes_service import (
    obtener_equipo_docente,
    agregar_docente,
    cambiar_participacion,
    quitar_docente,
    ROLES_PARTICIPACION,
)
from services.profesores_service import buscar_profesor_por_legajo

gestion_bp = Blueprint("gestion", __name__)


@gestion_bp.route("/historial")
@requiere_staff
def historial():
    cursadas = listar_cursadas()
    return render_template(
        "admin/historial/index.html",
        title="Historial de cursadas",
        active_page="historial",
        cursadas=cursadas,
        estado_labels=ESTADO_LABELS,
    )


@gestion_bp.route("/historial/activar", methods=["POST"])
@requiere_staff
def historial_activar():
    cursada_id = request.form.get("cursada_id", type=int)
    if not cursada_id:
        flash("No se indicó la cursada a activar.", "danger")
        return redirect(url_for("gestion.historial"))
    ok, resultado = activar_cursada(cursada_id)
    flash("Cursada activada." if ok else resultado, "success" if ok else "danger")
    return redirect(url_for("gestion.historial"))


@gestion_bp.route("/curso/<int:curso_id>/gestion")
@requiere_staff
def gestionar(curso_id):
    ok, curso = obtener_curso_para_vista(curso_id)
    if not ok:
        flash(curso, "danger")
        curso = {}

    ok_eq, integrantes = obtener_equipo_docente(curso_id)
    if not ok_eq:
        flash(integrantes, "danger")
        integrantes = []

    materias = obtener_materias()

    mostrar_modal       = request.args.get("modal") == "agregar"
    legajo_buscado      = request.args.get("legajo", "").strip()
    profesor_encontrado = None
    buscar_error        = None
    if mostrar_modal and legajo_buscado:
        ok_b, resultado = buscar_profesor_por_legajo(legajo_buscado)
        if ok_b:
            profesor_encontrado = resultado
        else:
            buscar_error = resultado

    estados = [{"key": k, "label": v} for k, v in ESTADO_LABELS.items()]
    cursadas = listar_cursadas()

    return render_template(
        "admin/gestion/index.html",
        title="Gestión de la cursada",
        active_page="gestion",
        active_section=request.args.get("seccion", "estado"),
        curso_id=curso_id,
        curso=curso,
        materias=materias,
        integrantes=integrantes,
        roles=ROLES_PARTICIPACION,
        estados=estados,
        transiciones=transiciones_disponibles(curso),
        cursadas=cursadas,
        estado_labels=ESTADO_LABELS,
        mostrar_modal=mostrar_modal,
        legajo_buscado=legajo_buscado,
        profesor_encontrado=profesor_encontrado,
        buscar_error=buscar_error,
    )


@gestion_bp.route("/curso/<int:curso_id>/gestion/estado", methods=["POST"])
@requiere_staff
def cambiar_estado(curso_id):
    nuevo_estado = (request.form.get("estado") or "").strip()
    ok, resultado = cambiar_estado_curso(curso_id, nuevo_estado)
    flash("Estado de la cursada actualizado." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))


@gestion_bp.route("/curso/<int:curso_id>/gestion/activar", methods=["POST"])
@requiere_staff
def activar(curso_id):
    # Se activa la cursada indicada en el form (la del panel) o, por defecto, la actual.
    objetivo = request.form.get("cursada_id", type=int) or curso_id
    ok, resultado = activar_cursada(objetivo)
    flash("Cursada activada (la anterior quedó finalizada)." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))


@gestion_bp.route("/curso/<int:curso_id>/gestion/crear-siguiente", methods=["POST"])
@requiere_staff
def crear_siguiente(curso_id):
    ok, resultado = crear_siguiente_cursada()
    if ok:
        flash("Siguiente cursada creada y activada. La anterior quedó finalizada.", "success")
        nuevo = (resultado.get("curso") or {}) if isinstance(resultado, dict) else {}
        return redirect(url_for("gestion.gestionar", curso_id=nuevo.get("id") or curso_id))
    flash(resultado, "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))


@gestion_bp.route("/curso/<int:curso_id>/gestion/info", methods=["POST"])
@requiere_staff
def actualizar_info(curso_id):
    form = request.form
    datos = {
        "materia_id":      form.get("materia_id", type=int),
        "nombre":          (form.get("nombre") or "").strip(),
        "anio":            form.get("anio", type=int),
        "cuatrimestre":    form.get("cuatrimestre", type=int),
        "descripcion":     (form.get("descripcion") or "").strip(),
        "modalidad":       (form.get("modalidad") or "").strip(),
        "carrera":         (form.get("carrera") or "").strip(),
        "horas_semanales": form.get("horas_semanales", type=int),
    }
    ok, resultado = actualizar_curso(curso_id, datos)
    flash("Información de la cursada actualizada." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))


@gestion_bp.route("/curso/<int:curso_id>/gestion/docentes/agregar", methods=["POST"])
@requiere_staff
def agregar_docente_curso(curso_id):
    docente_id = request.form.get("docente_id", type=int)
    rol = (request.form.get("rol") or "").strip()
    ok, resultado = agregar_docente(curso_id, docente_id, rol)
    flash("Integrante agregado al curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))


@gestion_bp.route("/curso/<int:curso_id>/gestion/docentes/<int:integrante_id>/participacion", methods=["POST"])
@requiere_staff
def cambiar_participacion_curso(curso_id, integrante_id):
    rol = (request.form.get("rol") or "").strip()
    ok, resultado = cambiar_participacion(integrante_id, rol)
    flash(f"Participación actualizada a '{rol}'." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))


@gestion_bp.route("/curso/<int:curso_id>/gestion/docentes/<int:integrante_id>/quitar", methods=["POST"])
@requiere_staff
def quitar_docente_curso(curso_id, integrante_id):
    ok, resultado = quitar_docente(integrante_id)
    flash("Integrante quitado del curso." if ok else resultado,
          "success" if ok else "danger")
    return redirect(url_for("gestion.gestionar", curso_id=curso_id))
