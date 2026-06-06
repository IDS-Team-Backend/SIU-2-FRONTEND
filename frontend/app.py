import json
import os
from pathlib import Path
from services.auth_service import usuario_logueado
from services.decorators import proteger_rutas
from routes import register_routes
from utils.api_client import api_request
from flask import Flask, render_template, request, redirect, url_for, abort
from datetime import datetime

CURSO_ACTIVO_ID = int(os.getenv("CURSO_ACTIVO_ID", "1"))

app = Flask(__name__)
app.secret_key = "pon_aqui_una_clave_secreta_segura"

register_routes(app)
proteger_rutas(app)


MOCKS_DIR = Path(__file__).parent / "mocks"

def _load_mock(filename):
    with open(MOCKS_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


cursos_mock = {int(k): v for k, v in _load_mock("cursos.json").items()}
listar_alumnos = _load_mock("alumnos.json")
listar_materiales = _load_mock("materiales.json")

listar_materias = [
    {"id": c["id"], "codigo": c["codigo"], "nombre": c["nombre"]}
    for c in cursos_mock.values()
]



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


@app.route("/curso/<int:curso_id>/cronograma")
def cronograma(curso_id):
    ok, data = api_request("GET", f"/cursos/{curso_id}/cronograma")
    semanas = data.get("semanas", []) if ok and data else []
    return render_template(
        "cronograma.html",
        title="Cronograma",
        active_page="cronograma",
        semanas=semanas,
    )



@app.template_filter('formatear_fecha')
def formatear_fecha(fecha_str):
    if not fecha_str:
        return ''
    try:
        fecha_obj = datetime.strptime(fecha_str, '%a, %d %b %Y %H:%M:%S %Z')
        return fecha_obj.strftime('%d/%m/%Y')
    except:
        return fecha_str  
if __name__ == "__main__":
    app.run(port=5001, debug=True)
