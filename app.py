from flask import Flask, jsonify, render_template, request
from conexion import conectar_bd, cerrar_bd
from seed import cargar_datos_iniciales
import operaciones as op

app = Flask(__name__)
driver = None


# Abrir conexion con Neo4j si todavia no existe
def get_driver():
    global driver
    if driver is None:
        driver = conectar_bd()
    return driver


# Pagina principal en el navegador
@app.route("/")
def inicio():
    return render_template("index.html")


# Obtener listas actuales de estudiantes, materias, cursos y colaboraciones
@app.route("/api/datos", methods=["GET"])
def api_datos():
    d = get_driver()
    if d is None:
        return jsonify({"ok": False, "mensaje": "Sin conexion a Neo4j AuraDB."}), 500
    return jsonify(
        {
            "ok": True,
            "estudiantes": op.listar_estudiantes(d),
            "materias": op.listar_materias(d),
            "cursos": op.listar_cursos(d),
            "colaboraciones": op.listar_colaboraciones(d),
        }
    )


# Reiniciar los datos iniciales en la nube
@app.route("/api/seed", methods=["POST"])
def api_seed():
    cargar_datos_iniciales(get_driver())
    return jsonify({"ok": True, "mensaje": "Base reiniciada con datos iniciales."})


# Guardar estudiante
@app.route("/api/estudiantes", methods=["POST"])
def api_guardar_estudiante():
    datos = request.get_json() or {}
    ok, msg = op.crear_estudiante(
        get_driver(),
        datos.get("matricula", ""),
        datos.get("nombre", ""),
        datos.get("carrera", ""),
        datos.get("semestre", ""),
    )
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Actualizar semestre de un estudiante
@app.route("/api/estudiantes/<matricula>/semestre", methods=["PUT"])
def api_actualizar_semestre(matricula):
    datos = request.get_json() or {}
    ok, msg = op.actualizar_semestre(get_driver(), matricula, datos.get("semestre", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Eliminar estudiante con DETACH DELETE
@app.route("/api/estudiantes/<matricula>", methods=["DELETE"])
def api_eliminar_estudiante(matricula):
    ok, msg = op.eliminar_estudiante(get_driver(), matricula)
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Consultar historial de un estudiante
@app.route("/api/estudiantes/<matricula>/historial", methods=["GET"])
def api_historial(matricula):
    ok, msg, datos = op.consultar_historial(get_driver(), matricula)
    return jsonify({"ok": ok, "mensaje": msg, "datos": datos}), (200 if ok else 404)


# Guardar materia
@app.route("/api/materias", methods=["POST"])
def api_guardar_materia():
    datos = request.get_json() or {}
    ok, msg = op.crear_materia(get_driver(), datos.get("codigo", ""), datos.get("nombre", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Registrar, actualizar o dar de baja un curso
@app.route("/api/cursos", methods=["POST", "PUT", "DELETE"])
def api_cursos():
    datos = request.get_json() or {}
    d = get_driver()
    if request.method == "POST":
        ok, msg = op.registrar_curso(
            d, datos.get("matricula", ""), datos.get("codigo", ""), datos.get("calificacion", ""), datos.get("periodo", "")
        )
    elif request.method == "PUT":
        ok, msg = op.actualizar_calificacion(
            d, datos.get("matricula", ""), datos.get("codigo", ""), datos.get("calificacion", ""), datos.get("periodo", "")
        )
    else:
        ok, msg = op.eliminar_curso(d, datos.get("matricula", ""), datos.get("codigo", ""), datos.get("periodo", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Registrar o eliminar una colaboracion
@app.route("/api/colaboraciones", methods=["POST", "DELETE"])
def api_colaboraciones():
    datos = request.get_json() or {}
    d = get_driver()
    if request.method == "POST":
        ok, msg = op.registrar_colaboracion(
            d, datos.get("matricula1", ""), datos.get("matricula2", ""), datos.get("proyecto", "")
        )
    else:
        ok, msg = op.eliminar_colaboracion(
            d, datos.get("matricula1", ""), datos.get("matricula2", ""), datos.get("proyecto", "")
        )
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Consulta especializada 1: recomendar asesores por vecindad
@app.route("/api/asesores", methods=["GET"])
def api_asesores():
    mat = request.args.get("matricula", "").strip()
    cod = request.args.get("codigo", "").strip()
    if not mat or not cod:
        return jsonify({"ok": False, "mensaje": "Matricula y codigo son obligatorios.", "datos": None}), 400
    ok, msg, datos = op.recomendar_asesores(get_driver(), mat, cod)
    return jsonify({"ok": ok, "mensaje": msg, "datos": datos}), 200


# Consulta especializada 2: camino mas corto con shortestPath
@app.route("/api/camino", methods=["GET"])
def api_camino():
    orig = request.args.get("origen", "").strip()
    dest = request.args.get("destino", "").strip()
    if not orig or not dest or orig == dest:
        return jsonify({"ok": False, "mensaje": "Origen y destino deben ser validos y distintos.", "datos": None}), 400
    ok, msg, datos = op.buscar_camino_mas_corto(get_driver(), orig, dest)
    return jsonify({"ok": ok, "mensaje": msg, "datos": datos}), 200


if __name__ == "__main__":
    try:
        if get_driver() is not None:
            print("Servidor corriendo en http://127.0.0.1:5000")
            app.run(host="127.0.0.1", port=5000, debug=False)
    finally:
        cerrar_bd(driver)
