from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.decorators import login_required
from services import password_service

password_bp = Blueprint("password", __name__)


@password_bp.route("/recuperar", methods=["GET", "POST"])
def solicitar_reset():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password_service.solicitar_reset(email)
        flash("Si tu email está registrado, recibirás un enlace en los próximos minutos.", "success")
        return redirect(url_for("auth.login"))   # ← redirect, no render_template

    return render_template("public/password/recuperar_password.html",
                           title="Recuperar contraseña")


@password_bp.route("/recuperar/confirmar", methods=["GET", "POST"])
def confirmar_reset():
    token = request.args.get("token", "").strip() or request.form.get("token", "").strip()

    if not token:
        flash("Enlace inválido. Solicitá uno nuevo.", "danger")
        return redirect(url_for("password.solicitar_reset"))   # ← nombre correcto

    if request.method == "POST":
        nueva     = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")

        ok, mensaje = password_service.confirmar_reset(token, nueva, confirmar)
        if ok:
            flash("Contraseña actualizada correctamente. Ya podés iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(mensaje, "danger")

    return render_template("admin/password/nueva_password.html",
                           title="Nueva contraseña",
                           token=token)


@password_bp.route("/perfil/cambiar-contrasena", methods=["GET", "POST"])
@login_required
def cambiar():
    if request.method == "POST":
        actual    = request.form.get("password_actual", "")
        nueva     = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")

        ok, mensaje = password_service.cambiar_contraseña(actual, nueva, confirmar)
        if ok:
            flash(mensaje, "success")
            return redirect(url_for("perfil.index"))
        else:
            flash(mensaje, "danger")

    return render_template("admin/password/cambiar_password.html",
                           title="Cambiar contraseña")
