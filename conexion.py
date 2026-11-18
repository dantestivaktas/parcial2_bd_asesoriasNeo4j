import os
import time
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Cargar variables del archivo .env y certificados para Windows
load_dotenv()
try:
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
except ImportError:
    pass


# Regresar el nombre de la base configurada en .env
def obtener_nombre_bd():
    return os.getenv("NEO4J_DATABASE") or "neo4j"


# Conectar con Neo4j AuraDB con reintentos simples por si falla la red
def conectar_bd():
    uri = os.getenv("NEO4J_URI")
    usuario = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not usuario or not password:
        print("Faltan datos en el archivo .env.")
        return None

    for i in range(3):
        driver = None
        try:
            driver = GraphDatabase.driver(uri, auth=(usuario, password))
            driver.verify_connectivity()
            with driver.session(database=obtener_nombre_bd()) as sesion:
                sesion.run("RETURN 1").consume()
            print("Conectado a Neo4j AuraDB correctamente.")
            return driver
        except Exception as error:
            if driver is not None:
                driver.close()
            if i == 2:
                print("No se pudo conectar a Neo4j AuraDB:", error)
            time.sleep(0.5)

    return None


# Cerrar la conexion del driver
def cerrar_bd(driver):
    if driver is not None:
        driver.close()
        print("Conexion cerrada.")
