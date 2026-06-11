from datetime import date, datetime

# Formato en el que el backend serializa las fechas (RFC 1123).
FORMATO_BACKEND = "%a, %d %b %Y %H:%M:%S %Z"


def parsear_fecha_hora(valor):
    """Convierte strings del backend (RFC 1123) o instancias de fecha a datetime."""
    if not valor:
        return None

    if isinstance(valor, datetime):
        return valor

    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())

    try:
        return datetime.strptime(str(valor).strip(), FORMATO_BACKEND)
    except (ValueError, TypeError):
        return None


def fecha_a_date(valor):
    """Extrae un objeto date puro de un valor fecha/hora."""
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor

    dt = parsear_fecha_hora(valor)
    return dt.date() if dt else None


def fecha_hora_api(valor):
    """Normaliza fecha/hora a string estándar para enviar a la API."""
    dt = parsear_fecha_hora(valor)
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    texto = str(valor).strip() if valor else ""
    return texto or None


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