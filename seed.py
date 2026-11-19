from conexion import conectar_bd, obtener_nombre_bd, cerrar_bd


# Ejecutar la carga inicial dentro de transacciones gestionadas en la nube
def _crear_esquema(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Estudiante) REQUIRE e.matricula IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Materia) REQUIRE m.codigo IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Carrera) REQUIRE c.nombre IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Area) REQUIRE a.nombre IS UNIQUE")
    tx.run("CREATE INDEX idx_curso_calificacion IF NOT EXISTS FOR ()-[r:CURSO]-() ON (r.calificacion)")


def _insertar_datos(tx, estudiantes, materias, cursos, colaboraciones):
    tx.run("MATCH (n) DETACH DELETE n")

    for mat, nom, car, sem in estudiantes:
        tx.run(
            "MERGE (c:Carrera {nombre: $carrera}) "
            "MERGE (e:Estudiante {matricula: $matricula}) "
            "SET e.nombre = $nombre, e.semestre = $semestre "
            "MERGE (e)-[:PERTENECE_A]->(c)",
            matricula=mat, nombre=nom, carrera=car, semestre=sem,
        )

    for cod, nom, area in materias:
        tx.run(
            "MERGE (a:Area {nombre: $area}) "
            "MERGE (m:Materia {codigo: $codigo}) "
            "SET m.nombre = $nombre "
            "MERGE (m)-[:PERTENECE_AL_AREA]->(a)",
            codigo=cod, nombre=nom, area=area,
        )

    for mat, cod, calif, per in cursos:
        tx.run(
            "MATCH (e:Estudiante {matricula: $matricula}), (m:Materia {codigo: $codigo}) "
            "MERGE (e)-[r:CURSO {periodo: $periodo}]->(m) "
            "SET r.calificacion = $calificacion",
            matricula=mat, codigo=cod, calificacion=calif, periodo=per,
        )

    for m1, m2, proy in colaboraciones:
        if m1 > m2:
            m1, m2 = m2, m1
        tx.run(
            "MATCH (e1:Estudiante {matricula: $m1}), (e2:Estudiante {matricula: $m2}) "
            "MERGE (e1)-[:COLABORO_CON {proyecto: $proyecto}]->(e2)",
            m1=m1, m2=m2, proyecto=proy,
        )


# Borrar datos anteriores, crear restricciones y cargar nodos de prueba
def cargar_datos_iniciales(driver):
    estudiantes = [
        ("00548126", "Dante Stivaktas", "Ingeniería en TI", 5),
        ("00548201", "Ana Lopez", "Ingeniería en TI", 5),
        ("00548202", "Carlos Perez", "Ingeniería en TI", 6),
        ("00548203", "Sofia Ramirez", "Ingeniería en TI", 6),
        ("00548204", "Mateo Hernandez", "Ingeniería en TI", 5),
        ("00548205", "Diego Morales", "Ingeniería en TI", 3),
    ]

    materias = [
        ("BDA101", "Bases de Datos Avanzadas", "Datos"),
        ("WEB102", "Desarrollo Web", "Software"),
        ("EDA103", "Estructura de Datos", "Algoritmos"),
        ("RED104", "Redes de Computadoras", "Infraestructura"),
    ]

    cursos = [
        ("00548126", "WEB102", 9, "2026-1"),
        ("00548126", "EDA103", 8, "2026-1"),
        ("00548201", "BDA101", 10, "2026-1"),
        ("00548201", "WEB102", 9, "2026-1"),
        ("00548204", "BDA101", 9, "2026-1"),
        ("00548204", "EDA103", 10, "2026-1"),
        ("00548202", "BDA101", 8, "2026-1"),
        ("00548202", "RED104", 9, "2026-1"),
        ("00548203", "RED104", 10, "2026-1"),
        ("00548205", "RED104", 8, "2026-1"),
    ]

    colaboraciones = [
        ("00548126", "00548201", "Sistema Inventario"),
        ("00548201", "00548202", "API REST"),
        ("00548202", "00548203", "Red Local"),
        ("00548204", "00548205", "App Movil Campus"),
    ]

    try:
        with driver.session(database=obtener_nombre_bd()) as sesion:
            sesion.execute_write(_crear_esquema)
            sesion.execute_write(_insertar_datos, estudiantes, materias, cursos, colaboraciones)
        print("Datos iniciales cargados correctamente.")
    except Exception as error:
        print("Error al cargar datos iniciales:", error)


if __name__ == "__main__":
    driver = conectar_bd()
    if driver is not None:
        cargar_datos_iniciales(driver)
        cerrar_bd(driver)
