from utils import api_client as api


def obtener_profesores(page=1, page_size=20):
    """Retorna (ok, profesores, paginacion)."""
    ok, data = api.get("/profesores/", params={"page": page, "page_size": page_size})
    if not ok:
        return False, data.get("error", "Error al obtener profesores.") if data else "Error de conexión.", {}

    # 204 → data es None (no hay profesores)
    if not data:
        return True, [], {"page": 1, "page_size": page_size, "total": 0, "total_paginas": 1}

    paginacion = {
        "page":          data.get("page", 1),
        "page_size":     data.get("page_size", page_size),
        "total":         data.get("total", 0),
        "total_paginas": data.get("total_paginas", 1),
    }
    return True, data.get("profesores", []), paginacion


def obtener_participaciones(docente_ids):
    """Retorna dict {docente_id: [participaciones]} en una sola llamada (evita N+1).
    Cada participación: {curso_id, curso_nombre, anio, cuatrimestre, rol, activa}."""
    ids = [str(i) for i in docente_ids if i]
    if not ids:
        return {}

    ok, data = api.get("/curso_docentes/participaciones",
        params={"docente_ids": ",".join(ids)},
    )
    if not ok or not data:
        return {}

    agrupado = {}
    for p in data.get("participaciones", []):
        agrupado.setdefault(p["docente_id"], []).append(p)
    return agrupado


def registrar_profesor(datos):
    """datos: nombre, apellido, email, dni, legajo, titulo, departamento, fecha_ingreso."""
    ok, data = api.post("/profesores/registro", json=datos)
    if not ok:
        return False, data.get("error", "Error al crear el profesor.") if data else "Error de conexión."
    return True, data


def buscar_profesor_por_legajo(legajo):
    legajo = str(legajo).strip()

    if not legajo:
        return False, "Ingresá un legajo."
    if not legajo.isdigit():
        return False, "El legajo debe contener solo números."

    ok, data = api.get(f"/profesores/legajo/{legajo}")
    if not ok:
        if data and data.get("status_code") == 404:
            return False, f"No se encontró ningún profesor con legajo {legajo}."
        return False, data.get("error", "Error al buscar profesor.") if data else "Error de conexión."

    return True, data
