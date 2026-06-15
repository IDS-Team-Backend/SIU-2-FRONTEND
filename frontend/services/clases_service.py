import calendar
import json
import re
from datetime import date, timedelta

from utils import api_client as api
from utils.filtros_fecha import (
    fecha_a_date,
    fecha_hora_api,
    fecha_input_datetime,
    parsear_fecha_hora,
)

MESES_ES = [
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

ESTADOS_CLASE_DEFAULT = ["pendiente", "suspendida", "en curso", "finalizada"]
TIPOS_CLASE = ["teorica", "practica"]
MODALIDADES_CLASE = ["Virtual", "Presencial"]


def _extraer_lista(data, posibles_claves):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for clave in posibles_claves:
        valor = data.get(clave)
        if isinstance(valor, list):
            return valor

    return []


def _limpiar_campos_clase(**campos):
    payload = {}

    for clave, valor in campos.items():
        if valor is None:
            continue

        texto = str(valor).strip() if isinstance(valor, str) else valor
        if texto == "":
            continue

        payload[clave] = texto

    return payload


def _normalizar_tags(tags):
    if tags is None:
        return None

    if isinstance(tags, list):
        return [str(tag).strip() for tag in tags if str(tag).strip()]

    if isinstance(tags, str):
        texto = tags.strip()
        if not texto:
            return []

        try:
            data = json.loads(texto)
        except json.JSONDecodeError:
            data = None

        if isinstance(data, list):
            return [str(tag).strip() for tag in data if str(tag).strip()]

        return [parte.strip() for parte in re.split(r"[;,\n]", texto) if parte.strip()]

    return tags


def normalizar_clase(clase, indice=0):
    if not isinstance(clase, dict):
        return {
            "id": None,
            "nombre": "Clase",
            "fecha_hora_inicio": None,
            "fecha_hora_fin": None,
            "status": "",
            "tema": "",
            "tipo": "",
            "modalidad": "",
            "tags": [],
            "color_index": indice % 6,
        }

    fecha_inicio = (
        clase.get("fecha_hora_inicio")
        or clase.get("fecha_inicio")
        or clase.get("inicio")
        or clase.get("fecha")
    )
    fecha_fin = clase.get("fecha_hora_fin") or clase.get("fecha_fin") or clase.get("fin")

    tags = _normalizar_tags(clase.get("tags") or [])
    if tags is None:
        tags = []

    nombre = (
        clase.get("nombre")
        or clase.get("titulo")
        or clase.get("tema")
        or f"Clase {clase.get('id', '')}".strip()
        or "Clase"
    )
    status = (clase.get("status") or clase.get("estado") or clase.get("estado_clase") or "").strip()

    return {
        **clase,
        "nombre": nombre,
        "titulo": nombre,
        "tema": clase.get("tema") or clase.get("descripcion") or "",
        "tipo": (clase.get("tipo") or "").strip(),
        "modalidad": (clase.get("modalidad") or "").strip(),
        "tags": tags,
        "fecha_hora_inicio": fecha_inicio,
        "fecha_hora_fin": fecha_fin,
        "fecha_date": fecha_a_date(fecha_inicio),
        "status": status,
        "estado": status,
        "descripcion": clase.get("tema") or clase.get("descripcion") or clase.get("observaciones") or "",
        "color_index": indice % 6,
    }


def agrupar_clases_por_dia(clases):
    clases_por_dia = {}
    for indice, clase in enumerate(clases):
        normalizada = normalizar_clase(clase, indice)
        dia = normalizada.get("fecha_date")
        if dia is not None:
            clases_por_dia.setdefault(dia, []).append(normalizada) # agrega la clase y sino existe el dia lo crea con []
    return clases_por_dia


def navegacion_calendario(anio, mes, hoy=None):
    hoy = hoy or date.today()

    try:
        anio = int(anio)
        mes = int(mes)
    except (TypeError, ValueError):
        anio, mes = hoy.year, hoy.month

    if not (1 <= mes <= 12):
        anio, mes = hoy.year, hoy.month

    semanas = calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes)
    prev_anio, prev_mes = (anio - 1, 12) if mes == 1 else (anio, mes - 1)
    next_anio, next_mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)

    return {
        "semanas": semanas,
        "anio": anio,
        "mes": mes,
        "nombre_mes": MESES_ES[mes],
        "prev_anio": prev_anio,
        "prev_mes": prev_mes,
        "next_anio": next_anio,
        "next_mes": next_mes,
        "hoy": hoy,
    }


def calcular_prefill_nueva_clase(fecha_prefill):
    if fecha_prefill and len(fecha_prefill) == 10:
        fecha_inicio_texto = f"{fecha_prefill}T08:00"
    else:
        fecha_inicio_texto = fecha_prefill or ""

    fecha_base = parsear_fecha_hora(fecha_inicio_texto)
    if fecha_base is None:
        return fecha_inicio_texto or None, None

    return (
        fecha_input_datetime(fecha_base),
        fecha_input_datetime(fecha_base + timedelta(hours=1)),
    )


def params_mes_desde_fecha(fecha_texto):
    fecha = parsear_fecha_hora(fecha_texto)
    if fecha is None:
        return {}
    return {"anio": fecha.year, "mes": fecha.month}


def extraer_id_clase_creada(respuesta):
    if not isinstance(respuesta, dict):
        return None

    if respuesta.get("id"):
        return respuesta["id"]

    clase = respuesta.get("clase")
    if isinstance(clase, dict):
        return clase.get("id")

    return None


def obtener_clases_del_curso(curso_id):
    ok, data = api.get("/clases", params={"curso_id": curso_id})

    if not ok:
        error_msg = data.get("error", "Error al obtener clases.") if data else "Error de conexión."
        return False, error_msg

    clases = _extraer_lista(data, ["clases", "resultados", "items", "data"])
    return True, clases


def obtener_clase_por_id(clase_id):
    if not clase_id:
        return False, "Falta el ID de la clase."

    ok, data = api.get(f"/clases/{clase_id}")

    if not ok:
        error_msg = data.get("error", "Error al obtener la clase.") if data else "Error de conexión."
        return False, error_msg

    if isinstance(data, dict):
        clase = data.get("clase") or data.get("resultado") or data
        return True, normalizar_clase(clase)

    return True, normalizar_clase(data)


def obtener_estados_clase():
    ok, data = api.get("/clases/estados")

    if not ok:
        error_msg = data.get("error", "Error al obtener estados de clase.") if data else "Error de conexión."
        return False, error_msg

    estados = _extraer_lista(data, ["estados", "resultados", "items", "data"])
    return True, estados


def crear_clase(
    curso_id,
    profesor_id,
    nombre,
    fecha_hora_inicio,
    fecha_hora_fin,
    tema=None,
    tipo=None,
    modalidad=None,
    tags=None,
    status=None,
):
    if not curso_id:
        return False, "Falta el ID del curso."

    if not profesor_id:
        return False, "Falta el ID del profesor."

    if not nombre or not str(nombre).strip():
        return False, "El nombre de la clase es obligatorio."

    if not fecha_hora_inicio:
        return False, "La fecha y hora de inicio son obligatorias."

    if not fecha_hora_fin:
        return False, "La fecha y hora de fin son obligatorias."

    payload = _limpiar_campos_clase(
        curso_id=int(curso_id),
        profesor_id=int(profesor_id),
        nombre=nombre,
        fecha_hora_inicio=fecha_hora_api(fecha_hora_inicio),
        fecha_hora_fin=fecha_hora_api(fecha_hora_fin),
        tema=tema,
        tipo=tipo,
        modalidad=modalidad,
        status=status,
    )

    tags_normalizados = _normalizar_tags(tags)
    if tags_normalizados is not None:
        payload["tags"] = tags_normalizados

    ok, data = api.post("/clases", json=payload)

    if not ok:
        error_msg = data.get("error", "Error al crear la clase.") if data else "Error de conexión."
        return False, error_msg

    return True, data


def actualizar_clase(
    clase_id,
    nombre=None,
    fecha_hora_inicio=None,
    fecha_hora_fin=None,
    tema=None,
    tipo=None,
    modalidad=None,
    tags=None,
    status=None,
    metodo="PATCH",
):
    if not clase_id:
        return False, "Falta el ID de la clase."

    payload = _limpiar_campos_clase(
        nombre=nombre,
        fecha_hora_inicio=fecha_hora_api(fecha_hora_inicio),
        fecha_hora_fin=fecha_hora_api(fecha_hora_fin),
        tema=tema,
        tipo=tipo,
        modalidad=modalidad,
        status=status,
    )

    tags_normalizados = _normalizar_tags(tags)
    if tags_normalizados is not None:
        payload["tags"] = tags_normalizados

    if not payload:
        return False, "No hay cambios para guardar."

    if metodo == "PUT":
        ok, data = api.put(f"/clases/{clase_id}", json=payload)
    else:
        ok, data = api.patch(f"/clases/{clase_id}", json=payload)

    if not ok:
        error_msg = data.get("error", "Error al actualizar la clase.") if data else "Error de conexión."
        return False, error_msg

    return True, data


def eliminar_clase(clase_id):
    if not clase_id:
        return False, "Falta el ID de la clase."

    ok, data = api.delete(f"/clases/{clase_id}")

    if not ok:
        error_msg = data.get("error", "Error al eliminar la clase.") if data else "Error de conexión."
        return False, error_msg

    return True, None
