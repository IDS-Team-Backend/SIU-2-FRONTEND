from flask import Flask, render_template, request, redirect, url_for, flash

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
    {"titulo": "Evaluación 1", "curso_id": 1, "fecha": "01/01", "tipo_evaluacion_id": 1, "descripcion": "Descripción de la evaluación 1"},
    {"titulo": "Evaluación 2", "curso_id": 2, "fecha": "02/01", "tipo_evaluacion_id": 2, "descripcion": "Descripción de la evaluación 2"},
    {"titulo": "Evaluación 3", "curso_id": 3, "fecha": "03/01", "tipo_evaluacion_id": 3, "descripcion": "Descripción de la evaluación 3"},
]

@app.route("/")
def index():
    return redirect(url_for("materias"))


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
