from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

listar_materias = [
    {"nombre": "Materia 1"},
    {"nombre": "Materia 2"},
    {"nombre": "Materia 3"},
]

listar_alumnos = [
    {"id": "1001", "nombre": "Bruno", "apellido": "Lanzillota", "email": "blanzilotta@gmail.com", "dni": "1234678", "activo": 1},
    {"id": "1002", "nombre": "Leonel", "apellido": "Chavez", "email": "bchavez@gmail.com", "dni": "1234677", "activo": 0},
    {"id": "1003", "nombre": "Nestor", "apellido": "Pala", "email": "npala@gmail.com", "dni": "1234566", "activo": 1},
]

listar_materiales = [
    {
        'id': 1,
        'curso_id': 1,
        'titulo': 'Instalación de Virtual Machine (Versión nueva)',
        'archivo_url': '/uploads/vm_nueva.pdf',
        'subido_por': 1,
        'created_at': '2024-01-15 10:30:00'
    },
    {
        'id': 2,
        'curso_id': 1,
        'titulo': 'Instalación de Virtual Machine (Versión antigua)',
        'archivo_url': '/uploads/vm_antigua.pdf',
        'subido_por': 1,
        'created_at': '2024-01-15 10:35:00'
    },
    {
        'id': 3,
        'curso_id': 2,
        'titulo': 'Primeros pasos en Linux',
        'archivo_url': '/uploads/linux_primeros_pasos.pdf',
        'subido_por': 1,
        'created_at': '2024-01-20 14:20:00'
    },
    {
        'id': 4,
        'curso_id': 2,
        'titulo': 'Docker',
        'archivo_url': '/uploads/debugger_vscode.pdf',
        'subido_por': 2
    }
]

evaluaciones = [
    {"titulo": "Parcialito", "curso_id": 1, "fecha": "01/01", "tipo_evaluacion_id": 1, "descripcion": "Instancia autoevaluatoria de backend", "activo": 1},
    {"titulo": "1er Parcial", "curso_id": 2, "fecha": "02/01", "tipo_evaluacion_id": 2, "descripcion": "Examen de frontend y flask"},
    {"titulo": "Defensa Oral", "curso_id": 3, "fecha": "03/01", "tipo_evaluacion_id": 3, "descripcion": "Entrega del proyecto final", "activo": 1},
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
