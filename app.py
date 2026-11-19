import os
from flask import Flask, jsonify, render_template, request
from conexion import conectar_bd, cerrar_bd
from seed import cargar_datos_iniciales
import operaciones as op

app = Flask(__name__)
driver = None


# Abrir conexion si todavia no existe
def get_driver():
    global driver
    if driver is None:
        driver = conectar_bd()
    return driver


# Pagina principal del frontend
@app.route("/")
def inicio():
    return render_template("index.html")


# Devolver nodos, relaciones y catalogos actuales
@app.route("/api/grafo", methods=["GET"])
def api_grafo():
    d = get_driver()
    if d is None:
        return jsonify({"ok": False, "mensaje": "Sin conexion a Neo4j."}), 500
    nodos, relaciones = op.obtener_grafo(d)
    return jsonify(
        {
            "ok": True,
            "nodos": nodos,
            "relaciones": relaciones,
            "estudiantes": op.listar_estudiantes(d),
            "materias": op.listar_materias(d),
        }
    )


# Reiniciar los datos iniciales en la nube (exige SEED_TOKEN obligatorio y confirmacion)
@app.route("/api/seed", methods=["POST"])
def api_seed():
    datos = request.get_json(silent=True) or {}
    token_env = os.getenv("SEED_TOKEN", "").strip()
    if not token_env:
        return jsonify({"ok": False, "mensaje": "SEED_TOKEN no esta configurado en el servidor."}), 503
    token_req = request.headers.get("X-Seed-Token", datos.get("token", "")).strip()
    if token_req != token_env:
        return jsonify({"ok": False, "mensaje": "Token de autorizacion invalido o faltante."}), 403
    if datos.get("confirmar") is not True:
        return jsonify({"ok": False, "mensaje": "Se requiere confirmar=true en el cuerpo JSON para reiniciar la base."}), 400
    cargar_datos_iniciales(get_driver())
    return jsonify({"ok": True, "mensaje": "Base reiniciada con datos iniciales."})


# Crear estudiante nuevo
@app.route("/api/estudiantes", methods=["POST"])
def api_crear_estudiante():
    datos = request.get_json() or {}
    ok, msg = op.crear_estudiante(
        get_driver(), datos.get("matricula", ""), datos.get("nombre", ""), datos.get("carrera", ""), datos.get("semestre", "")
    )
    return jsonify({"ok": ok, "mensaje": msg}), (201 if ok else 400)


# Actualizar datos completos de un estudiante
@app.route("/api/estudiantes/<matricula>", methods=["PUT"])
def api_actualizar_estudiante(matricula):
    datos = request.get_json() or {}
    ok, msg = op.actualizar_estudiante(
        get_driver(), matricula, datos.get("nombre", ""), datos.get("carrera", ""), datos.get("semestre", "")
    )
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 404)


# Actualizar semestre de un estudiante
@app.route("/api/estudiantes/<matricula>/semestre", methods=["PUT"])
def api_actualizar_semestre(matricula):
    datos = request.get_json() or {}
    ok, msg = op.actualizar_semestre(get_driver(), matricula, datos.get("semestre", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Eliminar estudiante completo con DETACH DELETE
@app.route("/api/estudiantes/<matricula>", methods=["DELETE"])
def api_eliminar_estudiante(matricula):
    ok, msg = op.eliminar_estudiante(get_driver(), matricula)
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Ver historial de un estudiante
@app.route("/api/estudiantes/<matricula>/historial", methods=["GET"])
def api_historial(matricula):
    ok, msg, datos = op.consultar_historial(get_driver(), matricula)
    return jsonify({"ok": ok, "mensaje": msg, "datos": datos}), (200 if ok else 404)


# Crear materia nueva
@app.route("/api/materias", methods=["POST"])
def api_crear_materia():
    datos = request.get_json() or {}
    ok, msg = op.crear_materia(get_driver(), datos.get("codigo", ""), datos.get("nombre", ""), datos.get("area", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (201 if ok else 400)


# Actualizar datos de una materia existente
@app.route("/api/materias/<codigo>", methods=["PUT"])
def api_actualizar_materia(codigo):
    datos = request.get_json() or {}
    ok, msg = op.actualizar_materia(get_driver(), codigo, datos.get("nombre", ""), datos.get("area", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 404)


# Registrar, actualizar o dar de baja un curso
@app.route("/api/cursos", methods=["POST", "PUT", "DELETE"])
def api_cursos():
    datos = request.get_json() or {}
    d = get_driver()
    if request.method == "POST":
        ok, msg = op.registrar_curso(d, datos.get("matricula", ""), datos.get("codigo", ""), datos.get("calificacion", ""), datos.get("periodo", ""))
    elif request.method == "PUT":
        ok, msg = op.actualizar_calificacion(d, datos.get("matricula", ""), datos.get("codigo", ""), datos.get("calificacion", ""), datos.get("periodo", ""))
    else:
        ok, msg = op.eliminar_curso(d, datos.get("matricula", ""), datos.get("codigo", ""), datos.get("periodo", ""))
    return jsonify({"ok": ok, "mensaje": msg}), (200 if ok else 400)


# Registrar o eliminar colaboracion entre dos estudiantes
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


# Consulta 1: recomendar asesores por vecindad
@app.route("/api/asesores", methods=["GET"])
def api_asesores():
    mat = request.args.get("matricula", "").strip()
    cod = request.args.get("codigo", "").strip()
    if not mat or not cod:
        return jsonify({"ok": False, "encontrado": False, "mensaje": "Matricula y codigo son obligatorios.", "datos": None}), 400
    ok, msg, datos = op.recomendar_asesores(get_driver(), mat, cod)
    return jsonify({"ok": ok, "encontrado": ok, "mensaje": msg, "datos": datos}), 200


# Consulta 2: camino mas corto entre dos estudiantes
@app.route("/api/camino", methods=["GET"])
def api_camino():
    orig = request.args.get("origen", "").strip()
    dest = request.args.get("destino", "").strip()
    if not orig or not dest or orig == dest:
        return jsonify({"ok": False, "encontrado": False, "mensaje": "Origen y destino validos y distintos son obligatorios.", "datos": None}), 400
    incluir = request.args.get("incluir_materias", "0") == "1"
    ok, msg, datos = op.buscar_camino_mas_corto(get_driver(), orig, dest, incluir)
    return jsonify({"ok": ok, "encontrado": ok, "mensaje": msg, "datos": datos}), 200


if __name__ == "__main__":
    try:
        if get_driver() is not None:
            print("Servidor corriendo en http://127.0.0.1:5000")
            app.run(host="127.0.0.1", port=5000, debug=False)
    finally:
        cerrar_bd(driver)
