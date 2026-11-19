from neo4j.exceptions import ConstraintError
from conexion import obtener_nombre_bd


# Ejecutar operaciones en la nube mediante transacciones gestionadas con reintentos
def _ejecutar_lectura(driver, fn, *args):
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return sesion.execute_read(fn, *args)


def _ejecutar_escritura(driver, fn, *args):
    with driver.session(database=obtener_nombre_bd()) as sesion:
        return sesion.execute_write(fn, *args)


# Crear un estudiante nuevo ligado a su nodo :Carrera
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

        def _tx(tx, m, n, c, s):
            return tx.run(
                "MERGE (car:Carrera {nombre: $carrera}) "
                "CREATE (e:Estudiante {matricula: $matricula, nombre: $nombre, semestre: $semestre}) "
                "MERGE (e)-[:PERTENECE_A]->(car) "
                "RETURN e.nombre AS nombre",
                matricula=m, nombre=n, carrera=c, semestre=s,
            ).single()

        res = _ejecutar_escritura(driver, _tx, matricula, nombre, carrera, semestre)
        return True, "Estudiante creado: " + res["nombre"] + " (" + matricula + ")"
    except ConstraintError:
        return False, "Ya existe un estudiante con la matricula " + matricula + "."
    except Exception as error:
        return False, "Error al crear estudiante: " + str(error)


# Actualizar datos de un estudiante existente y su relacion :PERTENECE_A
def actualizar_estudiante(driver, matricula, nombre, carrera, semestre):
    matricula = str(matricula).strip()
    nombre = str(nombre).strip()
    carrera = str(carrera).strip()
    if not matricula or not nombre or not carrera:
        return False, "Matricula, nombre y carrera son obligatorios."

    try:
        semestre = int(semestre)
        if semestre < 1 or semestre > 12:
            return False, "El semestre debe estar entre 1 y 12."

        def _tx(tx, m, n, c, s):
            return tx.run(
                "MATCH (e:Estudiante {matricula: $matricula}) "
                "SET e.nombre = $nombre, e.semestre = $semestre "
                "WITH e "
                "OPTIONAL MATCH (e)-[vieja:PERTENECE_A]->(:Carrera) "
                "DELETE vieja "
                "WITH e "
                "MERGE (car:Carrera {nombre: $carrera}) "
                "MERGE (e)-[:PERTENECE_A]->(car) "
                "RETURN e.nombre AS nombre",
                matricula=m, nombre=n, carrera=c, semestre=s,
            ).single()

        res = _ejecutar_escritura(driver, _tx, matricula, nombre, carrera, semestre)
        if not res:
            return False, "No se encontro el estudiante."
        return True, "Estudiante actualizado: " + res["nombre"] + " (" + matricula + ")"
    except Exception as error:
        return False, "Error al actualizar estudiante: " + str(error)


# Crear una materia nueva ligada a su nodo :Area
def crear_materia(driver, codigo, nombre, area):
    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()
    area = str(area).strip()
    if not codigo or not nombre or not area:
        return False, "Codigo, nombre y area son obligatorios."

    try:
        def _tx(tx, cod, nom, ar):
            return tx.run(
                "MERGE (a:Area {nombre: $area}) "
                "CREATE (m:Materia {codigo: $codigo, nombre: $nombre}) "
                "MERGE (m)-[:PERTENECE_AL_AREA]->(a) "
                "RETURN m.nombre AS nombre",
                codigo=cod, nombre=nom, area=ar,
            ).single()

        res = _ejecutar_escritura(driver, _tx, codigo, nombre, area)
        return True, "Materia creada: " + codigo + " - " + res["nombre"]
    except ConstraintError:
        return False, "Ya existe una materia con el codigo " + codigo + "."
    except Exception as error:
        return False, "Error al crear materia: " + str(error)


# Actualizar datos de una materia existente y su relacion :PERTENECE_AL_AREA
def actualizar_materia(driver, codigo, nombre, area):
    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()
    area = str(area).strip()
    if not codigo or not nombre or not area:
        return False, "Codigo, nombre y area son obligatorios."

    try:
        def _tx(tx, cod, nom, ar):
            return tx.run(
                "MATCH (m:Materia {codigo: $codigo}) "
                "SET m.nombre = $nombre "
                "WITH m "
                "OPTIONAL MATCH (m)-[vieja:PERTENECE_AL_AREA]->(:Area) "
                "DELETE vieja "
                "WITH m "
                "MERGE (a:Area {nombre: $area}) "
                "MERGE (m)-[:PERTENECE_AL_AREA]->(a) "
                "RETURN m.nombre AS nombre",
                codigo=cod, nombre=nom, area=ar,
            ).single()

        res = _ejecutar_escritura(driver, _tx, codigo, nombre, area)
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
        if calificacion < 0 or calificacion > 10:
            return False, "La calificacion debe estar entre 0 y 10."

        def _tx(tx, mat, cod, cal, per):
            return tx.run(
                "MATCH (e:Estudiante {matricula: $matricula}), (m:Materia {codigo: $codigo}) "
                "MERGE (e)-[r:CURSO {periodo: $periodo}]->(m) "
                "SET r.calificacion = $calificacion "
                "RETURN e.nombre AS est, m.nombre AS mat",
                matricula=mat, codigo=cod, calificacion=cal, periodo=per,
            ).single()

        res = _ejecutar_escritura(driver, _tx, matricula, codigo, calificacion, periodo)
        if not res:
            return False, "No se encontro el estudiante o la materia."
        return True, "Curso registrado: " + res["est"] + " en " + res["mat"] + " (" + periodo + ")"
    except Exception as error:
        return False, "Error al registrar curso: " + str(error)


# Registrar colaboracion ordenando matriculas (m1 < m2) para fijar la direccion en Neo4j
def registrar_colaboracion(driver, matricula1, matricula2, proyecto):
    m1 = str(matricula1).strip()
    m2 = str(matricula2).strip()
    proyecto = str(proyecto).strip()
    if not m1 or not m2 or not proyecto:
        return False, "Matriculas y proyecto son obligatorios."
    if m1 == m2:
        return False, "Los estudiantes deben ser diferentes."

    if m1 > m2:
        m1, m2 = m2, m1

    try:
        def _tx(tx, mat1, mat2, proy):
            return tx.run(
                "MATCH (e1:Estudiante {matricula: $m1}), (e2:Estudiante {matricula: $m2}) "
                "MERGE (e1)-[r:COLABORO_CON {proyecto: $proyecto}]->(e2) "
                "RETURN e1.nombre AS n1, e2.nombre AS n2, r.proyecto AS proyecto",
                m1=mat1, m2=mat2, proyecto=proy,
            ).single()

        res = _ejecutar_escritura(driver, _tx, m1, m2, proyecto)
        if not res:
            return False, "No se encontraron ambos estudiantes."
        return True, "Colaboracion guardada entre " + res["n1"] + " y " + res["n2"] + " (" + proyecto + ")"
    except Exception as error:
        return False, "Error al registrar colaboracion: " + str(error)


# Obtener lista de todos los estudiantes
def listar_estudiantes(driver):
    def _tx(tx):
        return [
            dict(r)
            for r in tx.run(
                "MATCH (e:Estudiante) "
                "OPTIONAL MATCH (e)-[:PERTENECE_A]->(c:Carrera) "
                "RETURN e.matricula AS matricula, e.nombre AS nombre, c.nombre AS carrera, e.semestre AS semestre "
                "ORDER BY e.matricula"
            )
        ]

    return _ejecutar_lectura(driver, _tx)


# Obtener lista de todas las materias
def listar_materias(driver):
    def _tx(tx):
        return [
            dict(r)
            for r in tx.run(
                "MATCH (m:Materia) "
                "OPTIONAL MATCH (m)-[:PERTENECE_AL_AREA]->(a:Area) "
                "RETURN m.codigo AS codigo, m.nombre AS nombre, a.nombre AS area "
                "ORDER BY m.codigo"
            )
        ]

    return _ejecutar_lectura(driver, _tx)


# Consultar datos, materias cursadas y colaboradores de un estudiante
def consultar_historial(driver, matricula):
    matricula = str(matricula).strip()
    if not matricula:
        return False, "Ingresa una matricula.", None

    def _tx(tx, m):
        est = tx.run(
            "MATCH (e:Estudiante {matricula: $m}) "
            "OPTIONAL MATCH (e)-[:PERTENECE_A]->(c:Carrera) "
            "RETURN e.matricula AS matricula, e.nombre AS nombre, c.nombre AS carrera, e.semestre AS semestre",
            m=m,
        ).single()
        if not est:
            return None

        cursos = [
            dict(r)
            for r in tx.run(
                "MATCH (e:Estudiante {matricula: $m})-[r:CURSO]->(mat:Materia) "
                "RETURN mat.codigo AS codigo, mat.nombre AS materia, r.calificacion AS calificacion, r.periodo AS periodo "
                "ORDER BY r.periodo, mat.codigo",
                m=m,
            )
        ]
        colabs = [
            dict(r)
            for r in tx.run(
                "MATCH (e:Estudiante {matricula: $m})-[r:COLABORO_CON]-(c:Estudiante) "
                "RETURN c.matricula AS matricula, c.nombre AS nombre, r.proyecto AS proyecto "
                "ORDER BY c.nombre, r.proyecto",
                m=m,
            )
        ]
        return {"estudiante": dict(est), "cursos": cursos, "colaboraciones": colabs}

    try:
        datos = _ejecutar_lectura(driver, _tx, matricula)
        if not datos:
            return False, "No se encontro el estudiante.", None
        return True, "Historial encontrado.", datos
    except Exception as error:
        return False, "Error al consultar historial: " + str(error), None


# Actualizar el semestre de un estudiante
def actualizar_semestre(driver, matricula, nuevo_semestre):
    matricula = str(matricula).strip()
    try:
        nuevo_semestre = int(nuevo_semestre)
        if nuevo_semestre < 1 or nuevo_semestre > 12:
            return False, "El semestre debe estar entre 1 y 12."

        def _tx(tx, mat, sem):
            return tx.run(
                "MATCH (e:Estudiante {matricula: $matricula}) "
                "SET e.semestre = $semestre RETURN e.nombre AS nombre",
                matricula=mat, semestre=sem,
            ).single()

        res = _ejecutar_escritura(driver, _tx, matricula, nuevo_semestre)
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
        if nueva_calificacion < 0 or nueva_calificacion > 10:
            return False, "La calificacion debe estar entre 0 y 10."
        filtro = " {periodo: $periodo}" if periodo else ""

        def _tx(tx, mat, cod, cal, per):
            consulta = (
                "MATCH (e:Estudiante {matricula: $matricula})-[r:CURSO" + filtro + "]->(m:Materia {codigo: $codigo}) "
                "SET r.calificacion = $calificacion RETURN e.nombre AS nombre, m.nombre AS materia"
            )
            return list(tx.run(consulta, matricula=mat, codigo=cod, calificacion=cal, periodo=per))

        res = _ejecutar_escritura(driver, _tx, matricula, codigo, nueva_calificacion, periodo)
        if not res:
            return False, "No se encontro el curso para ese estudiante."
        return True, "Calificacion actualizada a " + str(nueva_calificacion) + " en " + res[0]["materia"]
    except Exception as error:
        return False, "Error al actualizar calificacion: " + str(error)


# Eliminar un estudiante y todas sus relaciones con DETACH DELETE
def eliminar_estudiante(driver, matricula):
    matricula = str(matricula).strip()
    try:
        def _tx(tx, mat):
            return tx.run(
                "MATCH (e:Estudiante {matricula: $matricula}) "
                "WITH e, e.nombre AS nombre DETACH DELETE e RETURN nombre",
                matricula=mat,
            ).single()

        res = _ejecutar_escritura(driver, _tx, matricula)
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

        def _tx(tx, mat, cod, per):
            consulta = (
                "MATCH (e:Estudiante {matricula: $matricula})-[r:CURSO" + filtro + "]->(m:Materia {codigo: $codigo}) "
                "DELETE r RETURN e.nombre AS est, m.nombre AS mat"
            )
            return list(tx.run(consulta, matricula=mat, codigo=cod, periodo=per))

        res = _ejecutar_escritura(driver, _tx, matricula, codigo, periodo)
        if not res:
            return False, "No se encontro ese curso registrado."
        texto_periodo = " (Periodo: " + periodo + ")" if periodo else " (todos los periodos)"
        return True, "Se dio de baja el curso " + res[0]["mat"] + texto_periodo + " para el estudiante " + res[0]["est"]
    except Exception as error:
        return False, "Error al dar de baja curso: " + str(error)


# Eliminar una relacion :COLABORO_CON especifica entre dos estudiantes
def eliminar_colaboracion(driver, matricula1, matricula2, proyecto):
    m1 = str(matricula1).strip()
    m2 = str(matricula2).strip()
    proyecto = str(proyecto).strip()
    if not m1 or not m2 or not proyecto:
        return False, "Matriculas y proyecto son obligatorios."

    try:
        def _tx(tx, mat1, mat2, proy):
            return list(
                tx.run(
                    "MATCH (e1:Estudiante {matricula: $m1})-[r:COLABORO_CON {proyecto: $proyecto}]-(e2:Estudiante {matricula: $m2}) "
                    "DELETE r RETURN e1.nombre AS est1, e2.nombre AS est2",
                    m1=mat1, m2=mat2, proyecto=proy,
                )
            )

        res = _ejecutar_escritura(driver, _tx, m1, m2, proyecto)
        if not res:
            return False, "No se encontro esa colaboracion."
        return True, "Colaboracion eliminada entre " + res[0]["est1"] + " y " + res[0]["est2"] + " (Proyecto: " + proyecto + ")"
    except Exception as error:
        return False, "Error al eliminar colaboracion: " + str(error)


# Consulta especializada 1: recomendar asesores con calificacion >= 9
def recomendar_asesores(driver, mi_matricula, codigo):
    matricula = str(mi_matricula).strip()
    codigo = str(codigo).strip().upper()

    def _tx(tx, mat, cod):
        return list(
            tx.run(
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
                "ORDER BY calificacion DESC, compa.nombre ASC",
                matricula=mat, codigo=cod,
            )
        )

    try:
        filas = _ejecutar_lectura(driver, _tx, matricula, codigo)
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


# Consulta especializada 2: separa grafo social (:COLABORO_CON) de afinidad por materias (:CURSO)
def buscar_camino_mas_corto(driver, origen, destino, incluir_materias=False):
    origen = str(origen).strip()
    destino = str(destino).strip()
    if origen == destino:
        return False, "El origen y destino deben ser distintos.", None

    tipos = "COLABORO_CON|CURSO" if incluir_materias else "COLABORO_CON"

    def _tx(tx, orig, dest):
        consulta = (
            "MATCH (e1:Estudiante {matricula: $origen}), (e2:Estudiante {matricula: $destino}) "
            "MATCH camino = allShortestPaths((e1)-[:" + tipos + "*1..6]-(e2)) "
            "WITH e1, e2, camino, "
            "size([r IN relationships(camino) WHERE type(r) = 'COLABORO_CON']) AS colabs "
            "ORDER BY colabs DESC, [n IN nodes(camino) | coalesce(n.matricula, n.codigo)] ASC "
            "LIMIT 1 "
            "RETURN e1.nombre AS n1, e2.nombre AS n2, length(camino) AS saltos, "
            "[n IN nodes(camino) | {tipo: labels(n)[0], nombre: n.nombre, id: coalesce(n.matricula, n.codigo)}] AS nodos, "
            "[r IN relationships(camino) | {tipo: type(r), proyecto: r.proyecto, calificacion: r.calificacion}] AS relaciones"
        )
        return tx.run(consulta, origen=orig, destino=dest).single()

    try:
        res = _ejecutar_lectura(driver, _tx, origen, destino)
        if not res:
            if not incluir_materias:
                return False, "No hay ruta directa en la red social (:COLABORO_CON). Activa afinidad por materias si deseas incluir :CURSO.", None
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
    def _tx(tx):
        nodos = [
            dict(n)
            for n in tx.run(
                "MATCH (n) RETURN labels(n)[0] AS tipo, "
                "coalesce(n.matricula, n.codigo, labels(n)[0] + ':' + n.nombre) AS id, "
                "n.nombre AS nombre, n.semestre AS semestre ORDER BY tipo, id"
            )
        ]
        relaciones = [
            dict(r)
            for r in tx.run(
                "MATCH (a)-[r]->(b) "
                "RETURN coalesce(a.matricula, a.codigo, labels(a)[0] + ':' + a.nombre) AS origen, "
                "coalesce(b.matricula, b.codigo, labels(b)[0] + ':' + b.nombre) AS destino, "
                "type(r) AS tipo, r.calificacion AS calificacion, r.periodo AS periodo, r.proyecto AS proyecto"
            )
        ]
        return nodos, relaciones

    return _ejecutar_lectura(driver, _tx)
