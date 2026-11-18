let grafoActual = { nodos: [], relaciones: [], estudiantes: [], materias: [] };
let rutaNodos = [];

// Mostrar u ocultar pestanas
function mostrarSeccion(id) {
    let secciones = document.getElementsByClassName("seccion");
    for (let i = 0; i < secciones.length; i++) {
        secciones[i].style.display = secciones[i].id === id ? "block" : "none";
    }
}

// Mostrar aviso de resultado en la parte superior
function mostrarMensaje(texto, esError) {
    let div = document.getElementById("mensaje");
    div.textContent = texto;
    div.className = esError ? "mensaje error" : "mensaje";
    div.style.display = "block";
}

// Llenar todos los selectores de estudiantes y materias
function llenarSelectores() {
    let idsEst = [
        "hist-mat", "ase-mat", "cam-origen", "cam-destino", "cur-mat",
        "col-m1", "col-m2", "act-est-mat", "act-cur-mat", "del-cur-mat", "del-est-mat"
    ];
    let idsMat = ["ase-cod", "cur-cod", "act-cur-cod", "del-cur-cod"];

    for (let i = 0; i < idsEst.length; i++) {
        let sel = document.getElementById(idsEst[i]);
        sel.innerHTML = "";
        for (let j = 0; j < grafoActual.estudiantes.length; j++) {
            let e = grafoActual.estudiantes[j];
            sel.innerHTML += '<option value="' + e.matricula + '">' + e.matricula + " - " + e.nombre + "</option>";
        }
    }

    for (let i = 0; i < idsMat.length; i++) {
        let sel = document.getElementById(idsMat[i]);
        sel.innerHTML = "";
        for (let j = 0; j < grafoActual.materias.length; j++) {
            let m = grafoActual.materias[j];
            sel.innerHTML += '<option value="' + m.codigo + '">' + m.codigo + " - " + m.nombre + "</option>";
        }
    }
}

// Llenar las tablas HTML de estudiantes y materias
function llenarTablas() {
    let tEst = document.getElementById("tabla-estudiantes");
    tEst.innerHTML = "";
    for (let i = 0; i < grafoActual.estudiantes.length; i++) {
        let e = grafoActual.estudiantes[i];
        tEst.innerHTML += "<tr><td>" + e.matricula + "</td><td>" + e.nombre + "</td><td>" + e.carrera + "</td><td>" + e.semestre + "</td></tr>";
    }

    let tMat = document.getElementById("tabla-materias");
    tMat.innerHTML = "";
    for (let i = 0; i < grafoActual.materias.length; i++) {
        let m = grafoActual.materias[i];
        tMat.innerHTML += "<tr><td>" + m.codigo + "</td><td>" + m.nombre + "</td><td>" + m.area + "</td></tr>";
    }
}

// Dibujar nodos y lineas del grafo en el SVG
function dibujarGrafo() {
    let svg = document.getElementById("grafo");
    let pos = {};
    let estudiantes = [];
    let materias = [];

    for (let i = 0; i < grafoActual.nodos.length; i++) {
        if (grafoActual.nodos[i].tipo === "Estudiante") {
            estudiantes.push(grafoActual.nodos[i]);
        } else {
            materias.push(grafoActual.nodos[i]);
        }
    }

    // Repartir estudiantes arriba y abajo, y materias en medio
    let mitad = Math.ceil(estudiantes.length / 2);
    for (let i = 0; i < estudiantes.length; i++) {
        if (i < mitad) {
            pos[estudiantes[i].id] = { x: (820 / Math.max(mitad, 1)) * (i + 0.5) + 40, y: 55 };
        } else {
            let abajo = estudiantes.length - mitad;
            pos[estudiantes[i].id] = { x: (820 / Math.max(abajo, 1)) * (i - mitad + 0.5) + 40, y: 305 };
        }
    }
    for (let i = 0; i < materias.length; i++) {
        pos[materias[i].id] = { x: (820 / Math.max(materias.length, 1)) * (i + 0.5) + 40, y: 180 };
    }

    let html = "";
    for (let i = 0; i < grafoActual.relaciones.length; i++) {
        let r = grafoActual.relaciones[i];
        let p1 = pos[r.origen];
        let p2 = pos[r.destino];
        if (!p1 || !p2) continue;

        let enRuta = rutaNodos.indexOf(r.origen) !== -1 && rutaNodos.indexOf(r.destino) !== -1;
        let color = enRuta ? "#e67e22" : (r.tipo === "COLABORO_CON" ? "#2563eb" : "#16a34a");
        let grosor = enRuta ? "3" : "1.5";
        html += '<line x1="' + p1.x + '" y1="' + p1.y + '" x2="' + p2.x + '" y2="' + p2.y + '" stroke="' + color + '" stroke-width="' + grosor + '" />';
    }

    for (let i = 0; i < grafoActual.nodos.length; i++) {
        let n = grafoActual.nodos[i];
        let p = pos[n.id];
        let enRuta = rutaNodos.indexOf(n.id) !== -1;
        let fill = enRuta ? "#fdebd0" : (n.tipo === "Estudiante" ? "#dbeafe" : "#d1fae5");
        let stroke = enRuta ? "#d35400" : (n.tipo === "Estudiante" ? "#1d4ed8" : "#047857");

        html += '<rect x="' + (p.x - 62) + '" y="' + (p.y - 22) + '" width="124" height="44" rx="6" fill="' + fill + '" stroke="' + stroke + '" stroke-width="2" />';
        html += '<text x="' + p.x + '" y="' + (p.y - 3) + '" text-anchor="middle" font-size="11" font-weight="bold">' + n.nombre.slice(0, 17) + "</text>";
        html += '<text x="' + p.x + '" y="' + (p.y + 12) + '" text-anchor="middle" font-size="10">' + n.id + "</text>";
    }

    svg.innerHTML = html;
}

// Pedir el grafo actualizado al servidor Flask
async function cargarGrafo() {
    let resp = await fetch("/api/grafo");
    let datos = await resp.json();
    if (!datos.ok) {
        mostrarMensaje(datos.mensaje, true);
        return;
    }
    grafoActual = datos;
    document.getElementById("estado").textContent = "Conectado (" + datos.nodos.length + " nodos)";
    llenarSelectores();
    llenarTablas();
    dibujarGrafo();
}

async function reiniciarSeed() {
    if (!confirm("Reiniciar la base con los datos iniciales?")) return;
    let resp = await fetch("/api/seed", { method: "POST" });
    let datos = await resp.json();
    rutaNodos = [];
    mostrarMensaje(datos.mensaje, !datos.ok);
    cargarGrafo();
}

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
    let html = "<p><b>" + est.nombre + "</b> (" + est.matricula + ") - Semestre " + est.semestre + "</p><b>Cursos:</b><ul>";
    for (let i = 0; i < res.datos.cursos.length; i++) {
        let c = res.datos.cursos[i];
        html += "<li>" + c.codigo + " " + c.materia + " | Calif: " + c.calificacion + " | Periodo: " + c.periodo + "</li>";
    }
    html += "</ul><b>Colaboraciones:</b><ul>";
    for (let i = 0; i < res.datos.colaboraciones.length; i++) {
        let col = res.datos.colaboraciones[i];
        html += "<li>" + col.nombre + " (" + col.matricula + ") - Proyecto: " + col.proyecto + "</li>";
    }
    div.innerHTML = html + "</ul>";
}

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
    let html = "<p><b>Asesores para " + res.datos.materia + ":</b></p><ul>";
    for (let i = 0; i < res.datos.asesores.length; i++) {
        let a = res.datos.asesores[i];
        html += "<li>" + a.nombre + " (" + a.matricula + ") | Calif: " + a.calificacion + " | " + a.estado + "</li>";
    }
    div.innerHTML = html + "</ul>";
}

async function buscarCamino(e) {
    e.preventDefault();
    let origen = document.getElementById("cam-origen").value;
    let destino = document.getElementById("cam-destino").value;
    let resp = await fetch("/api/camino?origen=" + origen + "&destino=" + destino);
    let res = await resp.json();
    let div = document.getElementById("res-camino");
    if (!res.ok) {
        rutaNodos = [];
        dibujarGrafo();
        div.textContent = res.mensaje;
        return;
    }
    rutaNodos = res.datos.nodos_ids;
    dibujarGrafo();
    let html = "<p><b>Saltos:</b> " + res.datos.saltos + "</p><ul>";
    for (let i = 0; i < res.datos.pasos.length; i++) {
        let p = res.datos.pasos[i];
        html += "<li>Paso " + p.numero + ": " + p.desde_nombre + " -- " + p.relacion + " --> " + p.hacia_nombre + "</li>";
    }
    div.innerHTML = html + "</ul>";
}

// Funcion auxiliar para enviar formularios CRUD en JSON
async function enviarJson(url, metodo, datos) {
    let resp = await fetch(url, {
        method: metodo,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    });
    let res = await resp.json();
    mostrarMensaje(res.mensaje, !res.ok);
    if (res.ok) cargarGrafo();
}

function crearEstudiante(e) {
    e.preventDefault();
    enviarJson("/api/estudiantes", "POST", {
        matricula: document.getElementById("est-mat").value,
        nombre: document.getElementById("est-nom").value,
        carrera: document.getElementById("est-car").value,
        semestre: document.getElementById("est-sem").value
    });
}

function crearMateria(e) {
    e.preventDefault();
    enviarJson("/api/materias", "POST", {
        codigo: document.getElementById("mat-cod").value,
        nombre: document.getElementById("mat-nom").value,
        area: document.getElementById("mat-area").value
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

function eliminarEst(e) {
    e.preventDefault();
    let mat = document.getElementById("del-est-mat").value;
    if (!confirm("Eliminar al estudiante " + mat + "?")) return;
    rutaNodos = [];
    enviarJson("/api/estudiantes/" + mat, "DELETE", {});
}

window.onload = cargarGrafo;
