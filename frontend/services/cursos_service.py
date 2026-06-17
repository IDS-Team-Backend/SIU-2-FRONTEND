from utils import api_client as api

ROL_LABELS = {"titular": "Titular", "jefe_tp": "Jefe de TP", "ayudante": "Ayudante"}

ESTADO_LABELS = {
    "abierta": "Inscripción abierta",
    "inscripcion_cerrada": "Inscripción cerrada",
    "periodo_evaluativo": "Periodo evaluativo",
    "finalizada": "Cursada finalizada",
}

# Ciclo de vida de la cursada: para cada estado, a qué estado se AVANZA y a cuál se
# RETROCEDE, con el texto del botón. (destino, etiqueta, confirmación).
# Avanzar siempre se puede; retroceder solo si la cursada está activa.
_AVANCE = {
    "abierta":             ("inscripcion_cerrada", "Cerrar inscripciones", "¿Cerrar las inscripciones de la cursada?"),
    "inscripcion_cerrada": ("periodo_evaluativo",  "Iniciar periodo evaluativo", "¿Iniciar el periodo evaluativo?"),
    "periodo_evaluativo":  ("finalizada",          "Cerrar periodo evaluativo y finalizar", "¿Finalizar la cursada?"),
}
_RETROCESO = {
    "inscripcion_cerrada": ("abierta",             "Reabrir inscripciones", "¿Reabrir las inscripciones?"),
    "periodo_evaluativo":  ("inscripcion_cerrada", "Volver a cursada", "¿Volver al estado anterior?"),
    "finalizada":          ("periodo_evaluativo",  "Reabrir periodo evaluativo", "¿Reabrir el periodo evaluativo?"),
}


def transiciones_disponibles(curso):
    """Botones de cambio de estado para la pantalla de gestión.
    Avanzar siempre se puede; retroceder solo si la cursada está activa."""
    estado, activa = curso.get("estado"), curso.get("activa")
    botones = []
    if activa and estado in _RETROCESO:
        destino, etiqueta, confirmacion = _RETROCESO[estado]
        botones.append({"destino": destino, "etiqueta": etiqueta, "confirmacion": confirmacion, "clase": "btn btn-outline"})
    if estado in _AVANCE:
        destino, etiqueta, confirmacion = _AVANCE[estado]
        botones.append({"destino": destino, "etiqueta": etiqueta, "confirmacion": confirmacion, "clase": "btn btn-primary"})
    return botones


def _normalizar_curso(data):
    """Mapea la respuesta enriquecida del backend al shape que esperan los templates."""
    equipo = data.get("equipo_docente", []) or []
    return {
        "id":              data.get("id"),
        "materia_id":      data.get("materia_id"),
        "materia_nombre":  data.get("materia_nombre"),
        "codigo":          data.get("codigo") or "",
        "nombre":          data.get("nombre") or "",
        "descripcion":     data.get("descripcion") or "",
        "carrera":         data.get("carrera") or "",
        "modalidad":       data.get("modalidad") or "",
        "anio":            data.get("anio"),
        "cuatrimestre":    data.get("cuatrimestre"),
        "horas_semanales": data.get("horas_semanales"),
        "estado":          data.get("estado") or "abierta",
        "estado_label":    ESTADO_LABELS.get(data.get("estado"), data.get("estado") or "—"),
        "activa":          bool(data.get("activa")),
        "profesores": [
            {
                "nombre": f"{d.get('nombre', '')} {d.get('apellido', '')}".strip(),
                "rol":    ROL_LABELS.get(d.get("rol"), d.get("rol")),
            }
            for d in equipo
        ],
        "stats": data.get("stats", {"alumnos": 0, "materiales": 0, "evaluaciones": 0}),
    }


def obtener_curso_para_vista(curso_id):
    """(ok, curso_dict) con el shape que esperan los templates de curso (admin y público).
    Lee del endpoint público enriquecido (no requiere login)."""
    ok, data = api.get(f"/cursos-publico/{curso_id}", auth=False)
    if not ok or not data:
        msg = data.get("error", "No se pudo obtener el curso.") if isinstance(data, dict) else "No se pudo obtener el curso."
        return False, msg
    return True, _normalizar_curso(data)


def obtener_curso_activo():
    """(ok, curso_dict) de la cursada activa del sistema (endpoint público, sin login)."""
    ok, data = api.get("/cursos-publico/activa", auth=False)
    if not ok or not data:
        return False, "No se pudo obtener la cursada activa."
    return True, _normalizar_curso(data)


def obtener_curso_activo_id():
    """Id de la cursada activa, con fallback a 1 si no se pudo resolver."""
    ok, curso = obtener_curso_activo()
    if ok and curso.get("id"):
        return curso["id"]
    return 1


def obtener_cronograma(curso_id):
    """Lista de semanas del cronograma de un curso (endpoint público, sin login)."""
    ok, data = api.get(f"/cursos-publico/{curso_id}/cronograma", auth=False)
    return data.get("semanas", []) if ok and data else []


def listar_cursadas():
    """Lista de todas las cursadas (para el panel de gestión)."""
    ok, data = api.get("/cursos/", params={"page_size": 100})
    if not ok or not data:
        return []
    return data.get("cursos", [])


def activar_cursada(curso_id):
    ok, data = api.post(f"/cursos/{curso_id}/activar")
    if not ok:
        return False, data.get("error", "Error al activar la cursada.") if data else "Error de conexión."
    return True, data


def crear_siguiente_cursada():
    """(ok, data|error). data trae {message, curso} con la cursada nueva."""
    ok, data = api.post("/cursos/siguiente")
    if not ok:
        return False, data.get("error", "Error al crear la siguiente cursada.") if data else "Error de conexión."
    return True, data


def actualizar_curso(curso_id, datos):
    ok, data = api.put(f"/cursos/{curso_id}", json=datos)
    if not ok:
        return False, data.get("error", "Error al actualizar el curso.") if data else "Error de conexión."
    return True, data


def cambiar_estado_curso(curso_id, nuevo_estado):
    ok, data = api.patch(f"/cursos/{curso_id}/estado",
                           json={"estado": nuevo_estado})
    if not ok:
        return False, data.get("error", "Error al cambiar el estado.") if data else "Error de conexión."
    return True, data


def obtener_materias():
    ok, data = api.get("/materias/", params={"page_size": 100})
    if not ok or not data:
        return []
    return data.get("materias", [])
