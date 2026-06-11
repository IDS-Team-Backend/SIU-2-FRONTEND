from flask import Blueprint, flash, redirect, render_template, request, url_for
import utils.user_context as UserContext

from services.asistencia_service import (
    ESTADOS_ASISTENCIA,
    actualizar_planilla_asistencia,
    generar_qrs_clase,
    obtener_asistencia_clase,
    parsear_asistencias_form,
)

from services.clases_service import (
    ESTADOS_CLASE_DEFAULT,
    MODALIDADES_CLASE,
    TIPOS_CLASE,
    actualizar_clase,
    agrupar_clases_por_dia,
    calcular_prefill_nueva_clase,
    crear_clase,
    eliminar_clase,
    extraer_id_clase_creada,
    navegacion_calendario,
    obtener_clase_por_id,
    obtener_clases_del_curso,
    obtener_estados_clase,
    params_mes_desde_fecha,
)
from services.decorators import requiere_staff

clases_bp = Blueprint("clases", __name__)


def _redireccionar_a_mes_fecha(curso_id, fecha_texto):
    destino = {"curso_id": curso_id, **params_mes_desde_fecha(fecha_texto)}
    return redirect(url_for("clases.listar_clases", **destino))


@clases_bp.route("/curso/<int:curso_id>/clases", methods=["GET"])
@requiere_staff
def listar_clases(curso_id):
    ok_clases, clases = obtener_clases_del_curso(curso_id)
    if not ok_clases:
        flash(clases, "danger")
        clases = []

    ok_estados, estados_clase = obtener_estados_clase()
    if not ok_estados:
        estados_clase = []

    calendario = navegacion_calendario(
        request.args.get("anio"),
        request.args.get("mes"),
    )
    fecha_inicio_prefill, fecha_fin_prefill = calcular_prefill_nueva_clase(
        request.args.get("fecha", "")
    )

    return render_template(
        "admin/clases/index.html",
        title="Clases",
        curso_id=curso_id,
        active_page="clases",
        clases_por_dia=agrupar_clases_por_dia(clases),
        estados_clase=estados_clase or ESTADOS_CLASE_DEFAULT,
        tipos_clase=TIPOS_CLASE,
        modalidades_clase=MODALIDADES_CLASE,
        fecha_inicio_prefill=fecha_inicio_prefill,
        fecha_fin_prefill=fecha_fin_prefill,
        **calendario,
    )


@clases_bp.route("/curso/<int:curso_id>/clases", methods=["POST"])
@requiere_staff
def crear_clase_route(curso_id):
    fecha_hora_inicio = request.form.get("fecha_hora_inicio", "").strip()

    profesor_id = UserContext.get_profesor_id()
    if not profesor_id:
        flash("No tienes permisos de profesor para crear una clase.", "danger")
        return _redireccionar_a_mes_fecha(curso_id, fecha_hora_inicio)

    ok, resultado = crear_clase(
        curso_id=curso_id,
        profesor_id=profesor_id,
        nombre=request.form.get("nombre", "").strip(),
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=request.form.get("fecha_hora_fin", "").strip(),
        tema=request.form.get("tema", "").strip(),
        tipo=request.form.get("tipo", "").strip(),
        modalidad=request.form.get("modalidad", "").strip(),
        tags=request.form.get("tags", "").strip(),
        status=request.form.get("status", "").strip(),
    )

    if ok:
        flash("Clase creada correctamente.", "success")
        clase_id = extraer_id_clase_creada(resultado)
        if clase_id:
            return redirect(url_for("clases.ver_clase", curso_id=curso_id, clase_id=clase_id))
        return _redireccionar_a_mes_fecha(curso_id, fecha_hora_inicio)

    flash(resultado, "danger")
    return _redireccionar_a_mes_fecha(curso_id, fecha_hora_inicio)


@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>", methods=["GET"])
@requiere_staff
def ver_clase(curso_id, clase_id):
    ok_clase, clase = obtener_clase_por_id(clase_id)
    if not ok_clase:
        flash(clase, "danger")
        return redirect(url_for("clases.listar_clases", curso_id=curso_id))

    ok_asistencia, asistencia = obtener_asistencia_clase(clase_id)
    if not ok_asistencia:
        flash(asistencia, "danger")
        asistencia = {"planilla": [], "resumen": {}}

    return render_template(
        "admin/clases/detalle.html",
        title=clase.get("nombre", "Clase"),
        curso_id=curso_id,
        clase=clase,
        active_page="clases",
        planilla_asistencia=asistencia["planilla"],
        resumen_asistencia=asistencia["resumen"],
        estados_asistencia=ESTADOS_ASISTENCIA,
        estados_clase=ESTADOS_CLASE_DEFAULT,
        tipos_clase=TIPOS_CLASE,
        modalidades_clase=MODALIDADES_CLASE,
    )


@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/actualizar", methods=["POST"])
@requiere_staff
def actualizar_clase_route(curso_id, clase_id):
    ok, resultado = actualizar_clase(
        clase_id=clase_id,
        nombre=request.form.get("nombre", "").strip(),
        fecha_hora_inicio=request.form.get("fecha_hora_inicio", "").strip(),
        fecha_hora_fin=request.form.get("fecha_hora_fin", "").strip(),
        tema=request.form.get("tema", "").strip(),
        tipo=request.form.get("tipo", "").strip(),
        modalidad=request.form.get("modalidad", "").strip(),
        tags=request.form.get("tags", "").strip(),
        status=request.form.get("status", "").strip(),
        metodo="PATCH",
    )

    if ok:
        flash("Clase actualizada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("clases.ver_clase", curso_id=curso_id, clase_id=clase_id))


@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/eliminar", methods=["POST"])
@requiere_staff
def eliminar_clase_route(curso_id, clase_id):
    ok, resultado = eliminar_clase(clase_id)

    if ok:
        flash("Clase eliminada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("clases.listar_clases", curso_id=curso_id))


@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/generar-qrs", methods=["POST"])
@requiere_staff
def generar_qrs(curso_id, clase_id):
    ok, resultado = generar_qrs_clase(clase_id)

    if ok:
        flash("QRs generados y enviados correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("clases.ver_clase", curso_id=curso_id, clase_id=clase_id))


@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/asistencia", methods=["POST"])
@requiere_staff
def actualizar_asistencia(curso_id, clase_id):
    print(request.form, flush=True)
    asistencias = parsear_asistencias_form(request.form.items())
    ok, resultado = actualizar_planilla_asistencia(clase_id, asistencias)

    if ok:
        flash("Asistencia actualizada correctamente.", "success")
    else:
        flash(resultado, "danger")

    return redirect(url_for("clases.ver_clase", curso_id=curso_id, clase_id=clase_id))
