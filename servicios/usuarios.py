"""CRUD de nodos :Usuario y sus relaciones SIGUE y LE_GUSTA."""
from db.conexion import ConexionNeo4j as db


def _uno(resultado):
    """Devuelve el primer registro o None si no hubo resultados."""
    return resultado[0] if resultado else None


# ------------------------------------------------------------ CREATE ---
def crear_usuario(id_usuario, nombre, pais):
    """Crea un usuario. Lanza ConstraintError si el id ya existe."""
    return _uno(db.escribir(
        """
        CREATE (u:Usuario {id: $id, nombre: $nombre, pais: $pais})
        RETURN u.id AS id, u.nombre AS nombre, u.pais AS pais
        """,
        id=id_usuario, nombre=nombre, pais=pais,
    ))


# -------------------------------------------------------------- READ ---
def listar_usuarios():
    return db.leer(
        """
        MATCH (u:Usuario)
        RETURN u.id AS id, u.nombre AS nombre, u.pais AS pais
        ORDER BY u.id
        """
    )


def obtener_usuario(id_usuario):
    """Datos del usuario + conteos calculados recorriendo sus relaciones."""
    return _uno(db.leer(
        """
        MATCH (u:Usuario {id: $id})
        RETURN u.id AS id, u.nombre AS nombre, u.pais AS pais,
               COUNT { (u)-[:SIGUE]->() }    AS siguiendo,
               COUNT { ()-[:SIGUE]->(u) }    AS seguidores,
               COUNT { (u)-[:ESCRIBIO]->() } AS escritos,
               COUNT { (u)-[:LEYO]->() }     AS leidos
        """,
        id=id_usuario,
    ))


# ------------------------------------------------------------ UPDATE ---
def actualizar_usuario(id_usuario, nombre, pais):
    return _uno(db.escribir(
        """
        MATCH (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.pais = $pais
        RETURN u.id AS id, u.nombre AS nombre, u.pais AS pais
        """,
        id=id_usuario, nombre=nombre, pais=pais,
    ))


# ------------------------------------------------------------ DELETE ---
def eliminar_usuario(id_usuario):
    """Elimina al usuario, sus relaciones y en cascada los artículos que escribió."""
    return _uno(db.escribir(
        """
        MATCH (u:Usuario {id: $id})
        OPTIONAL MATCH (u)-[:ESCRIBIO]->(a:Articulo)
        WITH u, collect(a) AS articulos
        FOREACH (art IN articulos | DETACH DELETE art)
        DETACH DELETE u
        RETURN size(articulos) AS articulos_borrados
        """,
        id=id_usuario,
    ))


# -------------------------------------------------------- RELACIONES ---
def seguir(seguidor_id, seguido_id):
    """MERGE evita duplicar la relación si ya existía."""
    return _uno(db.escribir(
        """
        MATCH (a:Usuario {id: $seguidor}), (b:Usuario {id: $seguido})
        WHERE a <> b
        MERGE (a)-[r:SIGUE]->(b)
        ON CREATE SET r.desde = date()
        RETURN a.nombre AS seguidor, b.nombre AS seguido
        """,
        seguidor=seguidor_id, seguido=seguido_id,
    ))


def dejar_de_seguir(seguidor_id, seguido_id):
    return _uno(db.escribir(
        """
        MATCH (:Usuario {id: $seguidor})-[r:SIGUE]->(b:Usuario {id: $seguido})
        WITH r, b.nombre AS seguido
        DELETE r
        RETURN seguido
        """,
        seguidor=seguidor_id, seguido=seguido_id,
    ))


def me_gusta(id_usuario, nombre_juego):
    return _uno(db.escribir(
        """
        MATCH (u:Usuario {id: $id}), (j:Juego {nombre: $juego})
        MERGE (u)-[:LE_GUSTA]->(j)
        RETURN u.nombre AS usuario, j.nombre AS juego
        """,
        id=id_usuario, juego=nombre_juego,
    ))
