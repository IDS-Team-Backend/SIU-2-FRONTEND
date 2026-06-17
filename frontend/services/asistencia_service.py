from utils import api_client as api

ESTADOS_ASISTENCIA = ["presente", "ausente", "justificada", "tarde"]


def normalizar_item_asistencia(item):
    return {
        "alumno_id": item.get("alumno_id"),
        "nombre": item.get("nombre", ""),
        "apellido": item.get("apellido", ""),
        "padron": item.get("padron", ""),
        "estado": (item.get("estado") or "").strip(),
        "fecha_registro": item.get("fecha_registro"),
    }


def calcular_resumen_asistencia(planilla):
    presentes = sum(1 for item in planilla if str(item.get("estado", "")).lower() == "presente")
    ausentes = sum(1 for item in planilla if str(item.get("estado", "")).lower() == "ausente")
    justificadas = sum(1 for item in planilla if str(item.get("estado", "")).lower() == "justificada")
    tardanzas = sum(1 for item in planilla if str(item.get("estado", "")).lower() == "tarde")
    total = len(planilla)

    return {
        "total": total,
        "presentes": presentes,
        "ausentes": ausentes,
        "justificadas": justificadas,
        "tarde": tardanzas,
        "porcentaje_presentes": round((presentes / total) * 100, 2) if total else 0,
    }


def parsear_asistencias_form(form_items):
    asistencias = []
    for clave, valor in form_items:
        if not clave.startswith("estado_"):
            continue
        alumno_id = clave.removeprefix("estado_")
        if alumno_id:
            asistencias.append({"alumno_id": int(alumno_id), "estado": valor})
    return asistencias


def obtener_asistencia_clase(clase_id):
    ok, data = api.get(f"/asistencia/clases/{clase_id}")
    if not ok:
        return False, data.get("error", "Error al obtener asistencia.") if data else "Error de conexión."

    planilla = [normalizar_item_asistencia(item) for item in data.get("asistencias", [])]
    resumen = calcular_resumen_asistencia(planilla)
    return True, {"planilla": planilla, "resumen": resumen}


def actualizar_planilla_asistencia(clase_id, asistencias):
    ok, data = api.put(
        f"/asistencia/clases/{clase_id}",
        json={"asistencias": asistencias},
    )
    if not ok:
        return False, data.get("error", "Error al actualizar asistencia.") if data else "Error de conexión."
    return True, data

def escanear_qr(token, clase_id):
    ok, data = api.post("/asistencia/escanear", json={"token": token, "clase_id": clase_id})
    if not ok:
        return False, data.get("error", "Error al escanear.") if data else "Error de conexión."
    return True, data.get("asistencia")


# //////////////////////////////////////////////
# /////////// ALUMNOS - ASISTENCIA /////////////
# //////////////////////////////////////////////

def obtener_mis_asistencias(curso_id):
    ok, data = api.get(f"/asistencia/cursos/{curso_id}/me")
    if not ok:
        return False, data.get("error", "Error al obtener asistencias.") if data else "Error de conexión."
    return True, data.get("asistencias", {})


def obtener_mi_qr():
    ok, data = api.get(f"/asistencia/mi-qr")
    if not ok:
        return False, data.get("error", "Error al obtener el QR.") if data else "Error de conexión."
    return True, data.get("token_qr")