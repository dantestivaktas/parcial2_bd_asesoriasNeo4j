from conexion import obtener_nombre_bd


# Crear o actualizar un estudiante
def crear_estudiante(driver, matricula, nombre, carrera, semestre):
    matricula = str(matricula).strip()
    nombre = str(nombre).strip()
    carrera = str(carrera).strip()
    if not matricula or not nombre or not carrera:
        return False, "Matricula, nombre y carrera son obligatorios."

    try:
        semestre = int(semestre)
        if semestre < 1 or semestre > 12:
            return False, "El semestre debe estar entre 1 y 12."

        consulta = (
            "MERGE (e:Estudiante {matricula: $matricula}) "
            "SET e.nombre = $nombre, e.carrera = $carrera, e.semestre = $semestre "
            "RETURN e.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(
                consulta, matricula=matricula, nombre=nombre, carrera=carrera, semestre=semestre
            ).single()
        return True, "Estudiante guardado: " + res["nombre"] + " (" + matricula + ")"
    except Exception as error:
        return False, "Error al guardar estudiante: " + str(error)


# Crear o actualizar una materia
def crear_materia(driver, codigo, nombre):
    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()
    if not codigo or not nombre:
        return False, "Codigo y nombre son obligatorios."

    try:
        consulta = (
            "MERGE (m:Materia {codigo: $codigo}) "
            "SET m.nombre = $nombre "
            "RETURN m.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, codigo=codigo, nombre=nombre).single()
        return True, "Materia guardada: " + codigo + " - " + res["nombre"]
    except Exception as error:
        return False, "Error al guardar materia: " + str(error)


# Registrar materia cursada por periodo
def registrar_curso(driver, matricula, codigo, calificacion, periodo):
    matricula = str(matricula).strip()
    codigo = str(codigo).strip().upper()
    periodo = str(periodo).strip()
    if not matricula or not codigo or not periodo:
        return False, "Matricula, codigo y periodo son obligatorios."

    try:
        calificacion = int(calificacion)
        if calificacion < 0 or calificacion > 10:
            return False, "La calificacion debe estar entre 0 y 10."

        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula}), (m:Materia {codigo: $codigo}) "
            "MERGE (e)-[r:CURSO {periodo: $periodo}]->(m) "
            "SET r.calificacion = $calificacion "
            "RETURN e.nombre AS est, m.nombre AS mat"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(
                consulta, matricula=matricula, codigo=codigo, calificacion=calificacion, periodo=periodo
            ).single()
        if not res:
            return False, "No se encontro el estudiante o la materia."
        return True, "Curso registrado: " + res["est"] + " en " + res["mat"] + " (" + periodo + ")"
    except Exception as error:
        return False, "Error al registrar curso: " + str(error)


# Registrar colaboracion entre dos estudiantes en un proyecto
def registrar_colaboracion(driver, matricula1, matricula2, proyecto):
    m1 = str(matricula1).strip()
    m2 = str(matricula2).strip()
    proyecto = str(proyecto).strip()
    if not m1 or not m2 or not proyecto:
        return False, "Matriculas y proyecto son obligatorios."
    if m1 == m2:
        return False, "Los estudiantes deben ser diferentes."

    try:
        consulta = (
            "MATCH (e1:Estudiante {matricula: $m1}), (e2:Estudiante {matricula: $m2}) "
            "MERGE (e1)-[r:COLABORO_CON {proyecto: $proyecto}]->(e2) "
            "RETURN e1.nombre AS n1, e2.nombre AS n2"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, m1=m1, m2=m2, proyecto=proyecto).single()
        if not res:
            return False, "No se encontraron ambos estudiantes."
        return True, "Colaboracion registrada entre " + res["n1"] + " y " + res["n2"] + " (" + proyecto + ")"
    except Exception as error:
        return False, "Error al registrar colaboracion: " + str(error)


# Listar todos los estudiantes
def listar_estudiantes(driver):
    consulta = (
        "MATCH (e:Estudiante) "
        "RETURN e.matricula AS matricula, e.nombre AS nombre, e.carrera AS carrera, e.semestre AS semestre "
        "ORDER BY e.matricula"
    )
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return [dict(r) for r in sesion.run(consulta)]


# Listar todas las materias
def listar_materias(driver):
    consulta = (
        "MATCH (m:Materia) "
        "RETURN m.codigo AS codigo, m.nombre AS nombre "
        "ORDER BY m.codigo"
    )
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return [dict(r) for r in sesion.run(consulta)]


# Listar todos los cursos registrados
def listar_cursos(driver):
    consulta = (
        "MATCH (e:Estudiante)-[r:CURSO]->(m:Materia) "
        "RETURN e.matricula AS matricula, e.nombre AS estudiante, "
        "m.codigo AS codigo, m.nombre AS materia, r.calificacion AS calificacion, r.periodo AS periodo "
        "ORDER BY e.matricula, r.periodo"
    )
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return [dict(r) for r in sesion.run(consulta)]


# Listar todas las colaboraciones registradas
def listar_colaboraciones(driver):
    consulta = (
        "MATCH (e1:Estudiante)-[r:COLABORO_CON]->(e2:Estudiante) "
        "RETURN e1.matricula AS matricula1, e1.nombre AS estudiante1, "
        "e2.matricula AS matricula2, e2.nombre AS estudiante2, r.proyecto AS proyecto "
        "ORDER BY r.proyecto"
    )
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return [dict(r) for r in sesion.run(consulta)]


# Consultar historial de cursos y colaboraciones de un estudiante
def consultar_historial(driver, matricula):
    matricula = str(matricula).strip()
    if not matricula:
        return False, "Ingresa una matricula.", None

    try:
        with driver.session(database=obtener_nombre_bd()) as sesion:
            est = sesion.run(
                "MATCH (e:Estudiante {matricula: $m}) "
                "RETURN e.matricula AS matricula, e.nombre AS nombre, e.carrera AS carrera, e.semestre AS semestre",
                m=matricula,
            ).single()
            if not est:
                return False, "No se encontro el estudiante.", None

            cursos = [
                dict(r)
                for r in sesion.run(
                    "MATCH (e:Estudiante {matricula: $m})-[r:CURSO]->(mat:Materia) "
                    "RETURN mat.codigo AS codigo, mat.nombre AS materia, r.calificacion AS calificacion, r.periodo AS periodo "
                    "ORDER BY r.periodo, mat.codigo",
                    m=matricula,
                )
            ]
            colabs = [
                dict(r)
                for r in sesion.run(
                    "MATCH (e:Estudiante {matricula: $m})-[r:COLABORO_CON]-(c:Estudiante) "
                    "RETURN c.matricula AS matricula, c.nombre AS nombre, r.proyecto AS proyecto "
                    "ORDER BY c.nombre, r.proyecto",
                    m=matricula,
                )
            ]
        return True, "Historial encontrado.", {"estudiante": dict(est), "cursos": cursos, "colaboraciones": colabs}
    except Exception as error:
        return False, "Error al consultar historial: " + str(error), None


# Actualizar el semestre de un estudiante
def actualizar_semestre(driver, matricula, nuevo_semestre):
    matricula = str(matricula).strip()
    try:
        nuevo_semestre = int(nuevo_semestre)
        if nuevo_semestre < 1 or nuevo_semestre > 12:
            return False, "El semestre debe estar entre 1 y 12."

        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula}) "
            "SET e.semestre = $semestre "
            "RETURN e.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, matricula=matricula, semestre=nuevo_semestre).single()
        if not res:
            return False, "No se encontro el estudiante."
        return True, "Semestre actualizado para " + res["nombre"] + " a " + str(nuevo_semestre)
    except Exception as error:
        return False, "Error al actualizar semestre: " + str(error)


# Actualizar la calificacion de un curso en un periodo
def actualizar_calificacion(driver, matricula, codigo, nueva_calificacion, periodo):
    matricula = str(matricula).strip()
    codigo = str(codigo).strip().upper()
    periodo = str(periodo).strip()
    if not matricula or not codigo or not periodo:
        return False, "Matricula, codigo y periodo son obligatorios."

    try:
        nueva_calificacion = int(nueva_calificacion)
        if nueva_calificacion < 0 or nueva_calificacion > 10:
            return False, "La calificacion debe estar entre 0 y 10."

        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula})-[r:CURSO {periodo: $periodo}]->(m:Materia {codigo: $codigo}) "
            "SET r.calificacion = $calificacion "
            "RETURN e.nombre AS nombre, m.nombre AS materia"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(
                consulta, matricula=matricula, codigo=codigo, calificacion=nueva_calificacion, periodo=periodo
            ).single()
        if not res:
            return False, "No se encontro ese curso en el periodo indicado."
        return True, "Calificacion actualizada a " + str(nueva_calificacion) + " en " + res["materia"] + " (" + periodo + ")"
    except Exception as error:
        return False, "Error al actualizar calificacion: " + str(error)


# Eliminar solo la relacion :CURSO de un periodo especifico
def eliminar_curso(driver, matricula, codigo, periodo):
    matricula = str(matricula).strip()
    codigo = str(codigo).strip().upper()
    periodo = str(periodo).strip()
    if not matricula or not codigo or not periodo:
        return False, "Matricula, codigo y periodo son obligatorios."

    try:
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula})-[r:CURSO {periodo: $periodo}]->(m:Materia {codigo: $codigo}) "
            "DELETE r "
            "RETURN e.nombre AS est, m.nombre AS mat"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = list(sesion.run(consulta, matricula=matricula, codigo=codigo, periodo=periodo))
        if not res:
            return False, "No se encontro ese curso registrado."
        return True, "Curso dado de baja: " + res[0]["mat"] + " (" + periodo + ") para " + res[0]["est"]
    except Exception as error:
        return False, "Error al dar de baja curso: " + str(error)


# Eliminar una relacion :COLABORO_CON especifica
def eliminar_colaboracion(driver, matricula1, matricula2, proyecto):
    m1 = str(matricula1).strip()
    m2 = str(matricula2).strip()
    proyecto = str(proyecto).strip()
    if not m1 or not m2 or not proyecto:
        return False, "Matriculas y proyecto son obligatorios."

    try:
        consulta = (
            "MATCH (e1:Estudiante {matricula: $m1})-[r:COLABORO_CON {proyecto: $proyecto}]-(e2:Estudiante {matricula: $m2}) "
            "DELETE r "
            "RETURN e1.nombre AS est1, e2.nombre AS est2"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = list(sesion.run(consulta, m1=m1, m2=m2, proyecto=proyecto))
        if not res:
            return False, "No se encontro esa colaboracion."
        return True, "Colaboracion eliminada entre " + res[0]["est1"] + " y " + res[0]["est2"] + " (" + proyecto + ")"
    except Exception as error:
        return False, "Error al eliminar colaboracion: " + str(error)


# Eliminar un estudiante y todas sus relaciones con DETACH DELETE
def eliminar_estudiante(driver, matricula):
    matricula = str(matricula).strip()
    try:
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula}) "
            "WITH e, e.nombre AS nombre "
            "DETACH DELETE e "
            "RETURN nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, matricula=matricula).single()
        if not res:
            return False, "No se encontro el estudiante."
        return True, "Estudiante eliminado: " + res["nombre"]
    except Exception as error:
        return False, "Error al eliminar estudiante: " + str(error)


# Consulta especializada 1: recomendar asesores con calificacion >= 9
def recomendar_asesores(driver, mi_matricula, codigo):
    matricula = str(mi_matricula).strip()
    codigo = str(codigo).strip().upper()

    consulta = (
        "MATCH (yo:Estudiante {matricula: $matricula}) "
        "MATCH (compa:Estudiante)-[r:CURSO]->(m:Materia {codigo: $codigo}) "
        "WHERE compa.matricula <> $matricula AND r.calificacion >= 9 "
        "WITH yo, compa, m, max(r.calificacion) AS calificacion "
        "OPTIONAL MATCH (yo)-[col:COLABORO_CON]-(compa) "
        "OPTIONAL MATCH (yo)-[:CURSO]->(comun:Materia)<-[:CURSO]-(compa) "
        "WHERE comun.codigo <> $codigo "
        "RETURN yo.nombre AS solicitante, m.nombre AS materia, "
        "compa.matricula AS matricula, compa.nombre AS nombre, compa.semestre AS semestre, "
        "calificacion, collect(DISTINCT col.proyecto) AS proyectos, "
        "collect(DISTINCT comun.nombre) AS materias_comunes "
        "ORDER BY calificacion DESC, compa.nombre ASC"
    )
    try:
        with driver.session(database=obtener_nombre_bd()) as sesion:
            filas = list(sesion.run(consulta, matricula=matricula, codigo=codigo))
        if not filas:
            return False, "No se encontraron asesores con calificacion >= 9 para esa materia.", None

        asesores = []
        for f in filas:
            proys = [p for p in f["proyectos"] if p]
            mats = [m for m in f["materias_comunes"] if m]
            if proys:
                relacion_previa = "Colaboraron en: " + ", ".join(proys)
            elif mats:
                relacion_previa = "Materias en comun: " + ", ".join(mats)
            else:
                relacion_previa = "Sin conexion directa previa"

            asesores.append(
                {
                    "matricula": f["matricula"],
                    "nombre": f["nombre"],
                    "semestre": f["semestre"],
                    "calificacion": f["calificacion"],
                    "relacion_previa": relacion_previa,
                }
            )
        datos = {"solicitante": filas[0]["solicitante"], "materia": filas[0]["materia"], "asesores": asesores}
        return True, "Asesores encontrados.", datos
    except Exception as error:
        return False, "Error al buscar asesores: " + str(error), None


# Consulta especializada 2: camino mas corto entre dos estudiantes con shortestPath
def buscar_camino_mas_corto(driver, origen, destino):
    origen = str(origen).strip()
    destino = str(destino).strip()
    if origen == destino:
        return False, "El origen y destino deben ser distintos.", None

    consulta = (
        "MATCH (e1:Estudiante {matricula: $origen}), (e2:Estudiante {matricula: $destino}) "
        "MATCH camino = shortestPath((e1)-[:COLABORO_CON|CURSO*1..4]-(e2)) "
        "RETURN e1.nombre AS n1, e2.nombre AS n2, length(camino) AS saltos, "
        "[n IN nodes(camino) | {tipo: labels(n)[0], nombre: n.nombre, id: coalesce(n.matricula, n.codigo)}] AS nodos, "
        "[r IN relationships(camino) | {tipo: type(r), proyecto: r.proyecto, calificacion: r.calificacion}] AS relaciones"
    )
    try:
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, origen=origen, destino=destino).single()
        if not res:
            return False, "No se encontro un camino de hasta 4 saltos entre esos estudiantes.", None

        pasos = []
        nodos = res["nodos"]
        rels = res["relaciones"]
        for i in range(len(rels)):
            rel = rels[i]
            if rel["tipo"] == "COLABORO_CON":
                detalle = "COLABORO_CON (Proyecto: " + str(rel["proyecto"]) + ")"
            else:
                detalle = "CURSO (Calificacion: " + str(rel["calificacion"]) + ")"
            pasos.append(
                {
                    "numero": i + 1,
                    "desde": nodos[i]["nombre"] + " [" + nodos[i]["id"] + "]",
                    "relacion": detalle,
                    "hacia": nodos[i + 1]["nombre"] + " [" + nodos[i + 1]["id"] + "]",
                }
            )
        datos = {
            "origen_nombre": res["n1"],
            "destino_nombre": res["n2"],
            "saltos": res["saltos"],
            "pasos": pasos,
        }
        return True, "Ruta encontrada.", datos
    except Exception as error:
        return False, "Error al buscar camino: " + str(error), None
