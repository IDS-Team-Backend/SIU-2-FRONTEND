from datetime import date, datetime, timezone

# Formato en el que el backend serializa las fechas (RFC 1123).
FORMATO_BACKEND = "%a, %d %b %Y %H:%M:%S %Z"

# Formatos que puede enviar el navegador (<input type="datetime-local"> no incluye segundos).
FORMATOS_ENTRADA = (
    FORMATO_BACKEND,
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
)


def parsear_fecha_hora(valor):
    """Convierte strings del backend (RFC 1123) o del formulario a datetime."""
    if not valor:
        return None

    if isinstance(valor, datetime):
        return valor

    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())

    texto = str(valor).strip()
    for formato in FORMATOS_ENTRADA:
        try:
            return datetime.strptime(texto, formato)
        except (ValueError, TypeError):
            continue
    return None


def fecha_a_date(valor):
    """Extrae un objeto date puro de un valor fecha/hora."""
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor

    dt = parsear_fecha_hora(valor)
    return dt.date() if dt else None


def fecha_hora_api(fecha_str: str) -> str:
    """
    Convierte el datetime recibido del formulario HTML (datetime-local)
    al formato ISO 8601: '2026-07-02T15:00:00'
    """
    if not fecha_str:
        return ""
    
    # datetime-local puede venir como '2026-07-02T15:00' o '2026-07-02T15:00:00'
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(fecha_str, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    
    raise ValueError(f"Formato de fecha no reconocido: {fecha_str}")


def _transformar_formato(fecha_str, formato_destino):
    """Helper privado para unificar el comportamiento y eliminar redundancia."""
    dt = parsear_fecha_hora(fecha_str)
    if dt:
        return dt.strftime(formato_destino)
    return fecha_str if fecha_str else ""


# =====================================================================
# FILTROS DE JINJA
# =====================================================================

def formatear_fecha(fecha_str):
    """RFC 1123 -> dd/mm/aaaa (para mostrar en tablas y textos)."""
    return _transformar_formato(fecha_str, "%d/%m/%Y")


def fecha_input(fecha_str):
    """RFC 1123 -> aaaa-mm-dd (para <input type=date>)."""
    return _transformar_formato(fecha_str, "%Y-%m-%d")


def formatear_fecha_hora(fecha_str):
    """RFC 1123 -> dd/mm/aaaa hh:mm (para mostrar fechas con hora)."""
    return _transformar_formato(fecha_str, "%d/%m/%Y %H:%M")


def fecha_input_datetime(fecha_str):
    """RFC 1123 -> aaaa-mm-ddThh:mm (para <input type=datetime-local>)."""
    return _transformar_formato(fecha_str, "%Y-%m-%dT%H:%M")


def registrar_filtros_fecha(app):
    """Registra los filtros de fecha en el entorno Jinja de la app Flask."""
    app.add_template_filter(formatear_fecha, "formatear_fecha")
    app.add_template_filter(fecha_input, "fecha_input")
    app.add_template_filter(fecha_input_datetime, "fecha_input_datetime")
    app.add_template_filter(formatear_fecha_hora, "formatear_fecha_hora")