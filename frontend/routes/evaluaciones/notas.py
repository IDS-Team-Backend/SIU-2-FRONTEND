from datetime import datetime

from flask import request, flash

from services.decorators import requiere_staff
from services.notas_service import (
    crear_nota,
    actualizar_nota,
    eliminar_nota,
    obtener_notas_por_alumno,
)
from services.entregas_service import (
    crear_entrega,
    obtener_entregas_por_equipo,
    obtener_entregas_por_alumno,
)

from routes.evaluaciones import evaluaciones_bp, _volver_a_evaluacion


# ── Notas (corrección: cargar / editar / quitar; cargar exige entrega) ────────

@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/equipos/<int:equipo_id>/nota", methods=["POST"])
@requiere_staff
def cargar_nota_equipo(curso_id, evaluacion_id, equipo_id):
    ok_ent, entregas = obtener_entregas_por_equipo(evaluacion_id)
    if not ok_ent or equipo_id not in entregas:
        flash("Registrá la entrega del equipo antes de cargar la nota.", "danger")
        return _volver_a_evaluacion(curso_id, evaluacion_id)

    ok, resultado = crear_nota(
        evaluacion_id,
        request.form.get("nota", "").strip(),
        request.form.get("observaciones", "").strip(),
        equipo_id=equipo_id,
    )
    flash("Nota cargada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/alumnos/<int:alumno_id>/nota", methods=["POST"])
@requiere_staff
def cargar_nota_alumno(curso_id, evaluacion_id, alumno_id):
    ok_ent, entregas = obtener_entregas_por_alumno(evaluacion_id)
    if not ok_ent or alumno_id not in entregas:
        flash("Registrá la entrega del alumno antes de cargar la nota.", "danger")
        return _volver_a_evaluacion(curso_id, evaluacion_id)

    ok, resultado = crear_nota(
        evaluacion_id,
        request.form.get("nota", "").strip(),
        request.form.get("observaciones", "").strip(),
        alumno_id=alumno_id,
    )
    flash("Nota cargada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/notas/<int:nota_id>/actualizar", methods=["POST"])
@requiere_staff
def editar_nota(curso_id, evaluacion_id, nota_id):
    ok, resultado = actualizar_nota(
        nota_id,
        request.form.get("nota", "").strip(),
        request.form.get("observaciones", ""),
    )
    flash("Nota actualizada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/notas/<int:nota_id>/eliminar", methods=["POST"])
@requiere_staff
def borrar_nota(curso_id, evaluacion_id, nota_id):
    ok, resultado = eliminar_nota(nota_id)
    flash("Nota eliminada correctamente." if ok else resultado, "success" if ok else "danger")
    return _volver_a_evaluacion(curso_id, evaluacion_id)


# ── Carga masiva (evaluación individual): registra entregas y carga/edita notas
#    de varios alumnos en un solo submit. Mantiene el flujo entrega→nota: la nota
#    solo se guarda si el alumno tiene (o se le acaba de registrar) una entrega.
#    Solo orquesta llamadas a la API existente; no cambia el backend. ───────────
@evaluaciones_bp.route("/curso/<int:curso_id>/evaluaciones/<int:evaluacion_id>/guardar-masivo", methods=["POST"])
@requiere_staff
def guardar_masivo(curso_id, evaluacion_id):
    # Fecha de la entrega: el momento de la carga (formato datetime-local, que el
    # service normaliza a DATETIME de MySQL).
    fecha_entrega = datetime.now().strftime("%Y-%m-%dT%H:%M")

    ok_e, entregas = obtener_entregas_por_alumno(evaluacion_id)
    ok_n, notas = obtener_notas_por_alumno(evaluacion_id)
    entregas = entregas if ok_e else {}
    notas = notas if ok_n else {}

    n_entregas = 0
    n_notas = 0
    errores = []

    def _num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    # Recolectar los alumnos del form: los que NO tienen entrega traen entrega_<id>
    # (select); los que YA tienen entrega solo traen nota_<id> (la entrega es un
    # badge, no un campo). Hay que recorrer ambos para no saltear a estos últimos.
    alumno_ids = set()
    for key in request.form.keys():
        for prefijo in ("entrega_", "nota_"):
            if key.startswith(prefijo):
                try:
                    alumno_ids.add(int(key[len(prefijo):]))
                except ValueError:
                    pass

    for alumno_id in alumno_ids:
        estado = (request.form.get(f"entrega_{alumno_id}") or "").strip()
        nota_val = (request.form.get(f"nota_{alumno_id}") or "").strip()

        tiene_entrega = alumno_id in entregas
        tiene_nota = alumno_id in notas

        # 1) Registrar entrega si se eligió un estado y todavía no la tenía.
        if estado and not tiene_entrega:
            ok, res = crear_entrega(evaluacion_id, fecha_entrega, estado, alumno_id=alumno_id)
            if ok:
                n_entregas += 1
                tiene_entrega = True
            else:
                errores.append(f"alumno {alumno_id}: {res}")
                continue

        # 2) Cargar/editar nota: solo si hay valor, tiene entrega, y CAMBIÓ
        #    respecto a la nota actual (el form reenvía todas las filas, no solo
        #    las tocadas; sin esta comparación re-procesaríamos notas sin cambio).
        if nota_val and tiene_entrega:
            actual = notas.get(alumno_id, {}).get("nota") if tiene_nota else None
            if _num(nota_val) == _num(actual):
                continue  # la nota no cambió, no la tocamos

            if tiene_nota:
                ok, res = actualizar_nota(notas[alumno_id]["id"], nota_val)
            else:
                ok, res = crear_nota(evaluacion_id, nota_val, alumno_id=alumno_id)
            if ok:
                n_notas += 1
            else:
                errores.append(f"alumno {alumno_id}: {res}")

    if n_entregas or n_notas:
        flash(f"Guardado: {n_entregas} entrega(s) y {n_notas} nota(s).", "success")
    elif not errores:
        flash("No hubo cambios para guardar.", "info")
    if errores:
        flash(f"{len(errores)} con error: " + "; ".join(errores[:3]), "danger")

    return _volver_a_evaluacion(curso_id, evaluacion_id)
