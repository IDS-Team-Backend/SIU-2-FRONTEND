from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
import utils.user_context as UserContext
import utils.api_client as api

from services.asistencia_service import (
    ESTADOS_ASISTENCIA,
    actualizar_planilla_asistencia,
    obtener_asistencia_clase,
    parsear_asistencias_form,
)

from services.clases_service import (
    DURACION_CLASE_DEFAULT,
    DURACIONES_CLASE,
    ESTADOS_CLASE_DEFAULT,
    HORAS_CLASE,
    MODALIDADES_CLASE,
    TIPOS_CLASE,
    actualizar_clase,
    agrupar_clases_por_dia,
    calcular_fecha_hora_fin,
    calcular_prefill_nueva_clase,
    combinar_fecha_hora,
    crear_clase,
    eliminar_clase,
    extraer_id_clase_creada,
    navegacion_calendario,
    obtener_clase_por_id,
    obtener_clases_del_curso,
    params_mes_desde_fecha,
)
from services.decorators import requiere_staff
from services.docentes_service import obtener_equipo_docente

clases_bp = Blueprint("clases", __name__)


def _resolver_profesor_id(curso_id):
    """Devuelve el profesor_id del usuario logueado, o el titular de la cursada si es admin."""
    profesor_id = UserContext.get_profesor_id()
    if profesor_id:
        return profesor_id
    # Admin sin registro de profesor: usar el titular de la cursada
    ok, equipo = obtener_equipo_docente(curso_id)
    if ok and equipo:
        titular = next((m for m in equipo if m.get("rol") == "titular"), equipo[0])
        return titular.get("docente_id")
    return None


def _redireccionar_a_mes_fecha(curso_id, fecha_texto):
    destino = {"curso_id": curso_id, **params_mes_desde_fecha(fecha_texto)}
    return redirect(url_for("clases.listar_clases", **destino))


@clases_bp.route("/curso/<int:curso_id>/clases", methods=["GET"])
def listar_clases(curso_id):
    ok_clases, clases = obtener_clases_del_curso(curso_id)
    if not ok_clases:
        flash(clases, "danger")
        clases = []

    calendario = navegacion_calendario(
        request.args.get("anio"),
        request.args.get("mes"),
    )
    fecha_prefill, hora_prefill = calcular_prefill_nueva_clase(
        request.args.get("fecha", "")
    )

    return render_template(
        "admin/clases/index.html",
        title="Clases",
        curso_id=curso_id,
        active_page="clases",
        clases_por_dia=agrupar_clases_por_dia(clases),
        tipos_clase=TIPOS_CLASE,
        modalidades_clase=MODALIDADES_CLASE,
        horas_clase=HORAS_CLASE,
        duraciones_clase=DURACIONES_CLASE,
        duracion_default=DURACION_CLASE_DEFAULT,
        fecha_prefill=fecha_prefill,
        hora_prefill=hora_prefill,
        **calendario,
    )


@clases_bp.route("/curso/<int:curso_id>/clases", methods=["POST"])
@requiere_staff
def crear_clase_route(curso_id):
    fecha = request.form.get("fecha", "").strip()
    hora_inicio = request.form.get("hora_inicio", "").strip()
    duracion = request.form.get("duracion_minutos", "").strip()

    fecha_hora_inicio = combinar_fecha_hora(fecha, hora_inicio)
    fecha_hora_fin = calcular_fecha_hora_fin(fecha, hora_inicio, duracion)

    profesor_id = _resolver_profesor_id(curso_id)
    if not profesor_id:
        flash("No hay docentes asignados a esta cursada.", "danger")
        return _redireccionar_a_mes_fecha(curso_id, fecha_hora_inicio)

    ok, resultado = crear_clase(
        curso_id=curso_id,
        profesor_id=profesor_id,
        nombre=request.form.get("nombre", "").strip(),
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        tema=request.form.get("tema", "").strip(),
        tipo=request.form.get("tipo", "").strip(),
        modalidad=request.form.get("modalidad", "").strip(),
        tags=request.form.get("tags", "").strip(),
        suspendida=request.form.get("suspendida") == "on",
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
def ver_clase(curso_id, clase_id):
    ok_clase, clase = obtener_clase_por_id(clase_id)
    if not ok_clase:
        flash(clase, "danger")
        return redirect(url_for("clases.listar_clases", curso_id=curso_id))
    
    if UserContext.es_staff():
        ok_asistencia, asistencia = obtener_asistencia_clase(clase_id)
        if not ok_asistencia:
            flash(asistencia, "danger")
            asistencia = {"planilla": [], "resumen": {}}
    else:
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
        tipos_clase=TIPOS_CLASE,
        modalidades_clase=MODALIDADES_CLASE,
        tema=clase.get("tema", ""),
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
        suspendida=request.form.get("suspendida") == "on",
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

# //////////////////////////////////////////////////
# /////////////////// ASISTENCIA ///////////////////
# //////////////////////////////////////////////////

@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/asistencia", methods=["POST"])
@requiere_staff
def actualizar_asistencia(curso_id, clase_id):
    asistencias = parsear_asistencias_form(request.form.items())
    ok, resultado = actualizar_planilla_asistencia(clase_id, asistencias)

    flash("Asistencia actualizada correctamente." if ok else resultado, "success" if ok else "danger")
    return redirect(url_for("clases.ver_clase", curso_id=curso_id, clase_id=clase_id))

@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/escanear", methods=["GET"])
@requiere_staff
def escanear_qr(curso_id, clase_id):
    return render_template(
        "admin/asistencia/escanear_qr.html",
        title="Escanear QR",
        curso_id=curso_id,
        clase_id=clase_id,
    )

@clases_bp.route("/curso/<int:curso_id>/clases/<int:clase_id>/escanear", methods=["POST"])
@requiere_staff
def escanear_qr_post(curso_id, clase_id):
    data = request.get_json(silent=True)
    if not data or not data.get("token"):
        return jsonify({"error": "Token inválido."}), 400

    ok, resultado = api.post("/asistencia/escanear", json={"token": data["token"], "clase_id": clase_id})
    if not ok:
        return jsonify({"error": resultado}), 400

    return jsonify(resultado.get("asistencia")), 200