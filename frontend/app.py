import json
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)

MOCKS_DIR = Path(__file__).parent / "mocks"


def _load_mock(filename):
    with open(MOCKS_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


cursos_mock = {int(k): v for k, v in _load_mock("cursos.json").items()}
cronograma_por_curso = {int(k): v for k, v in _load_mock("cronograma.json").items()}
listar_alumnos = _load_mock("alumnos.json")
listar_materiales = _load_mock("materiales.json")
evaluaciones = _load_mock("evaluaciones.json")

listar_materias = [
    {"id": c["id"], "codigo": c["codigo"], "nombre": c["nombre"]}
    for c in cursos_mock.values()
]

CURSO_ACTIVO = cursos_mock[1]


@app.context_processor
def inject_curso_activo():
    return {"curso_activo": CURSO_ACTIVO}


_perfil_estudiante_raw = _load_mock("perfil_estudiante.json")
perfil_estudiante_mock = {
    **_perfil_estudiante_raw,
    "curso": {
        "codigo": CURSO_ACTIVO["codigo"],
        "nombre": CURSO_ACTIVO["nombre"],
        "carrera": CURSO_ACTIVO["carrera"],
        "modalidad": CURSO_ACTIVO["modalidad"],
        **_perfil_estudiante_raw["curso"],
    },
}

_perfil_profesor_raw = _load_mock("perfil_profesor.json")
perfil_profesor_mock = {
    **_perfil_profesor_raw,
    "catedra": {
        "codigo": CURSO_ACTIVO["codigo"],
        "nombre": CURSO_ACTIVO["nombre"],
        "alumnos": CURSO_ACTIVO["stats"]["alumnos"],
        "modalidad": CURSO_ACTIVO["modalidad"],
        "carga_horaria": CURSO_ACTIVO["horas_semanales"],
        **_perfil_profesor_raw["catedra"],
    },
}

try:
    reporte_stats_mock = _load_mock("reporte_estadisticas.json")
    listar_equipos_mock = _load_mock("equipos.json")
except Exception:
    reporte_stats_mock = []
    listar_equipos_mock = []

@app.route("/")
def index():
    return redirect(url_for("curso", curso_id=CURSO_ACTIVO["id"]))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and password == "1234":
            return redirect(url_for('materias')) 
            
    return render_template('login.html')

@app.route("/materias")
def materias():
    return render_template(
        "materias.html",
        title="Materias",
        active_page="materias",
        materias=listar_materias,
    )


@app.route("/alumnos")
def alumnos_page():
    return render_template(
        "alumnos.html",
        title="Alumnos",
        active_page="alumnos",
        alumnos=listar_alumnos,
    )


@app.route("/material")
def material():
    return render_template(
        "material.html",
        title="Material",
        active_page="material",
        materiales=listar_materiales,
    )


@app.route("/evaluaciones")
def evaluaciones_page():
    return render_template(
        "evaluaciones.html",
        title="Evaluaciones",
        active_page="evaluaciones",
        evaluaciones=evaluaciones,
    )


@app.route("/reportes")
def reportes_page():
    # Identificamos qué pestaña mostrar. Por defecto va a 'alumnos'
    tab_actual = request.args.get("tab", "alumnos")
    
    # Capturamos filtros de alumnos
    carrera_filtro = request.args.get("carrera", "")
    condicion_filtro = request.args.get("condicion", "")
    
    # SIMULACIÓN DE FILTRADO PARA ALUMNO (Hardcodeado sobre tus mocks)
    alumnos_filtrados = listar_alumnos
    if carrera_filtro:
        alumnos_filtrados = [a for a in alumnos_filtrados if a.get("carrera") == carrera_filtro]
    if condicion_filtro:
        # Simulamos que en una base de datos real filtraría por notas, acá lo hacemos conceptual
        if condicion_filtro == "aprobado":
            alumnos_filtrados = alumnos_filtrados[:30] # una porción mock
        else:
            alumnos_filtrados = alumnos_filtrados[30:]

    return render_template(
        "reportes.html",
        title="Reportes de Cátedra",
        active_page="reportes", # Cambiá esto en tu navbar si tenés un link a reportes
        tab_actual=tab_actual,
        alumnos=alumnos_filtrados,
        estadisticas=reporte_stats_mock,
        equipos=listar_equipos_mock,
        carrera_filtro=carrera_filtro,
        condicion_filtro=condicion_filtro,
        curso_id_hardcodeado=1
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
        semanas=cronograma_por_curso.get(CURSO_ACTIVO["id"], []),
    )


if __name__ == "__main__":
    app.run(debug=True)
