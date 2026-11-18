# Sistema de Analisis de Conexiones y Asesorias Academicas TI

## Datos del Proyecto
- Alumno: Dante Stivaktas (ID: 00548126)
- Correo: dante_stivaktas@anahuac.mx
- Materia: Bases de Datos Avanzadas
- Proyecto: Parcial 2 - Integracion de Aplicacion Python y Frontend Web con Neo4j AuraDB

## Descripcion General
Aplicacion web (Flask + HTML/CSS/JavaScript) y de consola en Python conectada a una instancia administrada en la nube de Neo4j AuraDB (modelo de grafos). Permite administrar estudiantes, materias, cursos aprobados por periodo y colaboraciones en proyectos academicos, garantizando unicidad mediante restricciones (`CREATE CONSTRAINT`) en Neo4j, visualizando el grafo en vivo en el navegador y ejecutando consultas de vecindad para recomendar asesores y busqueda de caminos mas cortos (`shortestPath`).

## Requisitos Previos
- Python 3.10 o superior instalado en el sistema.
- Conexion a internet para comunicarse con Neo4j AuraDB mediante protocolo `neo4j+s://`.
- Credenciales activas de la instancia en Neo4j AuraDB.

## Instalacion de Dependencias
1. Abrir una terminal en la carpeta raiz del proyecto.
2. Instalar las librerias indicadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuracion del Archivo `.env`
1. Tomar como referencia el archivo `.env.example` incluido en el repositorio.
2. Crear un archivo `.env` en la raiz del proyecto con las credenciales reales de tu instancia AuraDB:

```env
NEO4J_URI=neo4j+s://tu_instancia.databases.neo4j.io
NEO4J_USERNAME=tu_usuario
NEO4J_PASSWORD=tu_password
NEO4J_DATABASE=tu_base
AURA_INSTANCEID=tu_instance_id
AURA_INSTANCENAME=Free instance
```

El archivo `.env` esta incluido en `.gitignore` para evitar subir credenciales o identificadores de infraestructura al repositorio.

## Ejecucion del Proyecto
1. Cargar o reiniciar los datos iniciales y restricciones de unicidad en la nube:

```bash
python seed.py
```

2. Iniciar la aplicacion web con frontend en el navegador:

```bash
python app.py
```

Luego abrir en el navegador `http://127.0.0.1:5000`.

3. De forma alternativa, tambien se puede ejecutar la interfaz clasica de consola:

```bash
python main.py
```

## Estructura Modular de Archivos
- `app.py`: Servidor web Flask que sirve la interfaz HTML y expone los endpoints REST (`/api/grafo`, `/api/estudiantes`, `/api/materias`, `/api/cursos`, `/api/colaboraciones`, `/api/asesores`, `/api/camino`, `/api/seed`).
- `templates/index.html`: Interfaz web principal con visualizador SVG del grafo en vivo, tablas de catalogo, historial por estudiante, formularios CRUD y consultas especializadas.
- `static/estilos.css`: Hoja de estilos limpia de la interfaz web.
- `static/app.js`: Logica del frontend en JavaScript para consumir la API, renderizar el grafo y resaltar rutas `shortestPath`.
- `conexion.py`: Carga las variables de entorno desde `.env`, inicializa el driver oficial de Neo4j, verifica la conectividad y cierra la sesion de forma segura.
- `seed.py`: Script de carga inicial que limpia la base, define restricciones `UNIQUE` sobre `Estudiante.matricula` y `Materia.codigo`, e inserta los 6 estudiantes, 4 materias, relaciones `:CURSO` y relaciones `:COLABORO_CON` mediante consultas Cypher parametrizadas.
- `operaciones.py`: Capa compartida de acceso a Neo4j con las operaciones CRUD completas (sin sobrescribir cursos de periodos anteriores ni colaboraciones de proyectos distintos) y las dos consultas especializadas de grafos.
- `main.py`: Interfaz de consola alternativa con menu numerado para ejecutar cada operacion contra Neo4j AuraDB.
- `requirements.txt`: Lista de dependencias del proyecto (`neo4j`, `python-dotenv` y `flask`).
- `.env.example`: Plantilla segura de configuracion de variables de entorno.
- `.gitignore`: Reglas para excluir archivos sensibles y temporales del control de versiones.
