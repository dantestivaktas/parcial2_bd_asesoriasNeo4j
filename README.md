# Sistema Web de Asesorias Academicas TI con Neo4j AuraDB

## Datos del Alumno
- **Nombre:** Dante Stivaktas (00548126)
- **Materia:** Bases de Datos Avanzadas
- **Proyecto:** Parcial 2 - Aplicacion Web en Python (Flask) conectada a Neo4j AuraDB

## Descripcion
Aplicacion web desarrollada con Python (Flask), HTML, CSS y JavaScript conectada a una base de datos orientada a grafos en la nube con **Neo4j AuraDB**. El sistema modela una red academica con nodos `:Estudiante` y `:Materia` conectados por las relaciones `:CURSO` y `:COLABORO_CON`, permitiendo realizar operaciones CRUD completas, recomendar asesores con calificacion de 9 o 10 y calcular la ruta de conexion mas corta entre dos estudiantes con `shortestPath`.

## 1. Instalacion de Dependencias
En la carpeta del proyecto, instalar las librerias de `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 2. Configuracion del Archivo `.env`
Crear un archivo `.env` en la raiz del proyecto tomando como guia `.env.example`:

```env
NEO4J_URI=neo4j+s://tu_instancia.databases.neo4j.io
NEO4J_USERNAME=tu_usuario
NEO4J_PASSWORD=tu_password
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=tu_instance_id
AURA_INSTANCENAME=Free instance
```

El archivo `.env` esta incluido en `.gitignore` para no subir credenciales al repositorio.

## 3. Poblar Datos Iniciales en Neo4j AuraDB
Ejecutar `seed.py` para limpiar la base, crear las restricciones `UNIQUE` sobre `Estudiante.matricula` y `Materia.codigo`, y cargar los 6 estudiantes, 4 materias y relaciones iniciales:

```bash
python seed.py
```

## 4. Ejecutar la Aplicacion Web
Iniciar el servidor Flask:

```bash
python app.py
```

Abrir en el navegador: **`http://127.0.0.1:5000`**

## Estructura del Proyecto
- `app.py`: Servidor web Flask con las rutas de la interfaz y endpoints REST (`/api/datos`, `/api/estudiantes`, `/api/materias`, `/api/cursos`, `/api/colaboraciones`, `/api/asesores`, `/api/camino`, `/api/seed`).
- `operaciones.py`: Funciones con las consultas Cypher parametrizadas para el CRUD y las dos consultas especializadas de grafos.
- `conexion.py`: Lectura de variables de entorno desde `.env` y conexion a Neo4j AuraDB con el driver oficial (`neo4j+s://`).
- `seed.py`: Script para crear restricciones de unicidad y cargar los datos iniciales de prueba.
- `templates/index.html`: Interfaz web organizada en tablas y tarjetas para visualizar nodos, relaciones, consultas y formularios CRUD.
- `static/estilos.css`: Estilos de la interfaz web.
- `static/app.js`: Funciones JavaScript que consumen la API de Flask con `fetch()`.
- `requirements.txt`: Dependencias del proyecto (`flask`, `neo4j`, `python-dotenv`).
- `.env.example` y `.gitignore`: Plantilla de variables de entorno y exclusion de archivos privados.
