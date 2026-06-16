"""Configuración derivada del entorno, en un solo lugar.

CURSO_ACTIVO_ID: id de la única cursada activa del sistema (ver regla de negocio
"una sola cursada activa por vez"). Antes estaba duplicado en public_routes.py y
private_routes.py.
"""
import os

CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))
