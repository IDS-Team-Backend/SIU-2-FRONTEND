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


def obtener_profesor(profesor_id):
    """Retorna (ok, profesor) por id."""
    ok, data = api.get(f"/profesores/{profesor_id}")
    if not ok:
        if data and data.get("status_code") == 404:
            return False, "No se encontró el profesor."
        return False, data.get("error", "Error al obtener el profesor.") if data else "Error de conexión."
    return True, data


def editar_profesor(profesor_id, usuario_id, datos):
    """Edita datos personales (PUT /usuarios) y de perfil (PATCH /profesores).
    datos: nombre, apellido, email, dni, legajo, titulo, departamento, fecha_ingreso.
    Retorna (ok, error)."""
    errores = []

    # Campos numéricos: form.get(type=int) los deja en None si no son numéricos,
    # así que los validamos explícitamente antes de escribir nada (evita updates parciales).
    try:
        dni_int = int(str(datos.get("dni")).strip())
    except (ValueError, TypeError):
        return False, "El DNI debe ser un número."

    try:
        legajo_int = int(str(datos.get("legajo")).strip())
    except (ValueError, TypeError):
        return False, "El legajo debe ser un número."

    # Datos personales → PUT /usuarios/{id} (igual que editar_alumno: sin password).
    if usuario_id:
        ok_u, data_u = api.put(f"/usuarios/{usuario_id}", json={
            "nombre":   datos["nombre"],
            "apellido": datos["apellido"],
            "email":    datos["email"],
            "dni":      dni_int,
        })
        if not ok_u:
            errores.append(data_u.get("error", "Error al actualizar datos personales.") if data_u
                           else "Error de conexión al actualizar usuario.")
    else:
        errores.append("No se pudo identificar el usuario — datos personales no actualizados.")

    # Datos de perfil → PATCH /profesores/{id} (legajo, titulo, departamento, fecha_ingreso).
    prof_body = {"legajo": legajo_int}
    if datos.get("titulo"):
        prof_body["titulo"] = datos["titulo"]
    if datos.get("departamento"):
        prof_body["departamento"] = datos["departamento"]
    if datos.get("fecha_ingreso"):
        prof_body["fecha_ingreso"] = datos["fecha_ingreso"]

    ok_p, data_p = api.patch(f"/profesores/{profesor_id}", json=prof_body)
    if not ok_p:
        errores.append(data_p.get("error", "Error al actualizar datos del profesor.") if data_p
                       else "Error de conexión al actualizar profesor.")

    if errores:
        return False, " | ".join(errores)
    return True, None


def eliminar_profesor(profesor_id):
    """Soft delete del profesor (DELETE /profesores/{id}). Retorna (ok, error)."""
    ok, data = api.delete(f"/profesores/{profesor_id}")
    if not ok:
        if data and data.get("status_code") == 404:
            return False, "El profesor no existe o ya fue eliminado."
        return False, data.get("error", "Error al eliminar el profesor.") if data else "Error de conexión."
    return True, None


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
