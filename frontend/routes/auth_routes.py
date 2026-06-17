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
from services.cursos_service import obtener_curso_activo_id
from utils import api_client as api

auth_bp = Blueprint("auth", __name__)

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



@auth_bp.route("/finalizar-registracion", methods=["GET", "POST"])
def finalizar_registracion():
    email = (request.values.get("email") or "").strip()

    if request.method == "POST":
        ok, data = api.post(
            "/auth/finalizar-registro",
            json={
                "email":              email,
                "codigo":             (request.form.get("codigo") or "").strip(),
                "nueva_password":     request.form.get("nueva_password") or "",
                "confirmar_password": request.form.get("confirmar_password") or "",
            },
            auth=False,
        )

        if ok:
            flash("Registración finalizada. Ya podés iniciar sesión.", "success")
            return redirect(url_for("public.index"))

        error = data.get("error", "No se pudo finalizar la registración.") if isinstance(data, dict) else "Error inesperado."
        return render_template("auth/finalizar_registracion.html", email=email, error=error)

    return render_template("auth/finalizar_registracion.html", email=email)


@auth_bp.route("/post-login")
@login_required
def post_login():
    perfiles = UserContext.get_perfiles()

    ok = UserContext.guardar_usuario_actual_en_sesion()  # carga datos del usuario en la sesión para que estén disponibles en el contexto global (g.usuario y g.perfiles)
    if not ok:
        flash("Error al cargar los datos del usuario en la sesion.", "danger")
        return redirect(url_for("auth.login"))

    #remplazar a futuro con obtener_destino_por_perfil(perfiles) cuando se tenga perfiles
    #POR AHORA ESTA HARDCODEADO PARA REDIRIGIR AL CURSO ACTIVO, YA QUE NO HAY PERFILES NI ASIGNACIÓN DE PERFILES A USUARIOS EN EL BACKEND

    # destino = ("curso", curso_id = CURSO_ACTIVO["id"])  
    #   if not destino:
    #       flash("Tu usuario no tiene un perfil asignado.", "warning")
    #       return redirect(url_for("auth.login"))
    # return redirect(url_for(destino))

    return redirect(url_for("private.curso", curso_id=obtener_curso_activo_id()))

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    response = redirect(url_for("auth.login"))
    borrar_token_cookie(response)
    flash("Sesión cerrada correctamente.", "success")
    return response