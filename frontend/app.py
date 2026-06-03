import json
import os
from pathlib import Path
from services.auth_service import usuario_logueado
from routes import register_routes
from utils.api_client import api_request
from flask import Flask, render_template, request, redirect, url_for, flash, abort
CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

app = Flask(__name__)
app.secret_key = "pon_aqui_una_clave_secreta_segura"

register_routes(app)


MOCKS_DIR = Path(__file__).parent / "mocks"

def _load_mock(filename):
    with open(MOCKS_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


cursos_mock = {int(k): v for k, v in _load_mock("cursos.json").items()}
cronograma_por_curso = {int(k): v for k, v in _load_mock("cronograma.json").items()}
listar_alumnos = _load_mock("alumnos.json")
listar_materiales = _load_mock("materiales.json")

listar_materias = [
    {"id": c["id"], "codigo": c["codigo"], "nombre": c["nombre"]}
    for c in cursos_mock.values()
]

_perfil_estudiante_raw = _load_mock("perfil_estudiante.json")
perfil_estudiante_mock = {
    **_perfil_estudiante_raw,
    "curso": {
        "codigo": cursos_mock[CURSO_ACTIVO_ID]["codigo"],
        "nombre": cursos_mock[CURSO_ACTIVO_ID]["nombre"],
        "carrera": cursos_mock[CURSO_ACTIVO_ID]["carrera"],
        "modalidad": cursos_mock[CURSO_ACTIVO_ID]["modalidad"],
        **_perfil_estudiante_raw["curso"],
    },
}

_perfil_profesor_raw = _load_mock("perfil_profesor.json")
perfil_profesor_mock = {
    **_perfil_profesor_raw,
    "catedra": {
        "codigo": cursos_mock[CURSO_ACTIVO_ID]["codigo"],
        "nombre": cursos_mock[CURSO_ACTIVO_ID]["nombre"],
        "alumnos": cursos_mock[CURSO_ACTIVO_ID]["stats"]["alumnos"],
        "modalidad": cursos_mock[CURSO_ACTIVO_ID]["modalidad"],
        "carga_horaria": cursos_mock[CURSO_ACTIVO_ID]["horas_semanales"],
        **_perfil_profesor_raw["catedra"],
    },
}


@app.context_processor
def inject_curso_activo():
    if not usuario_logueado():
        return {"curso_activo": {"id": CURSO_ACTIVO_ID, "nombre": "Sistema"}}
    ok, data = api_request("GET", f"/cursos/{CURSO_ACTIVO_ID}")
    if ok and data:
        return {"curso_activo": data}
    return {"curso_activo": {"id": CURSO_ACTIVO_ID, "nombre": "Sistema"}}
 
 
@app.context_processor
def inject_usuario_actual():
    if not usuario_logueado():
        return {"usuario_actual": None}
    ok, data = api_request("GET", "/auth/me/perfiles")
    if ok and data:
        return {"usuario_actual": {"perfiles": data.get("perfiles", [])}}
    return {"usuario_actual": None}


@app.route("/")
def index():
    return redirect(url_for("curso", curso_id=CURSO_ACTIVO_ID))


@app.route("/materias")
def materias():
    return render_template(
        "materias.html",
        title="Materias",
        active_page="materias",
        materias=listar_materias,
    )


@app.route("/material")
def material():
    return render_template(
        "material.html",
        title="Material",
        active_page="material",
        materiales=listar_materiales,
    )


@app.route("/perfil")
def perfil():
    return redirect(url_for("perfil_estudiante"))


@app.route("/perfil/estudiante")
def perfil_estudiante():
    return render_template(
        "perfil_estudiante.html",
        title="Perfil Estudiante",
        active_page="perfil",
        perfil=perfil_estudiante_mock,
    )


@app.route("/perfil/profesor")
def perfil_profesor():
    return render_template(
        "perfil_profesor.html",
        title="Perfil Docente",
        active_page="perfil",
        perfil=perfil_profesor_mock,
    )


@app.route("/curso/<int:curso_id>")
def curso(curso_id):
    curso_data = cursos_mock.get(curso_id)
    if curso_data is None:
        abort(404)
    return render_template(
        "curso.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )


@app.route("/cronograma")
def cronograma():
    return render_template(
        "cronograma.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=cronograma_por_curso.get(CURSO_ACTIVO_ID, []),
    )

if __name__ == "__main__":
    app.run(port=5001, debug=True)



@app.route("/perfil")
def perfil():
    return redirect(url_for("perfil_estudiante"))


@app.route("/perfil/estudiante")
def perfil_estudiante():
    return render_template(
        "perfil_estudiante.html",
        title="Perfil Estudiante",
        active_page="perfil",
        perfil=perfil_estudiante_mock,
    )


@app.route("/perfil/profesor")
def perfil_profesor():
    return render_template(
        "perfil_profesor.html",
        title="Perfil Docente",
        active_page="perfil",
        perfil=perfil_profesor_mock,
    )


@app.route("/curso/<int:curso_id>")
def curso(curso_id):
    curso_data = cursos_mock.get(curso_id)
    if curso_data is None:
        abort(404)
    return render_template(
        "curso.html",
        title=curso_data["nombre"],
        active_page="curso",
        curso=curso_data,
    )


@app.route("/cronograma")
def cronograma():
    return render_template(
        "cronograma.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=cronograma_por_curso.get(CURSO_ACTIVO_ID, []),
    )


if __name__ == "__main__":
    app.run(port=5001, debug=True)
