import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
import utils.user_context as UserContext
from services.decorators import login_required
from services.auth_service import es_staff, es_alumno
from services import perfil_service
 
perfil_bp = Blueprint("perfil", __name__)
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))
POR_PAGINA = 5

@perfil_bp.route("/perfil")
@login_required
def index():
    perfiles = UserContext.get_perfiles()
    if perfiles is None:
        flash("Error al obtener perfiles del usuario.", "danger")
        return redirect(url_for("public.index"))
    if es_alumno(perfiles):
        return redirect(url_for("perfil.perfil_estudiante"))
    elif es_staff(perfiles):
        return redirect(url_for("perfil.perfil_profesor"))
    else:
        flash("No se pudo determinar el perfil del usuario.", "danger")
        return redirect(url_for("public.index"))
    
@perfil_bp.route("/perfil/estudiante")
@login_required
def estudiante():
    ok, perfil = perfil_service.obtener_perfil_estudiante(CURSO_ACTIVO_ID)
    if not ok:
        flash(perfil, "danger")
        return redirect(url_for("private.curso", curso_id=CURSO_ACTIVO_ID))
 
    total_evaluaciones = len(perfil["evaluaciones"])
    pagina_actual      = request.args.get("page", 1, type=int)
    total_paginas      = max(1, -(-total_evaluaciones // POR_PAGINA))  # ceil sin math
 

    pagina_actual = max(1, min(pagina_actual, total_paginas))
 
    inicio = (pagina_actual - 1) * POR_PAGINA
    fin    = inicio + POR_PAGINA
    evaluaciones_pagina = perfil["evaluaciones"][inicio:fin]
 
    return render_template(
        "admin/perfil/estudiante.html",
        title="Mi Perfil",
        active_page="perfil",
        perfil=perfil,
        # Paginación
        evaluaciones_pagina=evaluaciones_pagina,
        pagina_actual=pagina_actual,
        total_paginas=total_paginas,
        total_evaluaciones=total_evaluaciones,
        por_pagina=POR_PAGINA,
    )


@perfil_bp.route("/perfil/profesor")
@login_required
def perfil_profesor():
    ok, perfil = perfil_service.obtener_perfil_profesor(CURSO_ACTIVO_ID)
    if not ok:
        flash(perfil, "danger")
        return redirect(url_for("public.index"))
    return render_template(
        "admin/perfil/profesor.html",
        title="Perfil de Profesor",
        active_page="perfil",
        perfil=perfil,
    )