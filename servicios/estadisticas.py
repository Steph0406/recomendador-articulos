"""Consultas de apoyo para el tablero: conteos generales y subgrafo de un usuario."""
from db.conexion import ConexionNeo4j as db


def conteos():
    """Total de nodos por etiqueta y total de relaciones."""
    return db.leer(
        """
        OPTIONAL MATCH (u:Usuario)  WITH count(u) AS usuarios
        OPTIONAL MATCH (a:Articulo) WITH usuarios, count(a) AS articulos
        OPTIONAL MATCH (j:Juego)    WITH usuarios, articulos, count(j) AS juegos
        OPTIONAL MATCH ()-[r]->()
        RETURN usuarios, articulos, juegos, count(r) AS relaciones
        """
    )[0]


def subgrafo_usuario(id_usuario):
    """Vecindad directa (1 salto) del usuario: todo lo que sale de él y quién lo sigue."""
    return db.leer(
        """
        MATCH (u:Usuario {id: $id})-[r]->(m)
        RETURN u.nombre AS desde, 'Usuario' AS tipo_desde, type(r) AS rel,
               coalesce(m.nombre, m.titulo) AS hacia, labels(m)[0] AS tipo_hacia
        UNION
        MATCH (m:Usuario)-[r:SIGUE]->(u:Usuario {id: $id})
        RETURN m.nombre AS desde, 'Usuario' AS tipo_desde, type(r) AS rel,
               u.nombre AS hacia, 'Usuario' AS tipo_hacia
        """,
        id=id_usuario,
    )
