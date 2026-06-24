import calendar
from datetime import date, datetime
from flask import render_template, request, redirect, url_for, flash

from services.decorators import requiere_staff
from services.evaluaciones_service import (
    obtener_evaluaciones_del_curso,
    crear_evaluacion,
    actualizar_evaluacion,
    eliminar_evaluacion,
)
from services.tipos_evaluaciones_service import (
    obtener_tipos_evaluacion,
)
from services.equipos_service import (
    obtener_equipos,
)
from services.equipo_integrantes_service import (
    obtener_integrantes,
)
from services.alumnos_service import (
    obtener_alumnos_del_curso,
)
from services.notas_service import (
    obtener_notas_por_equipo,
    obtener_notas_por_alumno,
)
from services.entregas_service import (
    obtener_entregas_por_equipo,
    obtener_entregas_por_alumno,
)

from routes.evaluaciones import (
    evaluaciones_bp,
    ESTADOS_ENTREGA,
    MESES_ES,
    ALUMNOS_POR_PAGINA,
    _parsear_fecha_eval,
)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones", methods=["GET"])
def listar_evaluaciones(curso_id):
    """Calendario mensual con las evaluaciones del curso en su día."""
    ok, evaluaciones = obtener_evaluaciones_del_curso(curso_id)
    if not ok:
        flash(evaluaciones, "danger")
        evaluaciones = []

    ok_tipos, tipos_evaluacion = obtener_tipos_evaluacion(curso_id)
    if not ok_tipos:
        flash(tipos_evaluacion, "danger")
        tipos_evaluacion = []

    hoy = date.today()

    # Mes a mostrar (default: mes actual)
    try:
        anio = int(request.args.get("anio", hoy.year))
        mes = int(request.args.get("mes", hoy.month))
    except (ValueError, TypeError):
        anio, mes = hoy.year, hoy.month
    if not (1 <= mes <= 12):
        anio, mes = hoy.year, hoy.month

    # Grilla del mes (semanas Lun–Dom, con días de meses adyacentes para completar)
    semanas = calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes)

    # Agrupar evaluaciones por día
    evaluaciones_por_dia = {}
    for e in evaluaciones:
        dia = _parsear_fecha_eval(e.get("fecha"))
        if dia is not None:
            evaluaciones_por_dia.setdefault(dia, []).append(e)

    # Navegación de meses
    prev_anio, prev_mes = (anio - 1, 12) if mes == 1 else (anio, mes - 1)
    next_anio, next_mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)

    return render_template(
        "admin/evaluaciones/index.html",
        title="Evaluaciones",
        curso_id=curso_id,
        active_page="evaluaciones",
        tipos_evaluacion=tipos_evaluacion,
        semanas=semanas,
        evaluaciones_por_dia=evaluaciones_por_dia,
        anio=anio,
        mes=mes,
        nombre_mes=MESES_ES[mes],
        prev_anio=prev_anio,
        prev_mes=prev_mes,
        next_anio=next_anio,
        next_mes=next_mes,
        hoy=hoy,
    )


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones", methods=["POST"])
@requiere_staff
def crear_nueva_evaluacion(curso_id):
    titulo = request.form.get("titulo", "").strip()
    tipo_evaluacion_id = request.form.get("tipo_evaluacion_id")
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    ok, resultado = crear_evaluacion(
        titulo,
        tipo_evaluacion_id,
        fecha,
        descripcion,
        curso_id
    )

    if ok:
        flash("Evaluación creada correctamente.", "success")
    else:
        flash(resultado, "danger")

    # Volver al calendario en el mes de la fecha creada (si se pudo parsear).
    destino = {"curso_id": curso_id}
    try:
        d = datetime.strptime(fecha, "%Y-%m-%d").date()
        destino["anio"] = d.year
        destino["mes"] = d.month
    except (ValueError, TypeError):
        pass

    return redirect(url_for("evaluaciones.listar_evaluaciones", **destino))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/actualizar", methods=["POST"])
@requiere_staff
def actualizar(curso_id, evaluacion_id):
    titulo = request.form.get("titulo", "").strip()
    tipo_evaluacion_id = request.form.get("tipo_evaluacion_id")
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    ok, resultado = actualizar_evaluacion(
        evaluacion_id,
        titulo,
        tipo_evaluacion_id,
        fecha,
        descripcion,
        curso_id
    )

    if ok:
        flash("Evaluación actualizada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.ver_evaluacion", curso_id=curso_id, evaluacion_id=evaluacion_id))


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar(curso_id, evaluacion_id):
    ok, resultado = eliminar_evaluacion(evaluacion_id)

    if ok:
        flash("Evaluación eliminada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("evaluaciones.listar_evaluaciones", curso_id=curso_id))


# ──────────────────────────────────────────────────────────────────────────────
# Record page: detalle de la evaluación con ABM de equipos + entregas/notas
# ──────────────────────────────────────────────────────────────────────────────

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>", methods=["GET"])
@requiere_staff
def ver_evaluacion(curso_id, evaluacion_id):
    ok, evaluaciones = obtener_evaluaciones_del_curso(curso_id)
    if not ok:
        flash(evaluaciones, "danger")
        return redirect(url_for("evaluaciones.listar_evaluaciones", curso_id=curso_id))

    evaluacion = next(
        (e for e in evaluaciones if str(e["id"]) == str(evaluacion_id)), None
    )
    if not evaluacion:
        flash("La evaluación no existe.", "danger")
        return redirect(url_for("evaluaciones.listar_evaluaciones", curso_id=curso_id))

    # Determinar si la evaluación es grupal (sólo entonces aplican equipos/entregas)
    ok_tipos, tipos_evaluacion = obtener_tipos_evaluacion(curso_id)
    if not ok_tipos:
        tipos_evaluacion = []
    tipo = next(
        (t for t in tipos_evaluacion if t["id"] == evaluacion.get("tipo_evaluacion_id")),
        None
    )
    # Si no llega es_grupal, mostramos la sección igual (sin equipos no hay filas).
    es_grupal = bool(tipo.get("es_grupal")) if tipo and "es_grupal" in tipo else True

    equipos = []
    alumnos = []
    notas_por_sujeto = {}
    entregas_por_sujeto = {}
    paginacion = None
    page = None
    page_size = None

    if es_grupal:
        ok_eq, equipos = obtener_equipos(curso_id, evaluacion_id)
        if not ok_eq:
            flash(equipos, "danger")
            equipos = []

        for equipo in equipos:
            ok_int, integrantes = obtener_integrantes(equipo["id"])
            equipo["integrantes"] = integrantes if ok_int else []

        ok_notas, notas_por_sujeto = obtener_notas_por_equipo(evaluacion_id)
        ok_ent, entregas_por_sujeto = obtener_entregas_por_equipo(evaluacion_id)
    else:
        page = request.args.get("page", 1, type=int) or 1
        page_size = request.args.get("page_size", ALUMNOS_POR_PAGINA, type=int) or ALUMNOS_POR_PAGINA
        page_size = max(1, min(page_size, 100))  # el backend limita page_size a 100
        ok_al, alumnos, paginacion = obtener_alumnos_del_curso(
            curso_id, page=page, page_size=page_size
        )
        if not ok_al:
            flash(alumnos, "danger")
            alumnos = []
            paginacion = None

        ok_notas, notas_por_sujeto = obtener_notas_por_alumno(evaluacion_id)
        ok_ent, entregas_por_sujeto = obtener_entregas_por_alumno(evaluacion_id)

    if not ok_notas:
        flash(notas_por_sujeto, "danger")
        notas_por_sujeto = {}
    if not ok_ent:
        flash(entregas_por_sujeto, "danger")
        entregas_por_sujeto = {}

    # Objetos "actuales" para los modales (controlados por ?accion= y los ids del query).
    equipo_actual = None
    alumno_actual = None
    nota_actual = None

    if request.args.get("equipo_id"):
        equipo_actual = next(
            (e for e in equipos if str(e["id"]) == str(request.args.get("equipo_id"))),
            None
        )

    if request.args.get("alumno_id"):
        alumno_actual = next(
            (a for a in alumnos if str(a["id"]) == str(request.args.get("alumno_id"))),
            None
        )

    if request.args.get("nota_id"):
        nota_actual = next(
            (n for n in notas_por_sujeto.values()
             if str(n["id"]) == str(request.args.get("nota_id"))),
            None
        )

    return render_template(
        "admin/evaluaciones/detalle.html",
        title=evaluacion.get("titulo", "Evaluación"),
        curso_id=curso_id,
        active_page="evaluaciones",
        evaluacion=evaluacion,
        tipos_evaluacion=tipos_evaluacion,
        es_grupal=es_grupal,
        equipos=equipos,
        alumnos=alumnos,
        paginacion=paginacion,
        page=page,
        page_size=page_size,
        notas_por_sujeto=notas_por_sujeto,
        entregas_por_sujeto=entregas_por_sujeto,
        estados_entrega=ESTADOS_ENTREGA,
        equipo_actual=equipo_actual,
        alumno_actual=alumno_actual,
        nota_actual=nota_actual,
        hoy=date.today().isoformat(),
    )
