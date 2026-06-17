from utils import api_client as api


def _to_float(valor):
    if valor is None:
        return None
    try:
        return float(valor)
    except (ValueError, TypeError):
        return None


def _estado_nota(nota):
    """Aprobada (>=4) / Desaprobada / Pendiente (sin nota)."""
    if nota is None:
        return "Pendiente"
    return "Aprobada" if nota >= 4 else "Desaprobada"


def _variante_promedio(promedio):
    """Color de la tarjeta de promedio: ok (>=4) / bad / muted (sin notas)."""
    if promedio is None:
        return "muted"
    return "ok" if promedio >= 4 else "bad"


def _variante_asistencia(porcentaje):
    """Color de la tarjeta de asistencia según el porcentaje (None -> muted)."""
    if porcentaje is None:
        return "muted"
    if porcentaje >= 75:
        return "ok"
    if porcentaje >= 50:
        return "warn"
    return "bad"


def _nota_en_evaluacion(curso_id, padron, evaluacion_id):
    """Nota del alumno en una evaluación (individual o grupal, vía /reportes/alumnos).
    Retorna el número o None si no tiene nota."""
    if evaluacion_id is None or padron is None:
        return None
    ok, data = api.get("/reportes/alumnos", params={
        "curso_id": curso_id, "padron": padron, "evaluacion_id": evaluacion_id,
    })
    resultados = (data or {}).get("resultados", []) if ok else []
    if not resultados:
        return None
    return _to_float(resultados[0].get("nota_evaluacion"))


def obtener_ficha_estudiante(curso_id, estudiante_id):
    """Ficha del estudiante en un curso (Page A): identidad + estado + notas + asistencia.

    Compone varios endpoints staff del backend (los `/me` no aplican porque los
    alumnos no se loguean). Las notas incluyen las grupales vía /reportes/alumnos.
    Retorna (ok, ficha)."""

    # ── Identidad ───────────────────────────────────────────────
    ok_est, est = api.get(f"/estudiantes/{estudiante_id}")
    if not ok_est:
        if est and est.get("status_code") == 404:
            return False, "Estudiante no encontrado."
        return False, est.get("error", "Error al obtener el estudiante.") if est else "Error de conexión."

    padron = est.get("padron")

    # ── Inscripción / estado en el curso (fuente correcta: estudiante_curso) ──
    ok_ec, data_ec = api.get(
        "/estudiante_curso/", params={"curso_id": curso_id, "estudiante_id": estudiante_id}
    )
    inscripciones = (data_ec or {}).get("estudiante_cursos", []) if ok_ec else []
    if not inscripciones:
        return False, "El alumno no está inscripto en este curso."
    estado_cursada = (inscripciones[0].get("estado") or "activo").capitalize()

    # ── Datos del curso ─────────────────────────────────────────
    ok_curso, curso = api.get(f"/cursos/{curso_id}")
    curso = curso if (ok_curso and curso) else {}

    # ── Evaluaciones del curso, con la nota del alumno en cada una ──
    ok_ev, data_ev = api.get("/evaluaciones/", params={"curso_id": curso_id})
    evaluaciones = (data_ev or {}).get("evaluaciones", []) if ok_ev else []

    evaluaciones_con_nota = []
    notas = []
    for ev in evaluaciones:
        nota = _nota_en_evaluacion(curso_id, padron, ev.get("id"))
        if nota is not None:
            notas.append(nota)
        evaluaciones_con_nota.append({
            "titulo": ev.get("titulo", "—"),
            "tipo":   ev.get("tipo_evaluacion", "—"),
            "fecha":  ev.get("fecha"),
            "nota":   nota,
            "estado": _estado_nota(nota),
        })

    promedio = round(sum(notas) / len(notas), 2) if notas else None

    # ── Asistencia (endpoint staff) ─────────────────────────────
    ok_asis, data_asis = api.get(f"/asistencia/cursos/{curso_id}/alumnos/{estudiante_id}")
    asis = (data_asis or {}).get("asistencias", {}) if ok_asis else {}
    total_clases = asis.get("total_clases", 0)
    porcentaje = asis.get("porcentaje_asistencia") if total_clases else None

    ficha = {
        "id":             est.get("id"),
        "nombre":         est.get("nombre",   "—"),
        "apellido":       est.get("apellido", "—"),
        "email":          est.get("email",    "—"),
        "dni":            est.get("dni",      "—"),
        "padron":         padron if padron is not None else "—",
        "carrera":        est.get("carrera",  "—"),
        "estado_cursada": estado_cursada,

        # Métricas destacadas: texto a mostrar + variante de color (ver helpers arriba).
        "promedio_texto":      str(promedio) if promedio is not None else "Sin notas",
        "promedio_variante":   _variante_promedio(promedio),
        "asistencia_texto":    f"{porcentaje}%" if porcentaje is not None else "Sin datos",
        "asistencia_variante": _variante_asistencia(porcentaje),

        "curso": {
            "id":           curso_id,
            "nombre":       curso.get("nombre",       "—"),
            "carrera":      curso.get("carrera",      "—"),
            "modalidad":    curso.get("modalidad",    "—"),
            "anio":         curso.get("anio",         "—"),
            "cuatrimestre": curso.get("cuatrimestre", "—"),
        },
        "evaluaciones": evaluaciones_con_nota,

        "tiene_asistencia": bool(total_clases),
        "asistencia_resumen": {
            "presentes":    asis.get("presentes",    0),
            "ausentes":     asis.get("ausentes",     0),
            "justificadas": asis.get("justificadas", 0),
            "tarde":        asis.get("tarde",        0),
            "total_clases": total_clases,
        },
        "asistencia_detalle": asis.get("detalle", []),
    }
    return True, ficha
