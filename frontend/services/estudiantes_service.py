from utils import api_client as api


def obtener_estudiantes(page=1, page_size=20, carrera=None, anio_ingreso=None, q=None):
    """Listado general de estudiantes del sistema.
    Retorna (ok, estudiantes, paginacion). El backend responde 204 (data=None)
    cuando no hay resultados."""
    params = {"page": page, "page_size": page_size}
    if carrera:
        params["carrera"] = carrera
    if anio_ingreso:
        params["anio_ingreso"] = anio_ingreso
    if q:
        params["q"] = q

    ok, data = api.get("/estudiantes/", params=params)
    if not ok:
        return False, data.get("error", "Error al obtener estudiantes.") if data else "Error de conexión.", {}

    data = data or {}  # el backend responde 204 (data=None) cuando no hay resultados
    estudiantes = data.get("estudiantes", [])
    paginacion = {
        "page":          data.get("page",          page),
        "page_size":     data.get("page_size",     page_size),
        "total":         data.get("total",         0),
        "total_paginas": data.get("total_paginas", 1),
    }
    return True, estudiantes, paginacion


def obtener_detalle_estudiante(estudiante_id):
    """Ficha multi-curso (Page B): datos personales + cursos en los que está inscripto.
    Retorna (ok, detalle)."""
    ok, est = api.get(f"/estudiantes/{estudiante_id}")
    if not ok:
        if est and est.get("status_code") == 404:
            return False, "Estudiante no encontrado."
        return False, est.get("error", "Error al obtener el estudiante.") if est else "Error de conexión."

    # Inscripciones del estudiante (todas sus cursadas).
    ok_ec, data_ec = api.get(
        "/estudiante_curso/", params={"estudiante_id": estudiante_id, "page_size": 100}
    )
    inscripciones = (data_ec or {}).get("estudiante_cursos", []) if ok_ec else []

    cursos = [
        {
            "curso_id":          ins.get("curso_id"),
            "curso_nombre":      ins.get("curso_nombre", "—"),
            "estado":            ins.get("estado", "activo"),
            "fecha_inscripcion": ins.get("fecha_inscripcion"),
        }
        for ins in inscripciones
    ]

    detalle = {
        "id":           est.get("id"),
        "nombre":       est.get("nombre",       "—"),
        "apellido":     est.get("apellido",     "—"),
        "email":        est.get("email",        "—"),
        "dni":          est.get("dni",          "—"),
        "padron":       est.get("padron",       "—"),
        "carrera":      est.get("carrera",      "—"),
        "anio_ingreso": est.get("anio_ingreso", "—"),
        "cursos":       cursos,
    }
    return True, detalle
