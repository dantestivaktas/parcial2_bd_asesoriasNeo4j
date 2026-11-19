let datosActuales = { estudiantes: [], materias: [], cursos: [], colaboraciones: [] };

// Cambiar entre las pestanas de la pagina
function mostrarSeccion(id) {
    let secciones = document.getElementsByClassName("seccion");
    for (let i = 0; i < secciones.length; i++) {
        secciones[i].style.display = secciones[i].id === id ? "block" : "none";
    }
}

// Mostrar mensaje de confirmacion o error arriba
function mostrarMensaje(texto, esError) {
    let div = document.getElementById("mensaje");
    div.textContent = texto;
    div.className = esError ? "mensaje error" : "mensaje";
    div.style.display = "block";
}

// Llenar las listas desplegables de estudiantes y materias
function llenarSelectores() {
    let idsEst = [
        "hist-mat", "ase-mat", "cam-origen", "cam-destino", "cur-mat",
        "col-m1", "col-m2", "act-est-mat", "act-cur-mat", "del-cur-mat", "del-est-mat"
    ];
    let idsMat = ["ase-cod", "cur-cod", "act-cur-cod", "del-cur-cod"];

    for (let i = 0; i < idsEst.length; i++) {
        let sel = document.getElementById(idsEst[i]);
        sel.innerHTML = "";
        for (let j = 0; j < datosActuales.estudiantes.length; j++) {
            let e = datosActuales.estudiantes[j];
            sel.innerHTML += '<option value="' + e.matricula + '">' + e.matricula + " - " + e.nombre + "</option>";
        }
    }

    for (let i = 0; i < idsMat.length; i++) {
        let sel = document.getElementById(idsMat[i]);
        sel.innerHTML = "";
        for (let j = 0; j < datosActuales.materias.length; j++) {
            let m = datosActuales.materias[j];
            sel.innerHTML += '<option value="' + m.codigo + '">' + m.codigo + " - " + m.nombre + "</option>";
        }
    }
}

// Llenar las 4 tablas HTML principales
function llenarTablas() {
    let tEst = document.getElementById("tabla-estudiantes");
    tEst.innerHTML = "";
    for (let i = 0; i < datosActuales.estudiantes.length; i++) {
        let e = datosActuales.estudiantes[i];
        tEst.innerHTML += "<tr><td>" + e.matricula + "</td><td>" + e.nombre + "</td><td>" + e.carrera + "</td><td>" + e.semestre + "</td></tr>";
    }

    let tMat = document.getElementById("tabla-materias");
    tMat.innerHTML = "";
    for (let i = 0; i < datosActuales.materias.length; i++) {
        let m = datosActuales.materias[i];
        tMat.innerHTML += "<tr><td>" + m.codigo + "</td><td>" + m.nombre + "</td></tr>";
    }

    let tCur = document.getElementById("tabla-cursos");
    tCur.innerHTML = "";
    for (let i = 0; i < datosActuales.cursos.length; i++) {
        let c = datosActuales.cursos[i];
        tCur.innerHTML += "<tr><td>" + c.estudiante + " (" + c.matricula + ")</td><td>" + c.materia + " (" + c.codigo + ")</td><td>" + c.calificacion + "</td><td>" + c.periodo + "</td></tr>";
    }

    let tCol = document.getElementById("tabla-colaboraciones");
    tCol.innerHTML = "";
    for (let i = 0; i < datosActuales.colaboraciones.length; i++) {
        let col = datosActuales.colaboraciones[i];
        tCol.innerHTML += "<tr><td>" + col.estudiante1 + " (" + col.matricula1 + ")</td><td>" + col.estudiante2 + " (" + col.matricula2 + ")</td><td>" + col.proyecto + "</td></tr>";
    }
}

// Consultar datos actuales desde Flask
async function cargarDatos() {
    let resp = await fetch("/api/datos");
    let datos = await resp.json();
    if (!datos.ok) {
        mostrarMensaje(datos.mensaje, true);
        return;
    }
    datosActuales = datos;
    document.getElementById("estado").textContent = (
        "Conectado a Neo4j AuraDB (" + datos.estudiantes.length + " estudiantes, " + datos.materias.length + " materias)"
    );
    llenarSelectores();
    llenarTablas();
}

// Reiniciar datos iniciales con seed.py
async function reiniciarSeed() {
    if (!confirm("Reiniciar la base en Neo4j AuraDB con los datos iniciales?")) return;
    let resp = await fetch("/api/seed", { method: "POST" });
    let datos = await resp.json();
    mostrarMensaje(datos.mensaje, !datos.ok);
    cargarDatos();
}

// Ver historial de un estudiante
async function verHistorial(e) {
    e.preventDefault();
    let mat = document.getElementById("hist-mat").value;
    let resp = await fetch("/api/estudiantes/" + mat + "/historial");
    let res = await resp.json();
    let div = document.getElementById("res-historial");
    if (!res.ok) {
        div.textContent = res.mensaje;
        return;
    }
    let est = res.datos.estudiante;
    let html = "<p><b>" + est.nombre + "</b> (" + est.matricula + ") - " + est.carrera + " - Semestre " + est.semestre + "</p>";
    html += "<b>Materias cursadas (:CURSO):</b><ul>";
    for (let i = 0; i < res.datos.cursos.length; i++) {
        let c = res.datos.cursos[i];
        html += "<li>" + c.codigo + " - " + c.materia + " | Calificacion: " + c.calificacion + " | Periodo: " + c.periodo + "</li>";
    }
    html += "</ul><b>Colaboraciones (:COLABORO_CON):</b><ul>";
    for (let i = 0; i < res.datos.colaboraciones.length; i++) {
        let col = res.datos.colaboraciones[i];
        html += "<li>" + col.nombre + " (" + col.matricula + ") | Proyecto: " + col.proyecto + "</li>";
    }
    div.innerHTML = html + "</ul>";
}

// Consulta especializada 1: recomendar asesores
async function buscarAsesores(e) {
    e.preventDefault();
    let mat = document.getElementById("ase-mat").value;
    let cod = document.getElementById("ase-cod").value;
    let resp = await fetch("/api/asesores?matricula=" + mat + "&codigo=" + cod);
    let res = await resp.json();
    let div = document.getElementById("res-asesores");
    if (!res.ok) {
        div.textContent = res.mensaje;
        return;
    }
    let html = "<p><b>Asesores recomendados para " + res.datos.materia + ":</b></p>";
    html += "<table><thead><tr><th>Estudiante</th><th>Sem.</th><th>Calif.</th><th>Conexion Previa</th></tr></thead><tbody>";
    for (let i = 0; i < res.datos.asesores.length; i++) {
        let a = res.datos.asesores[i];
        html += "<tr><td>" + a.nombre + " (" + a.matricula + ")</td><td>" + a.semestre + "</td><td>" + a.calificacion + "</td><td>" + a.relacion_previa + "</td></tr>";
    }
    div.innerHTML = html + "</tbody></table>";
}

// Consulta especializada 2: camino mas corto con shortestPath
async function buscarCamino(e) {
    e.preventDefault();
    let origen = document.getElementById("cam-origen").value;
    let destino = document.getElementById("cam-destino").value;
    let resp = await fetch("/api/camino?origen=" + origen + "&destino=" + destino);
    let res = await resp.json();
    let div = document.getElementById("res-camino");
    if (!res.ok) {
        div.textContent = res.mensaje;
        return;
    }
    let html = "<p><b>Ruta de " + res.datos.origen_nombre + " a " + res.datos.destino_nombre + " (" + res.datos.saltos + " saltos):</b></p>";
    html += "<table><thead><tr><th>Paso</th><th>Origen</th><th>Relacion</th><th>Destino</th></tr></thead><tbody>";
    for (let i = 0; i < res.datos.pasos.length; i++) {
        let p = res.datos.pasos[i];
        html += "<tr><td>" + p.numero + "</td><td>" + p.desde + "</td><td>" + p.relacion + "</td><td>" + p.hacia + "</td></tr>";
    }
    div.innerHTML = html + "</tbody></table>";
}

// Funcion auxiliar para enviar peticiones JSON a Flask
async function enviarJson(url, metodo, cuerpo) {
    let resp = await fetch(url, {
        method: metodo,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cuerpo)
    });
    let datos = await resp.json();
    mostrarMensaje(datos.mensaje, !datos.ok);
    cargarDatos();
}

function guardarEstudiante(e) {
    e.preventDefault();
    enviarJson("/api/estudiantes", "POST", {
        matricula: document.getElementById("est-mat").value,
        nombre: document.getElementById("est-nom").value,
        carrera: document.getElementById("est-car").value,
        semestre: document.getElementById("est-sem").value
    });
}

function guardarMateria(e) {
    e.preventDefault();
    enviarJson("/api/materias", "POST", {
        codigo: document.getElementById("mat-cod").value,
        nombre: document.getElementById("mat-nom").value
    });
}

function registrarCurso(e) {
    e.preventDefault();
    enviarJson("/api/cursos", "POST", {
        matricula: document.getElementById("cur-mat").value,
        codigo: document.getElementById("cur-cod").value,
        calificacion: document.getElementById("cur-cal").value,
        periodo: document.getElementById("cur-per").value
    });
}

function registrarColab(e) {
    e.preventDefault();
    enviarJson("/api/colaboraciones", "POST", {
        matricula1: document.getElementById("col-m1").value,
        matricula2: document.getElementById("col-m2").value,
        proyecto: document.getElementById("col-proy").value
    });
}

function eliminarColab() {
    enviarJson("/api/colaboraciones", "DELETE", {
        matricula1: document.getElementById("col-m1").value,
        matricula2: document.getElementById("col-m2").value,
        proyecto: document.getElementById("col-proy").value
    });
}

function actualizarSemestre(e) {
    e.preventDefault();
    let mat = document.getElementById("act-est-mat").value;
    enviarJson("/api/estudiantes/" + mat + "/semestre", "PUT", {
        semestre: document.getElementById("act-est-sem").value
    });
}

function actualizarCalif(e) {
    e.preventDefault();
    enviarJson("/api/cursos", "PUT", {
        matricula: document.getElementById("act-cur-mat").value,
        codigo: document.getElementById("act-cur-cod").value,
        periodo: document.getElementById("act-cur-per").value,
        calificacion: document.getElementById("act-cur-cal").value
    });
}

function bajaCurso(e) {
    e.preventDefault();
    enviarJson("/api/cursos", "DELETE", {
        matricula: document.getElementById("del-cur-mat").value,
        codigo: document.getElementById("del-cur-cod").value,
        periodo: document.getElementById("del-cur-per").value
    });
}

function borrarEstudiante(e) {
    e.preventDefault();
    let mat = document.getElementById("del-est-mat").value;
    if (!confirm("Eliminar estudiante " + mat + " y todas sus relaciones?")) return;
    enviarJson("/api/estudiantes/" + mat, "DELETE", {});
}

window.onload = cargarDatos;
