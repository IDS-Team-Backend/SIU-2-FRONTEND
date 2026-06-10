from utils.api_client import api_request

def solicitar_reset (email):
    if not email or email.strip() == "":
        raise ValueError("El correo electrónico es obligatorio.")
    
    ok, data = api_request(
        "POST", "/password/solicitar",
        json_body={"email": email.strip()},
        auth=False,
    )

    if not ok:
        return False, data.get("error", "Error desconocido al solicitar el reset de contraseña.")
    return True, "Solicitud de reset de contraseña enviada exitosamente. Revisa tu correo electrónico."


def confirmar_reset (token, nueva_contraseña, confirmar_contraseña):
    if not token:
        return False, "El token es obligatorio."
    if not nueva_contraseña:
        return False, "La nueva contraseña es obligatoria."
    if not confirmar_contraseña:
        return False, "La confirmación de la nueva contraseña es obligatoria."
    if nueva_contraseña != confirmar_contraseña:
        return False, "Las contraseñas no coinciden."

    ok, data = api_request(
        "POST", "/password/confirmar",
        json_body={
            "token":              token,
            "nueva_password":     nueva_contraseña,
            "confirmar_password": confirmar_contraseña,
        },
        auth=False,
    )
 
    if not ok:
        return False, data.get("error", "El enlace es inválido o ya expiró.") if data else "Error de conexión."
 
    return True, data.get("message", "Contraseña actualizada.")

def cambiar_contraseña (contraseña_actual, nueva_contraseña, confirmar_contraseña):
    if not contraseña_actual:
        return False, "La contraseña actual es obligatoria."
    if not nueva_contraseña:
        return False, "La nueva contraseña es obligatoria."
    if not confirmar_contraseña:
        return False, "La confirmación de la nueva contraseña es obligatoria."
    if nueva_contraseña != confirmar_contraseña:
        return False, "Las contraseñas no coinciden."
    if nueva_contraseña == contraseña_actual:
        return False, "La nueva contraseña no puede ser igual a la contraseña actual."
    if len(nueva_contraseña) < 8:
        return False, "La nueva contraseña debe tener al menos 8 caracteres."

    ok, data = api_request(
        "POST", "/password/cambiar",
        json_body={
            "password_actual":    contraseña_actual,
            "nueva_password":     nueva_contraseña,
            "confirmar_password": confirmar_contraseña,
        },
    )
 
    if not ok:
        return False, data.get("error", "Error al cambiar la contraseña.") if data else "Error de conexión."
 
    return True, data.get("message", "Contraseña cambiada correctamente.")
