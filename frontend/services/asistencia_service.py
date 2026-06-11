from utils.api_client import api_request

ESTADOS_ASISTENCIA = ["presente", "ausente", "justificada", "tarde"]


def _extraer_planilla(data):
    if not data:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for clave in ("asistencias", "planilla", "resultados", "items", "data"):
            valor = data.get(clave)
            if isinstance(valor, list):
                return valor
            if isinstance(valor, dict):
                anidada = _extraer_planilla(valor)
                if anidada:
                    return anidada

    return []


def normalizar_item_asistencia(item):
    if not isinstance(item, dict):
        return item

    alumno = item.get("alumno") if isinstance(item.get("alumno"), dict) else {}
    alumno_id = item.get("alumno_id") or alumno.get("id")

    return {
        **item,
        "alumno_id": alumno_id,
        "apellido": item.get("apellido") or alumno.get("apellido") or item.get("alumno_apellido") or "",
        "nombre": item.get("nombre") or alumno.get("nombre") or item.get("alumno_nombre") or "",
        "padron": item.get("padron") or alumno.get("padron") or item.get("legajo") or "",
        "estado": (item.get("estado") or "").strip(),
        "observaciones": item.get("observaciones") or item.get("nota") or "",
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

        alumno_id = clave.replace("estado_", "")
        if not alumno_id:
            continue

        asistencias.append({"alumno_id": int(alumno_id), "estado": valor})

    return asistencias


def obtener_asistencia_clase(clase_id):
    if not clase_id:
        return False, "Falta el ID de la clase."

    ok, data = api_request("GET", f"/asistencia/clases/{clase_id}")

    if not ok:
        error_msg = data.get("error", "Error al obtener asistencia.") if data else "Error de conexión."
        return False, error_msg

    planilla = [normalizar_item_asistencia(item) for item in _extraer_planilla(data)]
    resumen = {}
    if isinstance(data, dict):
        resumen = data.get("resumen") or data.get("estadisticas") or {}

    if not resumen and planilla:
        resumen = calcular_resumen_asistencia(planilla)

    return True, {"planilla": planilla, "resumen": resumen}


def generar_qrs_clase(clase_id):
    if not clase_id:
        return False, "Falta el ID de la clase."

    ok, data = api_request("POST", f"/asistencia/clases/{clase_id}/generar-qrs")

    if not ok:
        error_msg = data.get("error", "Error al generar QRs.") if data else "Error de conexión."
        return False, error_msg

    return True, data


def actualizar_planilla_asistencia(clase_id, asistencias):
    if not clase_id:
        return False, "Falta el ID de la clase."

    if asistencias is None:
        return False, "No hay datos de asistencia para actualizar."

    ok, data = api_request(
        "PUT",
        f"/asistencia/clases/{clase_id}",
        json_body={"asistencias": asistencias},
    )

    if not ok:
        error_msg = data.get("error", "Error al actualizar asistencia.") if data else "Error de conexión."
        return False, error_msg

    return True, data
