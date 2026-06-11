from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

import utils.user_context as UserContext
from services.auth_service import (
    validar_formulario_login,
    login_backend,
    guardar_token_en_cookie,
    borrar_token_cookie,
    usuario_esta_logueado,
    obtener_destino_por_perfil,
)
from services.decorators import login_required

auth_bp = Blueprint("auth", __name__)

CURSO_ACTIVO_ID = 1

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if usuario_esta_logueado():
        return redirect(url_for("auth.post_login"))

    if request.method == "POST":
        errores, dni, password = validar_formulario_login(request.form)

        if errores:
            for error in errores:
                flash(error, "danger")

            return render_template(
                "auth/login.html",
                dni=request.form.get("dni") or request.form.get("username", "")
            )

        ok, resultado = login_backend(dni, password)

        if not ok:
            return render_template(
            "auth/login.html",
            error=resultado,
                dni=request.form.get("dni") or request.form.get("username", "")
            )

        token = resultado

        response = redirect(url_for("auth.post_login"))
        guardar_token_en_cookie(response, token)

        flash("Sesión iniciada correctamente.", "success")
        return response

    return render_template("auth/login.html")



@auth_bp.route("/post-login")
@login_required
def post_login():
    perfiles = UserContext.get_perfiles()

    #remplazar a futuro con obtener_destino_por_perfil(perfiles) cuando se tenga perfiles
    #POR AHORA ESTA HARDCODEADO PARA REDIRIGIR AL CURSO ACTIVO, YA QUE NO HAY PERFILES NI ASIGNACIÓN DE PERFILES A USUARIOS EN EL BACKEND

    # destino = ("curso", curso_id = CURSO_ACTIVO["id"])  
    #   if not destino:
    #       flash("Tu usuario no tiene un perfil asignado.", "warning")
    #       return redirect(url_for("auth.login"))
    # return redirect(url_for(destino))

    return redirect(url_for("private.curso", curso_id=CURSO_ACTIVO_ID))

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    response = redirect(url_for("auth.login"))
    borrar_token_cookie(response)
    flash("Sesión cerrada correctamente.", "success")
    return response