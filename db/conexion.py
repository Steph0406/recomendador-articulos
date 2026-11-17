"""
Módulo de conexión a Neo4j AuraDB.

Centraliza la creación del driver oficial de Neo4j (patrón Singleton):
se crea UNA sola instancia del driver para toda la aplicación, porque
el driver administra internamente un pool de conexiones y es costoso
crearlo varias veces.
"""
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase, RoutingControl

load_dotenv()  # Lee las credenciales del archivo .env


class ConexionNeo4j:
    """Administra el driver de Neo4j y ejecuta consultas Cypher."""

    _driver = None

    @classmethod
    def obtener_driver(cls):
        """Crea el driver la primera vez y lo reutiliza después."""
        if cls._driver is None:
            uri = os.getenv("NEO4J_URI")
            usuario = os.getenv("NEO4J_USERNAME")
            password = os.getenv("NEO4J_PASSWORD")

            if not all([uri, usuario, password]):
                raise RuntimeError("Faltan variables en el archivo .env")

            cls._driver = GraphDatabase.driver(uri, auth=(usuario, password))
            cls._driver.verify_connectivity()
        return cls._driver

    @classmethod
    def escribir(cls, consulta, **parametros):
        """Ejecuta una consulta de escritura (CREATE, MERGE, SET, DELETE)."""
        registros, _, _ = cls.obtener_driver().execute_query(
            consulta,
            parameters_=parametros,
            routing_=RoutingControl.WRITE,
        )
        return [r.data() for r in registros]

    @classmethod
    def leer(cls, consulta, **parametros):
        """Ejecuta una consulta de solo lectura (MATCH ... RETURN)."""
        registros, _, _ = cls.obtener_driver().execute_query(
            consulta,
            parameters_=parametros,
            routing_=RoutingControl.READ,
        )
        return [r.data() for r in registros]

    @classmethod
    def cerrar(cls):
        """Cierra el driver y libera las conexiones."""
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None


if __name__ == "__main__":
    # Prueba rápida: cuenta cuántos nodos hay en la base
    resultado = ConexionNeo4j.leer("MATCH (n) RETURN count(n) AS total")
    print("✅ Conexión OK. Nodos en la base:", resultado[0]["total"])
    ConexionNeo4j.cerrar()
