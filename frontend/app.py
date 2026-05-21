from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

listar_materias = [
    {"nombre": "Materia 1"},
    {"nombre": "Materia 2"},
    {"nombre": "Materia 3"},
]

listar_alumnos = [
    {"legajo": "1001", "nombre": "Alumno 1", "estado": "Activo"},
    {"legajo": "1002", "nombre": "Alumno 2", "estado": "Activo"},
    {"legajo": "1003", "nombre": "Alumno 3", "estado": "Inactivo"},
]

listar_materiales = [
    {"titulo": "Material 1"},
    {"titulo": "Material 2"},
    {"titulo": "Material 3"},
]

evaluaciones = [
    {"nombre": "Evaluación 1", "fecha": "01/01"},
    {"nombre": "Evaluación 2", "fecha": "02/01"},
    {"nombre": "Evaluación 3", "fecha": "03/01"},
]


@app.route("/")
def index():
    return redirect(url_for("materias"))


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


@app.route("/metricas")
def metricas():
    return render_template(
        "metricas.html",
        title="Métricas",
        active_page="metricas",
    )


@app.route("/perfil")
def perfil():
    return render_template(
        "perfil.html",
        title="Perfil",
        active_page="perfil",
    )


if __name__ == "__main__":
    app.run(debug=True)
