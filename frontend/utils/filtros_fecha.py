from datetime import datetime

# Formato en el que el backend serializa las fechas (RFC 1123).
FORMATO_BACKEND = "%a, %d %b %Y %H:%M:%S %Z"


def formatear_fecha(fecha_str):
    """RFC 1123 -> dd/mm/aaaa (para mostrar)."""
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, FORMATO_BACKEND).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return fecha_str


def fecha_input(fecha_str):
    """RFC 1123 -> aaaa-mm-dd (para <input type=date>)."""
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, FORMATO_BACKEND).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return fecha_str


def formatear_fecha_hora(fecha_str):
    """RFC 1123 -> dd/mm/aaaa hh:mm (para mostrar fechas con hora)."""
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, FORMATO_BACKEND).strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return fecha_str


def fecha_input_datetime(fecha_str):
    """RFC 1123 -> aaaa-mm-ddThh:mm (para <input type=datetime-local>)."""
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, FORMATO_BACKEND).strftime("%Y-%m-%dT%H:%M")
    except (ValueError, TypeError):
        return fecha_str


def registrar_filtros_fecha(app):
    """Registra los filtros de fecha en el entorno Jinja de la app."""
    app.add_template_filter(formatear_fecha, "formatear_fecha")
    app.add_template_filter(fecha_input, "fecha_input")
    app.add_template_filter(formatear_fecha_hora, "formatear_fecha_hora")
    app.add_template_filter(fecha_input_datetime, "fecha_input_datetime")
