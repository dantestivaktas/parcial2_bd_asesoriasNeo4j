let datosActuales = { estudiantes: [], materias: [], cursos: [], colaboraciones: [] };

// Cambiar entre las pestanas de la interfaz
function mostrarSeccion(id) {
    let secciones = document.getElementsByClassName("seccion");
    for (let i = 0; i < secciones.length; i++) {
        secciones[i].style.display = secciones[i].id === id ? "block" : "none";
    }
    let botones = document.getElementsByClassName("tab-btn");
    for (let i = 0; i < botones.length; i++) {
        botones[i].classList.remove("activo");
    }
    let btnActivo = document.getElementById("tab-" + id);
    if (btnActivo) {
        btnActivo.classList.add("activo");
    }
}

// Mostrar mensaje de confirmacion o error arriba
function mostrarMensaje(texto, esError) {
    let div = document.getElementById("mensaje");
    div.textContent = texto;
    div.className = esError ? "alerta error" : "alerta";
    div.style.display = "block";
}

// Etiqueta de color para la calificacion
function badgeCalif(valor) {
    let clase = "grade-low";
    if (valor >= 9) clase = "grade-high";
    else if (valor >= 7) clase = "grade-mid";
    return '<span class="grade-pill ' + clase + '">' + valor + "</span>";
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
        let prev = sel.value;
        sel.innerHTML = "";
        for (let j = 0; j < datosActuales.estudiantes.length; j++) {
            let e = datosActuales.estudiantes[j];
            sel.innerHTML += '<option value="' + e.matricula + '">' + e.matricula + " - " + e.nombre + "</option>";
        }
        if (prev) sel.value = prev;
    }

    for (let i = 0; i < idsMat.length; i++) {
        let sel = document.getElementById(idsMat[i]);
        let prev = sel.value;
        sel.innerHTML = "";
        for (let j = 0; j < datosActuales.materias.length; j++) {
            let m = datosActuales.materias[j];
            sel.innerHTML += '<option value="' + m.codigo + '">' + m.codigo + " - " + m.nombre + "</option>";
        }
        if (prev) sel.value = prev;
    }
}

// Llenar las 4 tablas HTML principales y los contadores
function llenarTablas() {
    document.getElementById("cnt-est").textContent = datosActuales.estudiantes.length;
    document.getElementById("cnt-mat").textContent = datosActuales.materias.length;
    document.getElementById("cnt-cur").textContent = datosActuales.cursos.length;
    document.getElementById("cnt-col").textContent = datosActuales.colaboraciones.length;

    let tEst = document.getElementById("tabla-estudiantes");
    tEst.innerHTML = "";
    for (let i = 0; i < datosActuales.estudiantes.length; i++) {
        let e = datosActuales.estudiantes[i];
        tEst.innerHTML +=
            '<tr><td><span class="code-chip">' + e.matricula + "</span></td>" +
            "<td><b>" + e.nombre + "</b></td>" +
            "<td>" + e.carrera + "</td>" +
            "<td>" + e.semestre + "</td></tr>";
    }

    let tMat = document.getElementById("tabla-materias");
    tMat.innerHTML = "";
    for (let i = 0; i < datosActuales.materias.length; i++) {
        let m = datosActuales.materias[i];
        tMat.innerHTML +=
            '<tr><td><span class="code-chip">' + m.codigo + "</span></td>" +
            "<td><b>" + m.nombre + "</b></td></tr>";
    }

    let tCur = document.getElementById("tabla-cursos");
    tCur.innerHTML = "";
    for (let i = 0; i < datosActuales.cursos.length; i++) {
        let c = datosActuales.cursos[i];
        tCur.innerHTML +=
            "<tr><td>" + c.estudiante + ' <span class="code-chip">' + c.matricula + "</span></td>" +
            "<td>" + c.materia + ' <span class="code-chip">' + c.codigo + "</span></td>" +
            "<td>" + badgeCalif(c.calificacion) + "</td>" +
            "<td>" + c.periodo + "</td></tr>";
    }

    let tCol = document.getElementById("tabla-colaboraciones");
    tCol.innerHTML = "";
    for (let i = 0; i < datosActuales.colaboraciones.length; i++) {
        let col = datosActuales.colaboraciones[i];
        tCol.innerHTML +=
            "<tr><td>" + col.estudiante1 + "</td>" +
            "<td>" + col.estudiante2 + "</td>" +
            '<td><span class="badge badge-purple">' + col.proyecto + "</span></td></tr>";
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
    document.getElementById("estado").textContent = "Neo4j AuraDB conectado";
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
        div.innerHTML = '<div class="res-empty">' + res.mensaje + "</div>";
        return;
    }
    let est = res.datos.estudiante;
    let html = '<div class="res-box">';
    html += '<p class="res-title">' + est.nombre + ' <span class="code-chip">' + est.matricula + "</span> &mdash; " + est.carrera + " (Semestre " + est.semestre + ")</p>";
    html += '<div class="hist-grid"><div><b>Materias cursadas (:CURSO)</b><ul class="hist-list">';
    if (res.datos.cursos.length === 0) {
        html += "<li>Sin cursos registrados</li>";
    }
    for (let i = 0; i < res.datos.cursos.length; i++) {
        let c = res.datos.cursos[i];
        html += "<li><b>" + c.codigo + "</b> " + c.materia + " &middot; Calif: " + badgeCalif(c.calificacion) + " (" + c.periodo + ")</li>";
    }
    html += '</ul></div><div><b>Colaboraciones (:COLABORO_CON)</b><ul class="hist-list">';
    if (res.datos.colaboraciones.length === 0) {
        html += "<li>Sin colaboraciones registradas</li>";
    }
    for (let i = 0; i < res.datos.colaboraciones.length; i++) {
        let col = res.datos.colaboraciones[i];
        html += "<li><b>" + col.nombre + "</b> (" + col.matricula + ') &middot; <span class="badge badge-purple">' + col.proyecto + "</span></li>";
    }
    html += "</ul></div></div></div>";
    div.innerHTML = html;
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
        div.innerHTML = '<div class="res-empty">' + res.mensaje + "</div>";
        return;
    }
    let html = '<div class="res-box"><p class="res-title">Asesores recomendados para ' + res.datos.materia + "</p>";
    html += '<div class="table-wrap"><table><thead><tr><th>Estudiante</th><th>Sem.</th><th>Calif.</th><th>Conexion Previa</th></tr></thead><tbody>';
    for (let i = 0; i < res.datos.asesores.length; i++) {
        let a = res.datos.asesores[i];
        html +=
            "<tr><td><b>" + a.nombre + '</b> <span class="code-chip">' + a.matricula + "</span></td>" +
            "<td>" + a.semestre + "</td>" +
            "<td>" + badgeCalif(a.calificacion) + "</td>" +
            "<td>" + a.relacion_previa + "</td></tr>";
    }
    html += "</tbody></table></div></div>";
    div.innerHTML = html;
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
        div.innerHTML = '<div class="res-empty">' + res.mensaje + "</div>";
        return;
    }
    let html = '<div class="res-box"><p class="res-title">Ruta de ' + res.datos.origen_nombre + " a " + res.datos.destino_nombre + " (" + res.datos.saltos + " saltos)</p>";
    html += '<div class="pasos-lista">';
    for (let i = 0; i < res.datos.pasos.length; i++) {
        let p = res.datos.pasos[i];
        html +=
            '<div class="paso-item">' +
            '<span class="paso-num">Paso ' + p.numero + "</span>" +
            '<span class="paso-nodo">' + p.desde + "</span>" +
            '<span class="paso-rel">' + p.relacion + "</span>" +
            '<span class="paso-nodo">' + p.hacia + "</span>" +
            "</div>";
    }
    html += "</div></div>";
    div.innerHTML = html;
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
