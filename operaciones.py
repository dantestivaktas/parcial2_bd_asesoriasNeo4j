from neo4j.exceptions import ConstraintError
from conexion import obtener_nombre_bd


# Crear un estudiante nuevo sin sobrescribir registros existentes
def crear_estudiante(driver, matricula, nombre, carrera, semestre):
    matricula = str(matricula).strip()
    nombre = str(nombre).strip()
    carrera = str(carrera).strip()
    if not matricula or not nombre or not carrera:
        return False, "Matricula, nombre y carrera son obligatorios."

    try:
        semestre = int(semestre)
        consulta = (
            "CREATE (e:Estudiante {matricula: $matricula, nombre: $nombre, carrera: $carrera, semestre: $semestre}) "
            "RETURN e.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, matricula=matricula, nombre=nombre, carrera=carrera, semestre=semestre).single()
        return True, "Estudiante creado: " + res["nombre"] + " (" + matricula + ")"
    except ConstraintError:
        return False, "Ya existe un estudiante con la matricula " + matricula + "."
    except Exception as error:
        return False, "Error al crear estudiante: " + str(error)


# Actualizar datos de un estudiante existente
def actualizar_estudiante(driver, matricula, nombre, carrera, semestre):
    matricula = str(matricula).strip()
    nombre = str(nombre).strip()
    carrera = str(carrera).strip()
    if not matricula or not nombre or not carrera:
        return False, "Matricula, nombre y carrera son obligatorios."

    try:
        semestre = int(semestre)
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula}) "
            "SET e.nombre = $nombre, e.carrera = $carrera, e.semestre = $semestre "
            "RETURN e.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, matricula=matricula, nombre=nombre, carrera=carrera, semestre=semestre).single()
        if not res:
            return False, "No se encontro el estudiante."
        return True, "Estudiante actualizado: " + res["nombre"] + " (" + matricula + ")"
    except Exception as error:
        return False, "Error al actualizar estudiante: " + str(error)


# Crear una materia nueva sin sobrescribir registros existentes
def crear_materia(driver, codigo, nombre, area):
    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()
    area = str(area).strip()
    if not codigo or not nombre or not area:
        return False, "Codigo, nombre y area son obligatorios."

    try:
        consulta = (
            "CREATE (m:Materia {codigo: $codigo, nombre: $nombre, area: $area}) "
            "RETURN m.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, codigo=codigo, nombre=nombre, area=area).single()
        return True, "Materia creada: " + codigo + " - " + res["nombre"]
    except ConstraintError:
        return False, "Ya existe una materia con el codigo " + codigo + "."
    except Exception as error:
        return False, "Error al crear materia: " + str(error)


# Actualizar datos de una materia existente
def actualizar_materia(driver, codigo, nombre, area):
    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()
    area = str(area).strip()
    if not codigo or not nombre or not area:
        return False, "Codigo, nombre y area son obligatorios."

    try:
        consulta = (
            "MATCH (m:Materia {codigo: $codigo}) "
            "SET m.nombre = $nombre, m.area = $area "
            "RETURN m.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, codigo=codigo, nombre=nombre, area=area).single()
        if not res:
            return False, "No se encontro la materia."
        return True, "Materia actualizada: " + codigo + " - " + res["nombre"]
    except Exception as error:
        return False, "Error al actualizar materia: " + str(error)


# Registrar materia cursada diferenciada por periodo para no borrar intentos previos
def registrar_curso(driver, matricula, codigo, calificacion, periodo):
    matricula = str(matricula).strip()
    codigo = str(codigo).strip().upper()
    periodo = str(periodo).strip()
    if not matricula or not codigo or not periodo:
        return False, "Matricula, codigo y periodo son obligatorios."

    try:
        calificacion = int(calificacion)
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


# Registrar colaboracion en proyecto sin sobrescribir proyectos anteriores
def registrar_colaboracion(driver, matricula1, matricula2, proyecto):
    m1 = str(matricula1).strip()
    m2 = str(matricula2).strip()
    proyecto = str(proyecto).strip()
    if not m1 or not m2 or not proyecto:
        return False, "Matriculas y proyecto son obligatorios."
    if m1 == m2:
        return False, "Los estudiantes deben ser diferentes."

    # Ordenar matriculas y usar MERGE sin direccion para evitar duplicados inversos
    if m1 > m2:
        m1, m2 = m2, m1

    try:
        consulta = (
            "MATCH (e1:Estudiante {matricula: $m1}), (e2:Estudiante {matricula: $m2}) "
            "MERGE (e1)-[:COLABORO_CON {proyecto: $proyecto}]-(e2) "
            "RETURN e1.nombre AS n1, e2.nombre AS n2"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, m1=m1, m2=m2, proyecto=proyecto).single()
        if not res:
            return False, "No se encontraron ambos estudiantes."
        return True, "Colaboracion guardada entre " + res["n1"] + " y " + res["n2"] + " (" + proyecto + ")"
    except Exception as error:
        return False, "Error al registrar colaboracion: " + str(error)


# Obtener lista de todos los estudiantes
def listar_estudiantes(driver):
    consulta = (
        "MATCH (e:Estudiante) "
        "RETURN e.matricula AS matricula, e.nombre AS nombre, e.carrera AS carrera, e.semestre AS semestre "
        "ORDER BY e.matricula"
    )
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return [dict(r) for r in sesion.run(consulta)]


# Obtener lista de todas las materias
def listar_materias(driver):
    consulta = "MATCH (m:Materia) RETURN m.codigo AS codigo, m.nombre AS nombre, m.area AS area ORDER BY m.codigo"
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return [dict(r) for r in sesion.run(consulta)]


# Consultar datos, materias cursadas y colaboradores de un estudiante
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
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula}) "
            "SET e.semestre = $semestre RETURN e.nombre AS nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, matricula=matricula, semestre=nuevo_semestre).single()
        if not res:
            return False, "No se encontro el estudiante."
        return True, "Semestre actualizado para " + res["nombre"] + " a " + str(nuevo_semestre)
    except Exception as error:
        return False, "Error al actualizar semestre: " + str(error)


# Actualizar calificacion de un curso (opcionalmente filtrando por periodo)
def actualizar_calificacion(driver, matricula, codigo, nueva_calificacion, periodo=""):
    matricula = str(matricula).strip()
    codigo = str(codigo).strip().upper()
    periodo = str(periodo).strip()

    try:
        nueva_calificacion = int(nueva_calificacion)
        filtro = " {periodo: $periodo}" if periodo else ""
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula})-[r:CURSO" + filtro + "]->(m:Materia {codigo: $codigo}) "
            "SET r.calificacion = $calificacion RETURN e.nombre AS nombre, m.nombre AS materia"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = list(
                sesion.run(
                    consulta, matricula=matricula, codigo=codigo, calificacion=nueva_calificacion, periodo=periodo
                )
            )
        if not res:
            return False, "No se encontro el curso para ese estudiante."
        return True, "Calificacion actualizada a " + str(nueva_calificacion) + " en " + res[0]["materia"]
    except Exception as error:
        return False, "Error al actualizar calificacion: " + str(error)


# Eliminar un estudiante y todas sus relaciones con DETACH DELETE
def eliminar_estudiante(driver, matricula):
    matricula = str(matricula).strip()
    try:
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula}) "
            "WITH e, e.nombre AS nombre DETACH DELETE e RETURN nombre"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, matricula=matricula).single()
        if not res:
            return False, "No se encontro el estudiante."
        return True, "Estudiante eliminado: " + res["nombre"]
    except Exception as error:
        return False, "Error al eliminar estudiante: " + str(error)


# Dar de baja solo la relacion :CURSO sin borrar los nodos
def eliminar_curso(driver, matricula, codigo, periodo=""):
    matricula = str(matricula).strip()
    codigo = str(codigo).strip().upper()
    periodo = str(periodo).strip()

    try:
        filtro = " {periodo: $periodo}" if periodo else ""
        consulta = (
            "MATCH (e:Estudiante {matricula: $matricula})-[r:CURSO" + filtro + "]->(m:Materia {codigo: $codigo}) "
            "DELETE r RETURN e.nombre AS est, m.nombre AS mat"
        )
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = list(sesion.run(consulta, matricula=matricula, codigo=codigo, periodo=periodo))
        if not res:
            return False, "No se encontro ese curso registrado."
        return True, "Curso dado de baja: " + res[0]["mat"] + " para " + res[0]["est"]
    except Exception as error:
        return False, "Error al dar de baja curso: " + str(error)


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
                estado = "Conocido directo (" + ", ".join(proys) + ")"
            elif mats:
                estado = "Companero de materia (" + ", ".join(mats) + ")"
            else:
                estado = "Sin conexion previa"

            asesores.append(
                {
                    "matricula": f["matricula"],
                    "nombre": f["nombre"],
                    "semestre": f["semestre"],
                    "calificacion": f["calificacion"],
                    "estado": estado,
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
        "MATCH camino = shortestPath((e1)-[:COLABORO_CON|CURSO*1..6]-(e2)) "
        "RETURN e1.nombre AS n1, e2.nombre AS n2, length(camino) AS saltos, "
        "[n IN nodes(camino) | {tipo: labels(n)[0], nombre: n.nombre, id: coalesce(n.matricula, n.codigo)}] AS nodos, "
        "[r IN relationships(camino) | {tipo: type(r), proyecto: r.proyecto, calificacion: r.calificacion}] AS relaciones"
    )
    try:
        with driver.session(database=obtener_nombre_bd()) as sesion:
            res = sesion.run(consulta, origen=origen, destino=destino).single()
        if not res:
            return False, "No se encontro una ruta entre esos estudiantes.", None

        pasos = []
        nodos = res["nodos"]
        rels = res["relaciones"]
        for i in range(len(rels)):
            rel = rels[i]
            texto_rel = rel["proyecto"] if rel["tipo"] == "COLABORO_CON" else "CURSO calif " + str(rel["calificacion"])
            pasos.append(
                {
                    "numero": i + 1,
                    "desde_id": nodos[i]["id"],
                    "desde_nombre": nodos[i]["nombre"],
                    "relacion": rel["tipo"] + " (" + str(texto_rel) + ")",
                    "hacia_id": nodos[i + 1]["id"],
                    "hacia_nombre": nodos[i + 1]["nombre"],
                }
            )
        datos = {
            "origen_nombre": res["n1"],
            "destino_nombre": res["n2"],
            "saltos": res["saltos"],
            "nodos_ids": [n["id"] for n in nodos],
            "pasos": pasos,
        }
        return True, "Ruta encontrada.", datos
    except Exception as error:
        return False, "Error al buscar camino: " + str(error), None


# Obtener nodos y relaciones actuales para dibujar el grafo en la pagina web
def obtener_grafo(driver):
    consulta_nodos = (
        "MATCH (n) RETURN labels(n)[0] AS tipo, coalesce(n.matricula, n.codigo) AS id, "
        "n.nombre AS nombre, n.semestre AS semestre, n.area AS area ORDER BY tipo, id"
    )
    consulta_rels = (
        "MATCH (a)-[r]->(b) RETURN coalesce(a.matricula, a.codigo) AS origen, "
        "coalesce(b.matricula, b.codigo) AS destino, type(r) AS tipo, "
        "r.calificacion AS calificacion, r.periodo AS periodo, r.proyecto AS proyecto"
    )
    with driver.session(database=obtener_nombre_bd()) as sesion:
        nodos = [dict(n) for n in sesion.run(consulta_nodos)]
        relaciones = [dict(r) for r in sesion.run(consulta_rels)]
    return nodos, relaciones
